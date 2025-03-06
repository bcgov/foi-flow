namespace MCS.FOI.Integration.Application.Commands.GetCorrespondence
{
    public class GetCorrespondenceCommand : ICommand<string>
    {
        public string Token { get; set; } = string.Empty;
        public int FOIRequestId { get; init; }
        public int FOIMinistryRequestId { get; init; }
        public string FileName { get; init; } = string.Empty;
    }

    public class GetCorrespondenceRequest
    {
        public int FOIRequestId { get; init; }
        public int FOIMinistryRequestId { get; init; }
        public string FileName { get; init; } = string.Empty;
    }

    public class GetCorrespondenceResponse
    {
        public string Code { get; set; } = default!;
        public string FileName { get; set; } = default!;
        public string Extension { get; set; } = default!;
        public bool IsActive { get; set; }
    }

    public class GetCorrespondenceCommandValidator: AbstractValidator<GetCorrespondenceCommand>
    {
        public GetCorrespondenceCommandValidator()
        {
            RuleFor(a => a.FOIRequestId).NotNull().NotEmpty().WithMessage($"{nameof(GetCorrespondenceCommand.FOIRequestId)} is required.");
            RuleFor(a => a.FOIMinistryRequestId).NotNull().NotEmpty().WithMessage($"{nameof(GetCorrespondenceCommand.FOIMinistryRequestId)} is required.");
            RuleFor(a => a.FileName).NotNull().NotEmpty().WithMessage($"{nameof(GetCorrespondenceCommand.FileName)} is required.");
            RuleFor(a => a.Token).NotNull().NotEmpty().WithMessage($"{nameof(GetCorrespondenceCommand.Token)} is required.");
        }
    }
}