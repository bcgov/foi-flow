using System.Linq.Expressions;

namespace MCS.FOI.Integration.Core.Repositories.Base
{
    public interface IEFRepository<TEntity> where TEntity : class
    {
        Task AddAsync(TEntity entity);
        Task AddRangeAsync(IEnumerable<TEntity> entities, CancellationToken cancellationToken = default);
        Task<IEnumerable<TEntity>> GetAsync(
            Expression<Func<TEntity, bool>> filter = null,
            Func<IQueryable<TEntity>, IOrderedQueryable<TEntity>> orderBy = null,
            CancellationToken cancellationToken = default,
            params Expression<Func<TEntity, object>>[] includes);
        Task BulkInsertOrUpdateAsync(IEnumerable<TEntity> entities);
        Task DeleteAsync(TEntity entity);
        Task DeleteRangeAsync(IEnumerable<TEntity> entities);
        Task UpdateAsync(TEntity entityToUpdate);
        Task UpdateRangeAsync(IEnumerable<TEntity> entitiesToUpdate);
        Task<IEnumerable<TEntity>> GetAllAsync();
        Task SaveChangesAsync();
    }
}
