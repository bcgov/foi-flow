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
  isUnassignProfile,
  createProfile,
}) => {
  // Buttons
  const reassignProfileButton = (
    <button
      className={`btn-bottom btn-save btn`}
      onClick={reassignProfileToRequest}
      disabled={isSaveDisabled()}
    >
      Reassign Profile
    </button>
  );
  const selectProfileButton = (
    <button
      className={`btn-bottom btn-save btn`}
      onClick={reassignProfileToRequest}
      disabled={isSaveDisabled()}
    >
      Select Profile
    </button>
  );

  const confirmReassignProfileButton = (
    <button
      className={`btn-bottom btn-save btn`}
      onClick={reassignProfileToRequest}
    >
      Confirm Reassign Profile
    </button>
  );

  const confirmSelectedProfileButton = (
    <button
      className={`btn-bottom btn-save btn`}
      onClick={reassignProfileToRequest}
    >
      Confirm Reassigned Profile
    </button>
  );

  const confirmBackButton = (
    <button
      className="btn-bottom btn-cancel"
      onClick={() => setConfirmationMessage(false)}
    >
      Back
    </button>
  );

  const backButton = (
    <button className="btn-bottom btn-cancel" onClick={back}>
      Back
    </button>
  );

  const updateProfileButton = (
    <button
      className={`btn-bottom btn-save btn`}
      onClick={updateProfile}
      disabled={isSaveDisabled()}
    >
      Update Profile
    </button>
  );

//   const unassignProfileButton = (
//       <button className={`btn-bottom btn-save btn`} onClick={unassignProfileFromRequest}>
//       Unassign Profile
//       </button>
//   );

  const confirmUpdateProfileButton = (
    <button className={`btn-bottom btn-save btn`} onClick={updateProfile}>
      Save Changes
    </button>
  );

  const createNewProfileButton = (
    <button className={`btn-bottom btn-save btn`} onClick={createProfile}>
      Create New Profile
    </button>
  );

  const confirmCreateNewProfileButton = (
    <button className={`btn-bottom btn-save btn`} onClick={createProfile}>
      Confirm New Profile
    </button>
  );

  const cancelButton = (
    <button className="btn-bottom btn-cancel" onClick={cancel}>
      Cancel
    </button>
  );

  // Rendering logic
  if (isBeforeOpen(requestDetails)) {
    const hasAssignedApplicant = requestDetails?.foiRequestApplicantID
      ? true
      : false;
    if (createConfirmation) {
      return (
        <>
          {confirmCreateNewProfileButton}
          {backButton}
        </>
      );
    }

    if (
      (selectedApplicant && !hasAssignedApplicant) ||
      isChangeToDifferentProfile
    ) {
      return (
        <>
          {!applicantHistory && <>{selectProfileButton}</>}
          {backButton}
        </>
      );
    }

    if (selectedApplicant && hasAssignedApplicant) {
      return (
        <>
          {!applicantHistory && (
            <>
              {createNewProfileButton}
              {/* {selectProfileButton} */}
              {updateProfileButton}
            </>
          )}
          {backButton}
        </>
      );
    }

    if (!selectedApplicant) {
      return (
        <>
          {createNewProfileButton}
          {backButton}
        </>
      );
    }
  }
//   return;
  if (isUnassignProfile && confirmationMessage) {
    return (
      <>
        {/* {unassignProfileButton} */}
        {backButton}
      </>
    );
  }
  if (createConfirmation && isBeforeOpen(requestDetails)) {
    return <>{backButton}</>;
  }

  if (isChangeToDifferentProfile && !confirmationMessage)
    return (
      <>
        {!applicantHistory && selectProfileButton}
        {backButton}
      </>
    );
  if (isChangeToDifferentProfile && confirmationMessage)
    return (
      <>
        {confirmSelectedProfileButton}
        {backButton}
      </>
    );

  if (isChangeToDifferentProfile) {
    if (confirmationMessage) {
      return (
        <>
          {confirmReassignProfileButton}
          {confirmBackButton}
        </>
      );
    } else {
      return (
        <>
          {!applicantHistory && reassignProfileButton}
          {backButton}
        </>
      );
    }
  }

  if (selectedApplicant) {
    if (confirmationMessage) {
      return (
        <>
          {confirmUpdateProfileButton}
          {confirmBackButton}
        </>
      );
    } else if (createConfirmation) {
      return (
        <>
          {!applicantHistory && <>{confirmCreateNewProfileButton}</>}
          {backButton}
        </>
      );
    } else {
      if (isBeforeOpen(requestDetails)) {
        return (
          <>
            {!applicantHistory && (
              <>
                {updateProfileButton}
                {/* {unassignProfileButton} */}
              </>
            )}
            {backButton}
          </>
        );
      }
      return (
        <>
          {!applicantHistory && (
            <>
              {createNewProfileButton}
              {updateProfileButton}
            </>
          )}
          {backButton}
        </>
      );
    }
  }
  return (
    <>
      {createNewProfileButton}
      {cancelButton}
    </>
  );
};

export default ApplicantProfileModalActions;
