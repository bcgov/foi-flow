import React from "react";

const ApplicantProfileModalActions = ({
  requestDetails,
  reassignProfileToRequest,
  isSaveDisabled,
  confirmationMessage,
  setConfirmationMessage,
  back,
  cancel,
  updateProfile,
  isBeforeOpen,
  createConfirmation,
  selectedApplicant,
  applicantHistory,
  isChangeToDifferentProfile,
  createProfile,
  applicantProfileError,
}) => {
  const Button = ({ children, onClick, disabled, variant = "save" }) => (
    <button
      className={`btn-bottom btn-${variant} btn`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );

  const Buttons = {
    reassignProfile: <Button onClick={reassignProfileToRequest} disabled={isSaveDisabled()}>Reassign Profile</Button>,
    selectProfile: <Button onClick={reassignProfileToRequest} disabled={isSaveDisabled()}>Select Profile</Button>,
    confirmReassignProfile: <Button onClick={reassignProfileToRequest}>Confirm Reassign Profile</Button>,
    confirmSelectedProfile: <Button onClick={reassignProfileToRequest}>Confirm Reassigned Profile</Button>,
    back: <Button onClick={back} variant="cancel">Back</Button>,
    confirmBack: <Button onClick={() => setConfirmationMessage(false)} variant="cancel">Back</Button>,
    updateProfile: <Button onClick={updateProfile} disabled={isSaveDisabled() || applicantProfileError}>Update Profile</Button>,
    confirmUpdateProfile: <Button onClick={updateProfile} disabled={isSaveDisabled() || applicantProfileError}>Save Changes</Button>,
    createNewProfile: <Button onClick={createProfile}>Create New Profile</Button>,
    confirmCreateNewProfile: <Button onClick={createProfile} disabled={applicantProfileError}>Confirm New Profile</Button>,
    cancel: <Button onClick={cancel} variant="cancel">Cancel</Button>,
  };

  const beforeOpen = isBeforeOpen(requestDetails);
  const hasAssignedApplicant = !!requestDetails?.foiRequestApplicantID;

  const stateMachine = {
    NO_APPLICANT: [Buttons.createNewProfile, Buttons.cancel],
    CREATE_CONFIRM: [Buttons.confirmCreateNewProfile, Buttons.back],
    CHANGE_CONFIRM: [Buttons.confirmSelectedProfile, Buttons.back],
    CHANGE: [!applicantHistory && Buttons.reassignProfile, Buttons.back],
    UPDATE_CONFIRM: [Buttons.confirmUpdateProfile, Buttons.confirmBack],
    SELECT_PROFILE: [!applicantHistory && Buttons.selectProfile, Buttons.back],
    UPDATE_BEFORE_OPEN: [!applicantHistory && Buttons.updateProfile, Buttons.createNewProfile, Buttons.cancel],
    DEFAULT: [
      !applicantHistory && Buttons.createNewProfile,
      !applicantHistory && Buttons.updateProfile,
      Buttons.cancel,
    ],
  };

  const uiState = (() => {
    if (createConfirmation) return "CREATE_CONFIRM";
    if (!selectedApplicant) return "NO_APPLICANT";
    if (isChangeToDifferentProfile && confirmationMessage) return "CHANGE_CONFIRM";
    if (isChangeToDifferentProfile) return "CHANGE";
    if (confirmationMessage) return "UPDATE_CONFIRM";
    if (beforeOpen && !hasAssignedApplicant) return "SELECT_PROFILE";
    if (beforeOpen && hasAssignedApplicant) return "UPDATE_BEFORE_OPEN";
    return "DEFAULT";
  })();

  return (
  <>
    {stateMachine[uiState].filter(Boolean).map((btn, idx) => (
      <React.Fragment key={idx}>{btn}</React.Fragment>
    ))}
  </>
);  
}

export default ApplicantProfileModalActions;
