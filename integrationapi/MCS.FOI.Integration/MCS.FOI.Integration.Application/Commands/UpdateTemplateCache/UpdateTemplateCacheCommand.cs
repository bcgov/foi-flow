namespace MCS.FOI.Integration.Application.Commands.UpdateRedisTemplate
{
    public class UpdateTemplateCacheCommand: ICommand<bool>
    {
        public string Token { get; set; } = string.Empty;
    }
}
