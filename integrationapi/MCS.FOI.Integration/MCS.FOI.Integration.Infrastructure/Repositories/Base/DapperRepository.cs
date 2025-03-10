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
    }
}
