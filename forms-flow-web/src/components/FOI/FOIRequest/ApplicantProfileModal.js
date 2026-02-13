import React, { useState, memo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import ReactModal from "react-modal-resizable-draggable";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import CloseIcon from "@mui/icons-material/Close";
import IconButton from "@mui/material/IconButton";
import { ButtonBase } from "@mui/material";
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import { fetchPotentialApplicants, fetchApplicantInfo, fetchApplicantContactHistory, createNewApplicantProfile, updateApplicantProfile, reassignApplicantProfile, unassignApplicantProfile} from "../../../apiManager/services/FOI/foiApplicantProfileService";
import AddressContactDetails from "./AddressContanctInfo";
import ApplicantDetails from "./ApplicantDetails"
import AdditionalApplicantDetails from "./AdditionalApplicantDetails";
import Divider from "@mui/material/Divider";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import clsx from "clsx";
import _ from 'lodash';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { setFOIRequestApplicantProfile, setFOILoader } from "../../../actions/FOI/foiRequestActions";
import { toast } from "react-toastify";
import Loading from "../../../containers/Loading";
import { isBeforeOpen } from "./utils";
import { ApplicantProfileSearchView } from "./ApplicantProfileSearchView";
import Alert from "@mui/material/Alert";

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
    requestType = "general"
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
                disableInput={disableInput || requestType == "general"}
                defaultExpanded={defaultExpanded}
                warning={requestType != "general" || isAddRequest ? warning : null}
            />
        </>
    )
}

