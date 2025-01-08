export enum OIStates {
    FirstReview = 1,
    PeerReview,
    ReadyToPublish,
    Published,
    HoldPublication,
    Unpublished,
    DoNotPublish,
    ExemptionRequest,
}

export enum OIPublicationStatuses {
    DoNotPublish = 1,
    Publish,
    UnpublishRequest,
}

export enum OIExemptions {
    AnotherGovernmentsInformation = 1,
    BusinessInformation,
    FederalCopyright,
    FirstNationsInformation,
    OutsideScopeOfPublication,
    PersonalInformation,
    PublicBodyDecision,
    SecurityInformation
}