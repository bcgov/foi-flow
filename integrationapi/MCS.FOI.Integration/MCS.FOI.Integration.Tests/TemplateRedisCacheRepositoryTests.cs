using MCS.FOI.Integration.Core.DTOs;
using MCS.FOI.Integration.Core.Repositories.Base;
using MCS.FOI.Integration.Infrastructure.Data;
using MCS.FOI.Integration.Infrastructure.Repositories.RedisRepository;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using StackExchange.Redis;

namespace MCS.FOI.Integration.Tests;

[TestClass]
public class TemplateRedisCacheRepositoryTests
{
    private static TemplateDto CreateTemplate() => new()
    {
        TemplateId = 105,
        FileName = "AConsultRequest",
        EncodedContent = "TkVX"
    };

    [TestMethod]
    public async Task DisconnectedRedis_ThrowsException()
    {
        var context = new Mock<IRedisDbContext>();

        context.SetupGet(x => x.IsConnected).Returns(false);

        var repository = new TemplateRedisCacheRepository(
            context.Object,
            Mock.Of<IRedisRepository<TemplateDto>>());

        await Assert.ThrowsExceptionAsync<InvalidOperationException>(
            () => repository.UpdateCacheTemplateAsync(
                new[] { CreateTemplate() }));
    }

    [TestMethod]
    public async Task UnsuccessfulRedisWrite_ThrowsException()
    {
        var (repository, batch) = CreateConnectedRepository(false);

        await Assert.ThrowsExceptionAsync<InvalidOperationException>(
            () => repository.UpdateCacheTemplateAsync(
                new[] { CreateTemplate() }));

        batch.Verify(x => x.StringSetAsync(
            It.Is<RedisKey>(key =>
                key.ToString() == "Template_AConsultRequest"),
            It.IsAny<RedisValue>(),
            It.IsAny<TimeSpan?>(),
            It.IsAny<bool>(),
            It.IsAny<When>(),
            It.IsAny<CommandFlags>()),
            Times.Once());
    }

    [TestMethod]
    public async Task SuccessfulRedisWrite_UsesExpectedKeyAndContent()
    {
        var (repository, batch) = CreateConnectedRepository(true);

        await repository.UpdateCacheTemplateAsync(
            new[] { CreateTemplate() });

        batch.Verify(x => x.StringSetAsync(
            It.Is<RedisKey>(key =>
                key.ToString() == "Template_AConsultRequest"),
            It.Is<RedisValue>(value =>
                value.ToString().Contains(
                    "\"EncodedContent\":\"TkVX\"")),
            It.IsAny<TimeSpan?>(),
            It.IsAny<bool>(),
            It.Is<When>(when => when == When.Always),
            It.IsAny<CommandFlags>()),
            Times.Once());
    }

    private static (
        TemplateRedisCacheRepository Repository,
        Mock<IBatch> Batch)
        CreateConnectedRepository(bool writeResult)
    {
        var batch = new Mock<IBatch>();

        batch.Setup(x => x.StringSetAsync(
            It.IsAny<RedisKey>(),
            It.IsAny<RedisValue>(),
            It.IsAny<TimeSpan?>(),
            It.IsAny<bool>(),
            It.IsAny<When>(),
            It.IsAny<CommandFlags>()))
            .ReturnsAsync(writeResult);

        var database = new Mock<IDatabase>();

        database.Setup(x => x.CreateBatch(
            It.IsAny<object?>()))
            .Returns(batch.Object);

        var context = new Mock<IRedisDbContext>();

        context.SetupGet(x => x.IsConnected).Returns(true);
        context.SetupGet(x => x.Redis).Returns(database.Object);

        var repository = new TemplateRedisCacheRepository(
            context.Object,
            Mock.Of<IRedisRepository<TemplateDto>>());

        return (repository, batch);
    }
}