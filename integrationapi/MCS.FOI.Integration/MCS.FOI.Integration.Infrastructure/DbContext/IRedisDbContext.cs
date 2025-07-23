namespace MCS.FOI.Integration.Infrastructure.Data
{
    public interface IRedisDbContext
    {
        IDatabase Redis { get; }
        bool IsConnected { get; }
    }
}
