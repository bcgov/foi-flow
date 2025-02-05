namespace MCS.FOI.Integration.Infrastructure.Repositories.Base
{
    public class EFRepository<TEntity> : IEFRepository<TEntity> where TEntity : class
    {
        protected readonly IntegrationDbContext _dbContext;
        protected readonly DbSet<TEntity> _dbSet;

        public EFRepository(IntegrationDbContext dbContext)
        {
            _dbContext = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
            _dbSet = _dbContext.Set<TEntity>();
        }

        /// <summary>
        /// Adds a single entity asynchronously.
        /// </summary>
        public virtual async Task AddAsync(TEntity entity)
        {
            if (entity == null) throw new ArgumentNullException(nameof(entity));
            await _dbSet.AddAsync(entity);
        }

        /// <summary>
        /// Adds a collection of entities asynchronously.
        /// </summary>
        public async Task AddRangeAsync(IEnumerable<TEntity> entities, CancellationToken cancellationToken = default)
        {
            if (entities == null) throw new ArgumentNullException(nameof(entities));
            await _dbSet.AddRangeAsync(entities, cancellationToken);
        }

        /// <summary>
        /// Retrieves entities based on a filter, sorting, and includes.
        /// </summary>
        public async Task<IEnumerable<TEntity>> GetAsync(
            Expression<Func<TEntity, bool>> filter = null,
            Func<IQueryable<TEntity>, IOrderedQueryable<TEntity>> orderBy = null,
            CancellationToken cancellationToken = default,
            params Expression<Func<TEntity, object>>[] includes)
        {
            IQueryable<TEntity> query = _dbSet;

            if (filter != null)
                query = query.Where(filter);

            if (includes != null)
            {
                foreach (var include in includes)
                    query = query.Include(include);
            }

            return orderBy != null
                ? await orderBy(query).ToListAsync(cancellationToken)
                : await query.ToListAsync(cancellationToken);
        }

        /// <summary>
        /// Performs bulk insert or update of entities.
        /// </summary>
        public async Task BulkInsertOrUpdateAsync(IEnumerable<TEntity> entities)
        {
            if (entities == null) throw new ArgumentNullException(nameof(entities));

            var bulkConfig = new BulkConfig
            {
                PreserveInsertOrder = true,
                SetOutputIdentity = true
            };

            await _dbContext.BulkInsertOrUpdateAsync(entities.ToList(), bulkConfig);
        }

        /// <summary>
        /// Deletes a single entity.
        /// </summary>
        public async Task DeleteAsync(TEntity entity)
        {
            if (entity == null) throw new ArgumentNullException(nameof(entity));
            _dbSet.Remove(entity);
        }

        /// <summary>
        /// Deletes a collection of entities.
        /// </summary>
        public async Task DeleteRangeAsync(IEnumerable<TEntity> entities)
        {
            if (entities == null) throw new ArgumentNullException(nameof(entities));
            _dbSet.RemoveRange(entities);
        }

        /// <summary>
        /// Updates a single entity.
        /// </summary>
        public virtual async Task UpdateAsync(TEntity entityToUpdate)
        {
            if (entityToUpdate == null) throw new ArgumentNullException(nameof(entityToUpdate));
            _dbSet.Attach(entityToUpdate);
            _dbContext.Entry(entityToUpdate).State = EntityState.Modified;
        }

        /// <summary>
        /// Updates a collection of entities.
        /// </summary>
        public async Task UpdateRangeAsync(IEnumerable<TEntity> entitiesToUpdate)
        {
            if (entitiesToUpdate == null) throw new ArgumentNullException(nameof(entitiesToUpdate));

            foreach (var entity in entitiesToUpdate)
            {
                _dbContext.Entry(entity).State = EntityState.Modified;
            }
        }
    }
}
