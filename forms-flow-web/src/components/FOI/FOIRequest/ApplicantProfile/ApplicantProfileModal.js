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
import { validateApplicantProfileFields } from "./helper";

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

const ApplicantProfileModal = React.memo(({modalOpen, handleModalClose, applicantType = "applicant"}) => {
    const classes = useStyles();

    let requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
    const dispatch = useDispatch();
    const isAddRequest = window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1;
    const isUnopenedRequest = requestDetails?.currentState == "Unopened"

    const [applicantId, setApplicantId] = useState(requestDetails?.foiRequestApplicantID)
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
    const [isChangeToDifferentProfile, setIsChangeToDifferentProfile] = useState(false);
    const [applicantHistory, setApplicantHistory] = useState(false);
    const [requestHistory, setRequestHistory] = useState(false);
    const [applicantProfileError, setApplicantProfileError] = useState(false);

    useEffect(() => {
        if (applicantType == "applicant") {
            setApplicantId(requestDetails?.foiRequestApplicantID)
        } else if (applicantType == "onbehalfof") {
            setApplicantId(requestDetails?.foiRequestOnBehalfOfApplicantID)
        }
    }, [requestDetails])

    useEffect(() => {
        if (modalOpen) {
            setIsLoading(true);
            if (!applicantId) {
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
                dispatch(fetchApplicantInfo(applicantId, (err, res) => {
                    const {requestHistory, ...selectedApplicant} = res
                    setSelectedApplicant(selectedApplicant);
                    setRequestHistory(requestHistory)
                    setIsLoading(false);
                }))
            }
        }
    }, [modalOpen, requestDetails, applicantId])

    useEffect(() => {
        setCreateConfirmation(!selectedApplicant && requestDetails?.sourceOfSubmission == "onlineform")
        if (!selectedApplicant && requestDetails?.sourceOfSubmission == "onlineform") {
            // If no applicant assigned, set applicant profile modal data to match existing request data
            if (applicantType == "applicant") {
                setSaveApplicantObject(requestDetails)
            } else if (applicantType == "onbehalfof") {
                let onbehalfofApplicantObj = {
                    firstName: requestDetails?.additionalPersonalInfo?.anotherFirstName,
                    lastName: requestDetails?.additionalPersonalInfo?.anotherLastName,
                    middleName: requestDetails?.additionalPersonalInfo?.anotherMiddleName,
                    birthDate: requestDetails?.additionalPersonalInfo?.anotherBirthDate,
                    alsoKnownAs: requestDetails?.additionalPersonalInfo?.anotherAlsoKnownAs
                }
                setSaveApplicantObject(onbehalfofApplicantObj)
            }
        }
    }, [modalOpen, selectedApplicant])

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
        if (applicantId != selectedApplicant?.foiRequestApplicantID) {
            setIsChangeToDifferentProfile(true)
        } else {
            setIsChangeToDifferentProfile(false)
        }
    }, [selectedApplicant])

    useEffect(() => {
        setApplicantProfileError(validateApplicantProfileFields(saveApplicantObject));
    }, [saveApplicantObject])

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
        setApplicantHistory(false);
        setRequestHistory(false);
        handleModalClose();
    }

    const profilePayloadBuilder = () => {
        const payload = {
                "requestType": isBeforeOpen(requestDetails) ? "rawrequest" : "foirequest",
                "applicantType": applicantType,
                "foiRequestId": requestDetails?.id,
                "rawRequestId": requestDetails?.rawRequestId,
                "previousRequestApplicantId": applicantId,
                "applicant": saveApplicantObject
            }
        return payload
    }

    const dispatchUpdatedApplicantInfo = (updatedApplicantId = null) => {
        // This handles applicant info for onbehalfof fields
        const onbehalfofApplicant = {
            "onbehalfofApplicant": {
                "firstName": saveApplicantObject.firstName,
                "middleName": saveApplicantObject.middleName,
                "lastName": saveApplicantObject.lastName,
                "alsoKnownAs": saveApplicantObject.additionalPersonalInfo?.alsoKnownAs,
                "birthDate": saveApplicantObject.additionalPersonalInfo?.birthDate,
                "foiRequestOnBehalfOfApplicantID": updatedApplicantId
            }
        }
        // This handles applicant info for updated primary applicants
        let updatedApplicantInfo = {...saveApplicantObject}
        if (updatedApplicantId) {
            updatedApplicantInfo = {...updatedApplicantInfo, foiRequestApplicantID: updatedApplicantId}
        }
        if (applicantType == "applicant") {
            dispatch(setFOIRequestApplicantProfile(updatedApplicantInfo));
        } else if (applicantType == "onbehalfof") {
            dispatch(setFOIRequestApplicantProfile(onbehalfofApplicant));
        }
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
                    dispatchUpdatedApplicantInfo(res.id);
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
            // dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
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
            dispatchUpdatedApplicantInfo(selectedApplicant.foiRequestApplicantID);
            return;
        }
        if (!isChangeToDifferentProfile) {
            handleClose();
            // dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
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
        if (confirmationMessage) {
            setConfirmationMessage(false);
        } else if (applicantHistory) {
            setApplicantHistory(false);
        } else if (createConfirmation) {
            setCreateConfirmation(false)
        } else if (!isBeforeOpen(requestDetails)) {
            handleClose();
        } else if (applicantId) {
            // handleClose();
            dispatch(fetchApplicantInfo(applicantId, (err, res) => {
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
        if (isBeforeOpen(requestDetails) && !applicantId) {
            return false
        } else {
            if (isChangeToDifferentProfile) return false
            return _.isEqual(selectedApplicant, saveApplicantObject)
        }
    }

    const warning = (field) => {
        const hasAtributes = Object.keys(saveApplicantObject).length !== 0
        if (hasAtributes && [FOI_COMPONENT_CONSTANTS.DOB, FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS].includes(field)) {
            if (!requestDetails?.additionalPersonalInfo?.[field] && saveApplicantObject?.additionalPersonalInfo?.[field]) return true;
            return requestDetails?.additionalPersonalInfo?.[field] && requestDetails?.additionalPersonalInfo?.[field] !== saveApplicantObject?.additionalPersonalInfo?.[field]
        } else if (field == "otherNotes") {
            return selectedApplicant?.[field] != saveApplicantObject?.[field]
        } else {
            return requestDetails?.[field] != saveApplicantObject?.[field]
        }
    }

    return (
      <div className={"applicant-profile-modal-div"}>
        <ReactModal
          initWidth={900}
          initHeight={600}
          minWidth={400}
          minHeight={200}
          className={`${classes.root} applicant-profile-modal state-change-dialog`}
          top={applicantType == "onbehalfof" ? 1350 : 100}
          left={applicantType == "onbehalfof" ? 198 : 500}
          onRequestClose={handleClose}
          isOpen={modalOpen}
        >
          <DialogTitle disableTypography id="request-history-dialog-title">
            <ApplicantProfileModalHeader 
                confirmationMessage={confirmationMessage}
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
                createProfile={createProfile}
                applicantProfileError={applicantProfileError}
            />
          </DialogActions>
        </ReactModal>
      </div>
    );
  });

export default ApplicantProfileModal;
