import ApplicantDetails from "../ApplicantDetails"
import AddressContactDetails from "../AddressContanctInfo"
import AdditionalApplicantDetails from "../AdditionalApplicantDetails"

const ApplicantDetailsSections = ({
    requestDetails,
    contactDetailsNotGiven,
    createSaveRequestObject,
    handleApplicantDetailsInitialValue,
    handleApplicantDetailsValue,
    disableInput,
    defaultExpanded,
    showHistory,
    warning,
    displayOtherNotes,
    isAddRequest,
    isUnopenedRequest,
    requestType = "general",
    disableAdditionalDetails = requestType == "general" ? true : false
}) => {
    return (
        <>
            <ApplicantDetails
                requestDetails={requestDetails}
                contactDetailsNotGiven={contactDetailsNotGiven}
                createSaveRequestObject={createSaveRequestObject}
                handleApplicantDetailsInitialValue={handleApplicantDetailsInitialValue}
                handleApplicantDetailsValue={handleApplicantDetailsValue}
                disableInput={disableInput}
                defaultExpanded={true}
                showHistory={showHistory}
                warning={warning}
                displayOtherNotes={displayOtherNotes}
            />
            <AddressContactDetails
                requestDetails={requestDetails}
                contactDetailsNotGiven={contactDetailsNotGiven}
                createSaveRequestObject={createSaveRequestObject}
                handleContactDetailsInitialValue={handleApplicantDetailsInitialValue}
                handleContanctDetailsValue={handleApplicantDetailsValue}
                handleEmailValidation={() => {}}
                disableInput={disableInput}
                defaultExpanded={defaultExpanded}
                warning={warning}
            />
            <AdditionalApplicantDetails
                requestDetails={requestDetails}
                createSaveRequestObject={createSaveRequestObject}
                disableInput={disableInput || disableAdditionalDetails}
                defaultExpanded={defaultExpanded}
                warning={requestType != "general" || isAddRequest || isUnopenedRequest ? warning : null}
                setError={() => {}} //!!!!
            />
        </>
    )
}

export default ApplicantDetailsSections