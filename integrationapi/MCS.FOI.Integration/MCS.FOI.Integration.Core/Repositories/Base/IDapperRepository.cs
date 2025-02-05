namespace MCS.FOI.Integration.Core.Repositories.Base
{
    public interface IDapperRepository
    {
        Task<IEnumerable<T>> QueryAsync<T>(string query, object parameters = null);

        Task<T> QuerySingleAsync<T>(string query, object parameters = null);

        Task<int> ExecuteAsync(string query, object parameters = null);

        Task<T> ExecuteScalarAsync<T>(string query, object parameters = null);

        Task<IEnumerable<dynamic>> QueryDynamicAsync(string query, object parameters = null);
    }
}
