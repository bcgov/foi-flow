namespace MCS.FOI.Integration.Application.Exceptions
{
    public class NotValidOperationException : Exception
    {
        public NotValidOperationException(string message) : base(message)
        {
        }

        public NotValidOperationException(string message, string details) : base(message)
        {
            Details = details;
        }

        public string? Details { get; }
    }
}
