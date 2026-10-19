using System.Data;
using MCS.FOI.Integration.Infrastructure.Data;
using MCS.FOI.Integration.Infrastructure.Repositories.Base;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace MCS.FOI.Integration.Tests;

[TestClass]
public class DapperRepositoryConnectionTests
{
    private const string UpdateSql =
        @"UPDATE ""Template"" SET encodedcontent = @EncodedContent WHERE templateid = @TemplateId";

    [TestMethod]
    public async Task UpdateAsync_ClosedConnection_OpensCommitsAndCloses()
    {
        var database = await CreateDatabaseAsync();
        await using var keeper = database.Keeper;
        await using var context = database.Context;

        var connection = context.Database.GetDbConnection();

        Assert.AreEqual(ConnectionState.Closed, connection.State);

        var repository = new DapperRepository(context);

        await repository.UpdateAsync(UpdateSql, new[]
        {
            new { TemplateId = 105, EncodedContent = "refreshed-consult" }
        });

        Assert.AreEqual(ConnectionState.Closed, connection.State);
        Assert.AreEqual(
            "refreshed-consult",
            await GetContentAsync(keeper, 105));
    }

    [TestMethod]
    public async Task UpdateAsync_AlreadyOpenConnection_LeavesConnectionOpen()
    {
        var database = await CreateDatabaseAsync();
        await using var keeper = database.Keeper;
        await using var context = database.Context;

        await context.Database.OpenConnectionAsync();

        try
        {
            var connection = context.Database.GetDbConnection();
            Assert.AreEqual(ConnectionState.Open, connection.State);

            var repository = new DapperRepository(context);

            await repository.UpdateAsync(UpdateSql, new[]
            {
                new { TemplateId = 83, EncodedContent = "refreshed-personal" }
            });

            Assert.AreEqual(ConnectionState.Open, connection.State);
            Assert.AreEqual(
                "refreshed-personal",
                await GetContentAsync(keeper, 83));
        }
        finally
        {
            await context.Database.CloseConnectionAsync();
        }
    }

    [TestMethod]
    public async Task UpdateAsync_FailedSecondUpdate_RollsBackAndCloses()
    {
        var database = await CreateDatabaseAsync();
        await using var keeper = database.Keeper;
        await using var context = database.Context;

        var connection = context.Database.GetDbConnection();
        var repository = new DapperRepository(context);

        // The unique constraint causes the second UPDATE to fail.
        await Assert.ThrowsExceptionAsync<SqliteException>(
            () => repository.UpdateAsync(UpdateSql, new[]
            {
                new { TemplateId = 83, EncodedContent = "duplicate" },
                new { TemplateId = 105, EncodedContent = "duplicate" }
            }));

        Assert.AreEqual(ConnectionState.Closed, connection.State);

        // Neither update should survive the failed transaction.
        Assert.AreEqual("original-personal", await GetContentAsync(keeper, 83));
        Assert.AreEqual("original-consult", await GetContentAsync(keeper, 105));
    }

    private static async Task<(SqliteConnection Keeper, IntegrationDbContext Context)>
        CreateDatabaseAsync()
    {
        var name = "foimod5454_" + Guid.NewGuid().ToString("N");

        var connectionString = new SqliteConnectionStringBuilder
        {
            DataSource = name,
            Mode = SqliteOpenMode.Memory,
            Cache = SqliteCacheMode.Shared
        }.ToString();

        // Keep the shared in-memory database alive while the repository
        // opens and closes its separate connection.
        var keeper = new SqliteConnection(connectionString);
        await keeper.OpenAsync();

        try
        {
            using var command = keeper.CreateCommand();

            command.CommandText = @"
                CREATE TABLE ""Template"" (
                    templateid INTEGER PRIMARY KEY,
                    encodedcontent TEXT NOT NULL UNIQUE
                );

                INSERT INTO ""Template"" (templateid, encodedcontent)
                VALUES
                    (83, 'original-personal'),
                    (105, 'original-consult');
            ";

            await command.ExecuteNonQueryAsync();

            var options = new DbContextOptionsBuilder<IntegrationDbContext>()
                .UseSqlite(connectionString)
                .Options;

            return (keeper, new IntegrationDbContext(options));
        }
        catch
        {
            await keeper.DisposeAsync();
            throw;
        }
    }

    private static async Task<string> GetContentAsync(
        SqliteConnection keeper,
        int templateId)
    {
        using var command = keeper.CreateCommand();

        command.CommandText =
            @"SELECT encodedcontent FROM ""Template"" WHERE templateid = $id";

        command.Parameters.AddWithValue("$id", templateId);

        return Convert.ToString(await command.ExecuteScalarAsync())
            ?? string.Empty;
    }
}