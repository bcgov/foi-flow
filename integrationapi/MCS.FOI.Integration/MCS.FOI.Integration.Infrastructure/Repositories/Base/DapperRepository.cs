namespace MCS.FOI.Integration.Infrastructure.Repositories.Base
{
    public class DapperRepository : IDapperRepository
    {
        private readonly IDbConnection _dbConnection;

        public DapperRepository(IntegrationDbContext dbContext)
        {
            if (dbContext == null) throw new ArgumentNullException(nameof(dbContext));
            _dbConnection = dbContext.Database.GetDbConnection();
        }

        public async Task<IEnumerable<T>> QueryAsync<T>(string query, object? parameters = null)
        {
            ValidateQuery(query);
            return await _dbConnection.QueryAsync<T>(query, parameters);
        }

        public async Task<T> QuerySingleAsync<T>(string query, object? parameters = null)
        {
            ValidateQuery(query);
            return await _dbConnection.QuerySingleOrDefaultAsync<T>(query, parameters);
        }

        public async Task<IEnumerable<dynamic>> QueryDynamicAsync(string query, object? parameters = null)
        {
            ValidateQuery(query);
            return await _dbConnection.QueryAsync(query, parameters);
        }

        private void ValidateQuery(string query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                throw new ArgumentException("Query cannot be null or empty.", nameof(query));
            }
        }

        public async Task UpdateAsync<T>(string updateQuery, IEnumerable<T> items)
        {
            if (string.IsNullOrWhiteSpace(updateQuery))
                throw new ArgumentException("Update query cannot be null or empty.", nameof(updateQuery));

            if (items == null || !items.Any())
                throw new ArgumentException("Items collection cannot be null or empty.", nameof(items));

            using var transaction = _dbConnection.BeginTransaction();
            try
            {
                foreach (var item in items)
                {
                    await _dbConnection.ExecuteAsync(updateQuery, item, transaction);
                }

                transaction.Commit();
            }
            catch
            {
                transaction.Rollback();
                throw;
            }
        }
    }
}
