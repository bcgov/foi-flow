namespace MCS.FOI.Integration.Core.Entities.Base
{
    public abstract class EntityBase<TId> : IEntityBase<TId>
    {
        private int? _requestedHashCode;

        public TId Id { get; protected set; }

        public bool IsTransient() => Id.Equals(default(TId));

        public override bool Equals(object? obj)
        {
            if (obj is not EntityBase<TId> otherEntity)
                return false;

            if (ReferenceEquals(this, obj))
                return true;

            if (GetType() != obj.GetType())
                return false;

            return !IsTransient() && !otherEntity.IsTransient() && Id.Equals(otherEntity.Id);
        }

        public override int GetHashCode()
        {
            if (IsTransient())
                return base.GetHashCode();

            if (!_requestedHashCode.HasValue)
                _requestedHashCode = Id.GetHashCode() ^ 31;

            return _requestedHashCode.Value;
        }

        public static bool operator ==(EntityBase<TId> left, EntityBase<TId> right)
        {
            return Equals(left, right);
        }

        public static bool operator !=(EntityBase<TId> left, EntityBase<TId> right)
        {
            return !Equals(left, right);
        }
    }
}
