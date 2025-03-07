namespace MCS.FOI.Integration.Core.Entities.Base
{
    public abstract class EntityBase<TId> : IEntityBase<TId>
    {
        public TId Id { get; protected set; }
    }
}
