namespace MCS.FOI.Integration.Application.Interface
{
    public interface ICommand : ICommand<Unit>{}
    public interface ICommand<out TResponse> : IRequest<TResponse>{}
}
