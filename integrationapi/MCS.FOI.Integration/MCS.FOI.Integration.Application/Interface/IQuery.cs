namespace MCS.FOI.Integration.Application.Interface
{
    public interface IQuery<out TResponse> : IRequest<TResponse> where TResponse : notnull {}
}