const ApplicantProfileModal = React.memo(({modalOpen, handleModalClose}) => {    
    const classes = useStyles();

    const isAddRequest = window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1;

    let requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
    const dispatch = useDispatch();

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
    
    const requestHistoryColumns = [
        {
            field: "axisrequestid",
            headerName: "REQUEST ID",
            flex: 1,
            renderCell: (params) => {
                return <span className="table-cell-truncate">
                    <a style={{color: "rgba(0, 0, 0, 0.87)"}} href={params.row.ministryrequestid ?
                        "/foi/foirequests/" + params.row.requestid + "/ministryrequest/" +  params.row.ministryrequestid :
                        "/foi/reviewrequest/" + params.row.requestid
                    } target="_blank">
                        {params.row.axisrequestid}
                    </a>
                </span>
            }
        },
        {
            field: "requeststatus",
            headerName: "CURRENT STATE",
            flex: 1,
        },
        {
            field: "receiveddate",
            headerName: "RECEIVED DATE",
            flex: 1,
        },
        {
            field: "description",
            headerName: "REQUEST DESRCIPTION",
            flex: 2,
        },
    ];

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
        if (requestDetails?.foiRequestApplicantID != selectedApplicant?.foiRequestApplicantID) {
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
                    dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
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
        if (isAddRequest) {
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

    const clearObject = (obj) => {
        return Object.fromEntries(
            Object.entries(obj)
            .map(([key, value]) => {
            if (value && typeof value === "object" && !Array.isArray(value)) {
                return [key, clearObject(value)];
            }
            return [key, null];
            })
        );
    };

    const unassignProfileFromRequest = () => {
        if (!confirmationMessage) {
            setIsUnassignProfile(true);
            setConfirmationMessage(true);
            return;
        }
        if (isAddRequest) {
            handleClose();
            const clearedSaveApplicantObject = clearObject(saveApplicantObject)
            dispatch(setFOIRequestApplicantProfile({...clearedSaveApplicantObject}));
            return;
        }
        executeProfileAction(unassignApplicantProfile, {shouldClear: true});
    };

    const copyInfo = () => {
        let updatedApplicant = {...selectedApplicant}
        for (let field in selectedApplicant) {
            if (field === 'additionalPersonalInfo' && requestDetails.requestType === 'personal') {
                for (let infofield in requestDetails[field]) {
                    if (requestDetails[field][infofield] && requestDetails[field][infofield] !== selectedApplicant[field][infofield]) {
                        updatedApplicant[field][infofield] = requestDetails[field][infofield];
                    }
                }
            } else if (requestDetails[field] && selectedApplicant[field] !== requestDetails[field]) {
                updatedApplicant[field] = requestDetails[field];
            }
        }
        setSaveApplicantObject(updatedApplicant);
        setIsProfileDifferent(false);
    }

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
            handleClose();
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
        } else {
            return requestDetails[field] != saveApplicantObject?.[field]
        }
    }

    const renderApplicantProfileModalHeaders = () => {
        const FormattedHeader = ({ text }) => {
            return (
                <h3 className="request-history-header search-applicants-header applicant-profile-header">
                    {text}
                </h3>
            );
        };
        if (confirmationMessage && !isUnassignProfile)
            return <FormattedHeader text={"Saving Changes to Applicant Profile"} />;
        if (applicantHistory) return <FormattedHeader text={"Applicant History"} />;
        if (isUnassignProfile)
            return <FormattedHeader text={"Unassign Applicant Profile"} />;
        if (!selectedApplicant) return <FormattedHeader text={"Search Applicants"} />;
        if (createConfirmation)
            return <FormattedHeader text={"Create New Profile"} />;

        // Renders the tab options if none of the above conditions are met
        return (
            <>
            <ButtonBase
                onClick={() => {
                setShowApplicantProfileTab(true);
                setShowRequestHistoryTab(false);
                setShowSearchApplicantsTab(false);
                }}
                disableRipple
                className={clsx("request-history-header applicant-profile-header", {
                [classes.disabledTitle]: !showApplicantProfileTab,
                })}
            >
                Applicant Profile
            </ButtonBase>
            <Divider
                sx={{
                mr: 2,
                ml: 2,
                borderRightWidth: 3,
                height: 28,
                borderColor: "black",
                display: "inline-flex",
                top: 8,
                position: "relative",
                }}
                flexItem
                orientation="vertical"
            />
            <ButtonBase
                onClick={() => {
                setShowRequestHistoryTab(true);
                setShowApplicantProfileTab(false);
                setShowSearchApplicantsTab(false);
                }}
                disableRipple
                className={clsx("request-history-header applicant-profile-header", {
                [classes.disabledTitle]: !showRequestHistoryTab,
                })}
            >
                Request History ({requestHistory?.length})
            </ButtonBase>
            <Divider
                sx={{
                mr: 2,
                ml: 2,
                borderRightWidth: 3,
                height: 28,
                borderColor: "black",
                display: "inline-flex",
                top: 8,
                position: "relative",
                }}
                flexItem
                orientation="vertical"
            />
            <ButtonBase
                onClick={() => {
                setShowSearchApplicantsTab(true);
                setShowRequestHistoryTab(false);
                setShowApplicantProfileTab(false);
                }}
                disableRipple
                className={clsx("request-history-header applicant-profile-header", {
                [classes.disabledTitle]: !showSearchApplicantsTab,
                })}
            >
                Search Applicants
            </ButtonBase>
            </>
        );
    };


    const renderApplicantProfileModalContent = () => {
        if (isLoading) {
            return <Loading />;
        }

        if (confirmationMessage && isChangeToDifferentProfile) return (
            <>
  
                <Alert severity="warning" sx={{ fontSize: '1.2rem' }}>
                    Just a heads up:<br></br>
                    Previous information on this request will be overwritten by the applicant profile information, and won't be retrievable.<br></br>
                    Are you sure you would like to change the applicant profile linked to this request?
                </Alert>
            </>
            
        )
        if (confirmationMessage && isUnassignProfile) return (
            <div style={{ textAlign: "center" }}>
                The linked applicant profile will be removed, but the information for this request will stay the same.
                You can make updates to the request, and when the request is moved into the Open state, the correspondening
                applicant profile will be automatically created.
            </div>
        );

        if (confirmationMessage) return (
            <div style={{ textAlign: "center" }}>
                Are you sure you would like to save changes for all active requests associated with this profile?
                <br />
                <i>Please ensure you have checked the Request History to see the request(s) that will be affected.</i>
            </div>
        );

        if (createConfirmation && isBeforeOpen(requestDetails)) {
            return (
            <div style={{ textAlign: "center" }}>
                New Profile will be created automatically when request is moved to open state.
                <br />
                <i>Please make any additional changes in Request Details.</i>
            </div>
            );
        } 
        if (createConfirmation) return (
            <>
                <div style={{ textAlign: "center" }}>
                    A new Profile will be created from the following information. The old profile will 
                    not be connected to this request anymore.
                </div>
                <ApplicantDetailsSections
                    requestDetails={saveApplicantObject}
                    contactDetailsNotGiven={false}
                    createSaveRequestObject={createSaveApplicantObject}
                    handleApplicantDetailsInitialValue={() => {}}
                    handleApplicantDetailsValue={() => {}}
                    disableInput={true}
                    defaultExpanded={true}
                    showHistory={showApplicantHistory}
                    warning={null}
                    displayOtherNotes={true}
                    isAddRequest={isAddRequest}
                    requestType={requestDetails?.requestType}
                />
            </>
        );

        if (applicantHistory) {
            return (
            <>
                {applicantHistory.map((entry, index) => (
                <Accordion key={index} defaultExpanded={index === 0}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography className="acc-request-description">
                        APPLICANT CONTACT DETAILS
                    </Typography>
                    <Typography className="acc-username-date">
                        {entry.createdby} - {entry.updatedat}
                    </Typography>
                    </AccordionSummary>

                    <AccordionDetails className="acc-details">
                    <div className="acc-details-1">
                        {Object.keys(entry.fields).map((field) => (
                        <React.Fragment key={field}>
                            <div className="acc-applicant-profile-history-row">
                            <Typography className="acc-start-date">
                                <b>{field}: </b>{entry.fields[field]}
                            </Typography>
                            </div>
                            <div className="acc-applicant-profile-history-row">
                            <Typography className="acc-start-date">
                                <b>Previous {field}: </b>{entry.previousvalues[field]}
                            </Typography>
                            </div>
                        </React.Fragment>
                        ))}
                    </div>
                    </AccordionDetails>
                </Accordion>
                ))}
            </>
            );
        }

        const renderApplicantProfileTabMessage = () => {
            if (isChangeToDifferentProfile) return (
                    <span style={{ fontSize: "13px" }}>
                    You are changing the applicant profile that is linked to this request. 
                    </span>
                )
            if (isProfileDifferent) return (
                <span style={{ fontSize: "13px" }}>
                Some of the fields in this profile do not match your original request.
                <button
                    type="button"
                    className="btn-link btn-update-profile"
                    onClick={copyInfo}
                >
                    UPDATE ALL
                </button>
                </span>
            )
            return (
                <span style={{ fontSize: "13px" }}>
                All of the fields in the applicant profile match your original request.
                </span>
            )
        }

        if (showApplicantProfileTab) {
            if (selectedApplicant) {
                return (
                <>
                    {renderApplicantProfileTabMessage()}

                    <ApplicantDetailsSections
                        requestDetails={saveApplicantObject}
                        contactDetailsNotGiven={false}
                        createSaveRequestObject={createSaveApplicantObject}
                        handleApplicantDetailsInitialValue={() => {}}
                        handleApplicantDetailsValue={() => {}}
                        disableInput={isChangeToDifferentProfile ? true : false}
                        defaultExpanded={isChangeToDifferentProfile ? true : false}
                        showHistory={showApplicantHistory}
                        warning={warning}
                        displayOtherNotes={true}
                        isAddRequest={isAddRequest}
                        requestType={requestDetails?.requestType}
                    />
                </>);
            } else {
                return (
                    <ApplicantProfileSearchView
                        isLoading={isLoading}
                        setIsLoading={setIsLoading}
                        rows={rows}
                        setRows={setRows}
                        setSelectedApplicant={setSelectedApplicant}
                        setRequestHistory={setRequestHistory}
                        dispatch={dispatch}
                        toast={toast}
                        initialSearchMode={isAddRequest ? "manual" : "auto"}
                    />
                )
            }
        }

        if (showRequestHistoryTab) {
            return <>
                        <Box sx={{ height: "100%", width: "100%" }}>
                        <DataGrid
                            className="foi-data-grid foi-request-history-grid"
                            rows={requestHistory}
                            columns={requestHistoryColumns}
                            rowHeight={30}
                            headerHeight={50}
                            hideFooter={true}
                            loading={isLoading}                
                            // onRowClick={selectApplicantRow}
                            getRowHeight={() => 'auto'} 
                            getRowId={(row) => row.filenumber}
                        />
                        </Box>
                    </>
        }

        if (showSearchApplicantsTab) {
            return (
                <ApplicantProfileSearchView 
                    setShowSearchApplicantsTab={setShowSearchApplicantsTab}
                    setShowApplicantProfileTab={setShowApplicantProfileTab}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                    rows={rows}
                    setRows={setRows}
                    setSelectedApplicant={setSelectedApplicant}
                    setRequestHistory={setRequestHistory}
                    dispatch={dispatch}
                    toast={toast}
                    initialSearchMode={"manual"}
                />
            )
        }
    };

    const renderApplicantProfileModalActions = () => {
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
        <button className={`btn-bottom btn-save btn`} onClick={reassignProfileToRequest}>
        Confirm Reassign Profile
        </button>
    );

    const confirmSelectedProfileButton = (
        <button className={`btn-bottom btn-save btn`} onClick={reassignProfileToRequest}>
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

    const unassignProfileButton = (
        <button className={`btn-bottom btn-save btn`} onClick={unassignProfileFromRequest}>
        Unassign Profile
        </button>
    );

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
    if (isUnassignProfile && confirmationMessage) {
        return (
        <>
            {unassignProfileButton}
            {backButton}
        </>
        );
    }
    if (createConfirmation && isBeforeOpen(requestDetails)) {
        return <>{backButton}</>
    }

    if (isChangeToDifferentProfile && !confirmationMessage) return (
        <>
            {!applicantHistory && selectProfileButton}
            {backButton}
        </>
    )
    if (isChangeToDifferentProfile && confirmationMessage) return (
       <>
        {confirmSelectedProfileButton}
        {backButton}
       </>
    )

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
            {!applicantHistory && (
                <>
                {confirmCreateNewProfileButton}
                </>
            )}
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
                    {unassignProfileButton}
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
            {renderApplicantProfileModalHeaders()}
            <IconButton onClick={handleClose} value="close">
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
        <div style={{ overflowY: "scroll", height: "calc(100% - 181px)" }}>
          <DialogContent sx={{padding: "15px 50px 0 50px", height: "100%"}}>
            {renderApplicantProfileModalContent()}
          </DialogContent>
        </div>
          <DialogActions sx={{padding: 30}}>
            {renderApplicantProfileModalActions()}
          </DialogActions>
        </ReactModal>
      </div>
    );
  });

export default ApplicantProfileModal;
