import React, { useState, memo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import ReactModal from "react-modal-resizable-draggable";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import CloseIcon from "@mui/icons-material/Close";
import IconButton from "@mui/material/IconButton";
import { fetchPotentialApplicants, fetchApplicantInfo, fetchApplicantContactHistory, createNewApplicantProfile, updateApplicantProfile, reassignApplicantProfile } from "../../../../apiManager/services/FOI/foiApplicantProfileService";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import _ from 'lodash';
import { setFOIRequestApplicantProfile, setFOILoader } from "../../../../actions/FOI/foiRequestActions";
import { isBeforeOpen } from "../utils";
import ApplicantProfileModalHeader from "./ApplicantProfileModalHeader";
import ApplicantProfileModalContent from "./ApplicantProfileModalContent";
import ApplicantProfileModalActions from "./ApplicantProfileModalActions";

const useStyles = makeStyles((theme) => ({
    root: {
      "& .MuiTextField-root": {
        margin: theme.spacing(1, "0px"),
      },
    },
    disabledTitle: {
        opacity: "0.3", 
    },
}));

const ApplicantProfileModal = React.memo(({modalOpen, handleModalClose}) => {    
    const classes = useStyles();

    let requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
    const dispatch = useDispatch();
    const isAddRequest = window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1;
    const isUnopenedRequest = requestDetails?.currentState == "Unopened"

    const [isLoading, setIsLoading] = useState(true);
    const [rows, setRows] = useState([]);
    const [selectedApplicant, setSelectedApplicant] = useState(false)
    const [saveApplicantObject, setSaveApplicantObject] = React.useState({})
    const [showApplicantProfileTab, setShowApplicantProfileTab] = useState(true)
    const [showRequestHistoryTab, setShowRequestHistoryTab] = useState(false);
    const [showSearchApplicantsTab, setShowSearchApplicantsTab] = useState(false);
    const [confirmationMessage, setConfirmationMessage] = useState(false);
    const [createConfirmation, setCreateConfirmation] = useState(false);
    const [isProfileDifferent, setIsProfileDifferent] = useState(false);
    const [isUnassignProfile, setIsUnassignProfile] = useState(false);
    const [isChangeToDifferentProfile, setIsChangeToDifferentProfile] = useState(false);
    const [applicantHistory, setApplicantHistory] = useState(false);
    const [requestHistory, setRequestHistory] = useState(false);

    useEffect(() => {
        if (modalOpen) {
            setIsLoading(true);
            if (!requestDetails?.foiRequestApplicantID) {
                dispatch(fetchPotentialApplicants(
                    requestDetails.firstName,
                    requestDetails.lastName,
                    requestDetails.email,
                    requestDetails.primaryPhone,
                    (err, res) => {
                        setRows(res);
                        setIsLoading(false);
                    }))
            } else {
                setSelectedApplicant(true);
                dispatch(fetchApplicantInfo(requestDetails.foiRequestApplicantID, (err, res) => {
                    const {requestHistory, ...selectedApplicant} = res
                    setSelectedApplicant(selectedApplicant);
                    setRequestHistory(requestHistory)
                    setIsLoading(false);
                }))
            }
        }
    }, [modalOpen])

    useEffect(() => {
        setSaveApplicantObject({...selectedApplicant})
        for (let field in selectedApplicant) {
            if (field === 'additionalPersonalInfo') {
                if (requestDetails[field] && requestDetails.requestType === 'personal') {
                    for (let additionalField in selectedApplicant[field]) {
                        if (requestDetails[field][additionalField] && selectedApplicant[field][additionalField] !== requestDetails[field][additionalField]) {
                            setIsProfileDifferent(true);
                            break;
                        }
                    }
                }
            } else if (selectedApplicant[field] !== requestDetails[field]) {
                setIsProfileDifferent(true);
                break;
            }
        }
        if (requestDetails?.foiRequestApplicantID && requestDetails?.foiRequestApplicantID != selectedApplicant?.foiRequestApplicantID) {
            setIsChangeToDifferentProfile(true)
        } else {
            setIsChangeToDifferentProfile(false)
        }
    }, [selectedApplicant])

    const createSaveApplicantObject = (name, value, value2) => {
        let newApplicantObj = {...saveApplicantObject}
        if ([FOI_COMPONENT_CONSTANTS.DOB, FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS].includes(name)) {
            let additionalPersonalInfo = {...newApplicantObj.additionalPersonalInfo}
            additionalPersonalInfo[name] = value
            newApplicantObj.additionalPersonalInfo = additionalPersonalInfo;
        } else {            
            newApplicantObj[name] = value;
        }
        setSaveApplicantObject(newApplicantObj)
    }

    const handleClose = () => {
        setIsLoading(true);
        setRows([]);
        setSelectedApplicant(false);
        setSaveApplicantObject({})
        setConfirmationMessage(false);
        setCreateConfirmation(false);
        setIsProfileDifferent(false);
        setIsUnassignProfile(false);
        setApplicantHistory(false);
        setRequestHistory(false);
        handleModalClose();
    }

    const profilePayloadBuilder = () => {
        const payload = {
                "requestType": isBeforeOpen(requestDetails) ? "rawrequest" : "foirequest",
                "foiRequestId": requestDetails?.id,
                "rawRequestId": requestDetails?.rawRequestId,
                "previousRequestApplicantId": requestDetails?.foiRequestApplicantID,
                "applicant": saveApplicantObject
            }
        return payload
    }

    const executeProfileAction = (actionHandler, options = { shouldClear: false }) => {
        const { shouldClear = false } = options;
        const payload = profilePayloadBuilder();
        handleClose();
        dispatch(setFOILoader(true));
        dispatch(actionHandler(payload, (err, res) => {
            if (!err) {
                if (shouldClear) {
                    dispatch(setFOIRequestApplicantProfile({}));
                } else {
                    dispatch(setFOIRequestApplicantProfile({...saveApplicantObject, foiRequestApplicantID: res.id}));
                }
            }
        }));
    };

    const createProfile = () => {
        if (!createConfirmation) {
            setCreateConfirmation(true);
            return;
        }

        executeProfileAction(createNewApplicantProfile);
    };

    const updateProfile = () => {
        if (_.isEqual(selectedApplicant, saveApplicantObject) && !isChangeToDifferentProfile) {
            handleClose();
            dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
            return;
        }
        if (!confirmationMessage) {
            setConfirmationMessage(true);
            return;
        }
        executeProfileAction(updateApplicantProfile);
    };

    const reassignProfileToRequest = () => {
        if (isAddRequest || isUnopenedRequest) {
            handleClose();
            dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
            return;
        }
        if (!isChangeToDifferentProfile) {
            handleClose();
            dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
            return;
        }
        if (!confirmationMessage) {
            setConfirmationMessage(true);
            return;
        }
        executeProfileAction(reassignApplicantProfile);
    };

    const showApplicantHistory = () => {
        dispatch(fetchApplicantContactHistory(selectedApplicant.foiRequestApplicantID, (err, res) => {
            setApplicantHistory(res);
        }))       
    }

    const back = () => {
        setIsUnassignProfile(false);
        if (confirmationMessage) {
            setConfirmationMessage(false);
        } else if (applicantHistory) {
            setApplicantHistory(false);
        } else if (createConfirmation) {
            setCreateConfirmation(false)
        } else if (!isBeforeOpen(requestDetails)) {
            handleClose();
        } else if (requestDetails?.foiRequestApplicantID) {
            // handleClose();
            dispatch(fetchApplicantInfo(requestDetails.foiRequestApplicantID, (err, res) => {
                    const {requestHistory, ...selectedApplicant} = res
                    setSelectedApplicant(selectedApplicant);
                    setRequestHistory(requestHistory)
                    setIsLoading(false);
                    setShowSearchApplicantsTab(true);
                    setShowApplicantProfileTab(false);
                }))
        } else {
            setSelectedApplicant(false);
            setShowRequestHistoryTab(false);
            setIsProfileDifferent(false);
        }
    }

    const cancel = () => {
        if (createConfirmation) {
            setCreateConfirmation(false);
        } else {
            handleClose();
        }
    }

    const isSaveDisabled = () => {
        if (isBeforeOpen(requestDetails) && !requestDetails?.foiRequestApplicantID) {
            return false
        } else {
            if (isChangeToDifferentProfile) return false
            return _.isEqual(selectedApplicant, saveApplicantObject)
        }
    }

    const warning = (field) => {
        const hasAtributes = Object.keys(saveApplicantObject).length !== 0
        if (hasAtributes && [FOI_COMPONENT_CONSTANTS.DOB, FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS].includes(field)) {
            if (!requestDetails.additionalPersonalInfo?.[field] && saveApplicantObject?.additionalPersonalInfo[field]) return true;
            return requestDetails.additionalPersonalInfo?.[field] && requestDetails.additionalPersonalInfo[field] !== saveApplicantObject?.additionalPersonalInfo[field]
        } else if (field == "otherNotes") {
            return selectedApplicant?.[field] != saveApplicantObject?.[field]
        } else {
            return requestDetails[field] != saveApplicantObject?.[field]
        }
    }

    // const renderApplicantProfileModalActions = () => {
    // // Buttons
    // const reassignProfileButton = (
    //     <button
    //     className={`btn-bottom btn-save btn`}
    //     onClick={reassignProfileToRequest}
    //     disabled={isSaveDisabled()}
    //     >
    //     Reassign Profile
    //     </button>
    // );
    // const selectProfileButton = (
    //     <button
    //     className={`btn-bottom btn-save btn`}
    //     onClick={reassignProfileToRequest}
    //     disabled={isSaveDisabled()}
    //     >
    //     Select Profile
    //     </button>
    // );

    // const confirmReassignProfileButton = (
    //     <button className={`btn-bottom btn-save btn`} onClick={reassignProfileToRequest}>
    //     Confirm Reassign Profile
    //     </button>
    // );

    // const confirmSelectedProfileButton = (
    //     <button className={`btn-bottom btn-save btn`} onClick={reassignProfileToRequest}>
    //     Confirm Reassigned Profile
    //     </button>
    // );


    // const confirmBackButton = (
    //     <button
    //     className="btn-bottom btn-cancel"
    //     onClick={() => setConfirmationMessage(false)}
    //     >
    //     Back
    //     </button>
    // );

    // const backButton = (
    //     <button className="btn-bottom btn-cancel" onClick={back}>
    //     Back
    //     </button>
    // );

    // const updateProfileButton = (
    //     <button
    //     className={`btn-bottom btn-save btn`}
    //     onClick={updateProfile}
    //     disabled={isSaveDisabled()}
    //     >
    //     Update Profile
    //     </button>
    // );

    // // const unassignProfileButton = (
    // //     <button className={`btn-bottom btn-save btn`} onClick={unassignProfileFromRequest}>
    // //     Unassign Profile
    // //     </button>
    // // );

    // const confirmUpdateProfileButton = (
    //     <button className={`btn-bottom btn-save btn`} onClick={updateProfile}>
    //     Save Changes
    //     </button>
    // );

    // const createNewProfileButton = (
    //     <button className={`btn-bottom btn-save btn`} onClick={createProfile}>
    //     Create New Profile
    //     </button>
    // );

    // const confirmCreateNewProfileButton = (
    //     <button className={`btn-bottom btn-save btn`} onClick={createProfile}>
    //     Confirm New Profile
    //     </button>
    // );

    // const cancelButton = (
    //     <button className="btn-bottom btn-cancel" onClick={cancel}>
    //     Cancel
    //     </button>
    // );

    // // Rendering logic
    // if (isBeforeOpen(requestDetails)) {
    //     const hasAssignedApplicant = requestDetails?.foiRequestApplicantID ? true : false
    //     if (createConfirmation) {
    //         return (<>
    //                 {confirmCreateNewProfileButton}
    //                 {backButton}
    //             </>)
    //         }
        
    //     if (selectedApplicant && !hasAssignedApplicant || isChangeToDifferentProfile) {
    //         return (
    //         <>
    //             {!applicantHistory && (
    //             <>
    //                 {selectProfileButton}
    //             </>
    //             )}
    //             {backButton}
    //         </>
    //         );
    //     }
        
    //     if (selectedApplicant && hasAssignedApplicant) {
    //         return (
    //         <>
    //             {!applicantHistory && (
    //             <>
    //                 {createNewProfileButton}
    //                 {/* {selectProfileButton} */}
    //                 {updateProfileButton}
    //             </>
    //             )}
    //             {backButton}
    //         </>
    //         );
    //     }

    //     if (!selectedApplicant) {
    //         return (<>
    //                 {createNewProfileButton}
    //                 {backButton}
    //             </>)
    //     }
    //     }
    // return;
    // if (isUnassignProfile && confirmationMessage) {
    //     return (
    //     <>
    //         {unassignProfileButton}
    //         {backButton}
    //     </>
    //     );
    // }
    // if (createConfirmation && isBeforeOpen(requestDetails)) {
    //     return <>{backButton}</>
    // }

    // if (isChangeToDifferentProfile && !confirmationMessage) return (
    //     <>
    //         {!applicantHistory && selectProfileButton}
    //         {backButton}
    //     </>
    // )
    // if (isChangeToDifferentProfile && confirmationMessage) return (
    //    <>
    //     {confirmSelectedProfileButton}
    //     {backButton}
    //    </>
    // )

    // if (isChangeToDifferentProfile) {
    //     if (confirmationMessage) {
    //     return (
    //         <>
    //             {confirmReassignProfileButton}
    //             {confirmBackButton}
    //         </>
    //     );
    //     } else {
    //     return (
    //         <>
    //             {!applicantHistory && reassignProfileButton}
    //             {backButton}
    //         </>
    //     );
    //     }
    // }

    // if (selectedApplicant) {
    //     if (confirmationMessage) {
    //     return (
    //         <>
    //         {confirmUpdateProfileButton}
    //         {confirmBackButton}
    //         </>
    //     );
    //     } else if (createConfirmation) {
    //     return (
    //         <>
    //         {!applicantHistory && (
    //             <>
    //             {confirmCreateNewProfileButton}
    //             </>
    //         )}
    //         {backButton}
    //         </>
    //     );
    //     } else {
    //     if (isBeforeOpen(requestDetails)) {
    //         return (
    //         <>
    //             {!applicantHistory && (
    //             <>
    //                 {updateProfileButton}
    //                 {unassignProfileButton}
    //             </>
    //             )}
    //             {backButton}
    //         </>
    //         );
    //     }
    //     return (
    //         <>
    //         {!applicantHistory && (
    //             <>
    //             {createNewProfileButton}
    //             {updateProfileButton}
    //             </>
    //         )}
    //         {backButton}
    //         </>
    //     );
    //     }
    // }
    // return (
    //     <>
    //         {createNewProfileButton}
    //         {cancelButton}
    //     </>
    //     );
    // };
    
    return (
      <div className={"applicant-profile-modal-div"}>
        <ReactModal
          initWidth={900}
          initHeight={600}
          minWidth={400}
          minHeight={200}
          className={`${classes.root} applicant-profile-modal state-change-dialog`}
          onRequestClose={handleClose}
          isOpen={modalOpen}
        >
          <DialogTitle disableTypography id="request-history-dialog-title">
            <ApplicantProfileModalHeader 
                confirmationMessage={confirmationMessage}
                isUnassignProfile={isUnassignProfile}
                applicantHistory={applicantHistory}
                selectedApplicant={selectedApplicant}
                createConfirmation={createConfirmation}
                requestHistory={requestHistory}
                showApplicantProfileTab={showApplicantProfileTab}
                setShowApplicantProfileTab={setShowApplicantProfileTab}
                showRequestHistoryTab={showRequestHistoryTab}
                setShowRequestHistoryTab={setShowRequestHistoryTab}
                showSearchApplicantsTab={showSearchApplicantsTab}
                setShowSearchApplicantsTab={setShowSearchApplicantsTab}
                classes={classes}
            />
            <IconButton onClick={handleClose} value="close">
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
        <div style={{ overflowY: "scroll", height: "calc(100% - 181px)" }}>
          <DialogContent sx={{padding: "15px 50px 0 50px", height: "100%"}}>
            <ApplicantProfileModalContent 
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                rows={rows}
                setRows={setRows}
                requestDetails={requestDetails}
                saveApplicantObject={saveApplicantObject}
                setSaveApplicantObject={setSaveApplicantObject}
                createSaveApplicantObject={createSaveApplicantObject}
                selectedApplicant={selectedApplicant}
                setSelectedApplicant={setSelectedApplicant}
                applicantHistory={applicantHistory}
                showApplicantHistory={showApplicantHistory}
                createConfirmation={createConfirmation}
                confirmationMessage={confirmationMessage}
                isAddRequest={isAddRequest}
                isUnopenedRequest={isUnopenedRequest}
                isProfileDifferent={isProfileDifferent}
                setIsProfileDifferent={setIsProfileDifferent}
                isChangeToDifferentProfile={isChangeToDifferentProfile}
                isUnassignProfile={isUnassignProfile}
                warning={warning}
                requestHistory={requestHistory}
                setRequestHistory={setRequestHistory}
                dispatch={dispatch}
                showApplicantProfileTab={showApplicantProfileTab}
                setShowApplicantProfileTab={setShowApplicantProfileTab}
                showSearchApplicantsTab={showSearchApplicantsTab}
                setShowSearchApplicantsTab={setShowSearchApplicantsTab}
                showRequestHistoryTab={showRequestHistoryTab}
            />
          </DialogContent>
        </div>
          <DialogActions sx={{padding: 30}}>
            {/* {renderApplicantProfileModalActions()} */}
            <ApplicantProfileModalActions
                requestDetails={requestDetails}
                reassignProfileToRequest={reassignProfileToRequest}
                isSaveDisabled={isSaveDisabled}
                confirmationMessage={confirmationMessage}
                setConfirmationMessage={setConfirmationMessage}
                back={back}
                cancel={cancel}
                updateProfile={updateProfile}
                isBeforeOpen={isBeforeOpen}
                createConfirmation={createConfirmation}
                selectedApplicant={selectedApplicant}
                applicantHistory={applicantHistory}
                isChangeToDifferentProfile={isChangeToDifferentProfile}
                isUnassignProfile={isUnassignProfile}
                createProfile={createProfile}
            />
          </DialogActions>
        </ReactModal>
      </div>
    );
  });

export default ApplicantProfileModal;
