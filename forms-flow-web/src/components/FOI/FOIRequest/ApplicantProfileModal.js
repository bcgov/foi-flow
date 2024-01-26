import React, { useState, memo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import ReactModal from "react-modal-resizable-draggable";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import CloseIcon from "@mui/icons-material/Close";
import IconButton from "@mui/material/IconButton";
import { ButtonBase } from "@mui/material";
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import Grid from "@mui/material/Grid";
import { fetchPotentialApplicants, fetchApplicantInfo, fetchApplicantContactHistory, saveApplicantInfo, fetchApplicantProfileByKeyword, fetchApplicantRequests } from "../../../apiManager/services/FOI/foiApplicantProfileService";
import AddressContactDetails from "./AddressContanctInfo";
import ApplicantDetails from "./ApplicantDetails"
import AdditionalApplicantDetails from "./AdditionalApplicantDetails";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import { ClickableChip } from "../Dashboard/utils";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import clsx from "clsx";
import _ from 'lodash';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { setFOIRequestApplicantProfile, setFOILoader } from "../../../actions/FOI/foiRequestActions";
import { toast } from "react-toastify";
import Loading from "../../../containers/Loading";
import { isBeforeOpen } from "./utils";

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

    const isAddRequest = window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1;

    let requestDetails = useSelector((state) => state.foiRequests.foiRequestDetail);
    const dispatch = useDispatch();
    
    console.log(requestDetails);

    const [searchText, setSearchText] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [rows, setRows] = useState([]);
    const [selectedApplicant, setSelectedApplicant] = useState(false)
    const [searchMode, setSearchMode] = useState(isAddRequest ? "manual" : "auto")
    const [saveApplicantObject, setSaveApplicantObject] = React.useState({})
    const [showRequestHistory, setShowRequestHistory] = useState(false);
    const [confirmationMessage, setConfirmationMessage] = useState(false);
    const [createConfirmation, setCreateConfirmation] = useState(false);
    const [isProfileDifferent, setIsProfileDifferent] = useState(false);
    const [applicantHistory, setApplicantHistory] = useState(false);
    const [requestHistory, setRequestHistory] = useState(false);

    const columns = [
        {
          field: 'firstName',
          headerName: 'FIRST NAME',
          flex: 1,
        },
        {
          field: 'middleName',
          headerName: 'MIDDLE NAME',
          flex: 1,
        },
        {
          field: 'lastName',
          headerName: 'LAST NAME',
          flex: 1,
        },
        {
          field: 'birthDate',
          headerName: 'DATE OF BIRTH',
          flex: 1,
          valueGetter: (params) => params.row?.additionalPersonalInfo?.birthDate 
        },
        {
          field: 'email',
          headerName: 'EMAIL',
          flex: 1,
        },
        {
          field: 'primaryPhone',
          headerName: 'PRIMARY PHONE',
          flex: 1,
        },
    ];

    
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
            if (isBeforeOpen(requestDetails)) {
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
            console.log(field)
            if (field === 'additionalPersonalInfo') {
                if (requestDetails[field] && requestDetails.requestType === 'personal') {
                    for (let additionalField in selectedApplicant[field]) {
                        if (requestDetails[field][additionalField] && selectedApplicant[field][additionalField] !== requestDetails[field][additionalField]) {
                            setIsProfileDifferent(true);
                            break;
                        }
                    }
                }
            } else if (requestDetails[field] && selectedApplicant[field] !== requestDetails[field]) {
                setIsProfileDifferent(true);
                break;
            }
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

    const selectApplicantRow = (e) => {
        dispatch(fetchApplicantRequests(e.row.foiRequestApplicantID, (err, res) => {
            setSelectedApplicant(e.row)
            setRequestHistory(res);
            setIsLoading(false);
        }))
    }

    const handleClose = () => {
        setSearchText("");
        setIsLoading(true);
        setRows([]);
        setSelectedApplicant(false);
        setSearchMode(isAddRequest ? "manual" : "auto")
        setSaveApplicantObject({})
        setShowRequestHistory(false);
        setConfirmationMessage(false);
        setCreateConfirmation(false);
        setIsProfileDifferent(false);
        setApplicantHistory(false);
        setRequestHistory(false);
        handleModalClose();
    }

    const search = (rows) => {
        return rows.filter(r => (r.firstName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) || 
            (r.middleName?.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
            (r.lastName.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
            (r.birthDate?.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
            (r.email?.toLowerCase().indexOf(searchText.toLowerCase()) > -1) ||
            (r.primaryPhone?.toLowerCase().indexOf(searchText.toLowerCase()) > -1) 
        )
    }

    const onSearchChange = (e) => {
        if (searchMode === 'auto') {
            setSearchText(e.target.value)
        }
    }

    const createKeywordJSON = (keyword) => {
        const keywordJSON = {
            "keywords": {}
        }
        const mobileNumberRegex = /^(\+\d{1,3}[-.●]?)?\(?\d{3}\)?[-.●]?\d{3}[-.●]?\d{4}$/;
        const stringRegex = /^[A-Za-z0-9\s.@!#$%^&*()\-_=+[\]{};:'",<.>/?\\|]+$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValidEmail = emailRegex.test(keyword);
        const isValidNumber = mobileNumberRegex.test(keyword);
        const isValidString = stringRegex.test(keyword)
        if (isValidEmail) {
            keywordJSON.keywords["email"] = keyword;
        }            
        if (isValidNumber) {
            keywordJSON.keywords["homephone"] = keyword;
            keywordJSON.keywords["workphone"] = keyword;
            keywordJSON.keywords["workphone2"] = keyword;
            keywordJSON.keywords["mobilephone"] = keyword;
        }            
        if (isValidString) {
            keywordJSON.keywords["firstname"] = keyword;
            keywordJSON.keywords["lastname"] = keyword;
            keywordJSON.keywords["email"] = keyword;
        }
        return keywordJSON;
    }

    const onSearchEnter = (e) => {
        if (searchMode === 'manual' && e.key === 'Enter') {
            const keywordJSON = createKeywordJSON(e.target.value)
            setIsLoading(true);
                dispatch(fetchApplicantProfileByKeyword(
                    keywordJSON,
                    (err, res) => {
                        if (!err) {
                            setRows(res);
                            setIsLoading(false);
                        }
                        else {
                            toast.error(
                                "Temporarily unable to fetch applicant profiles. Please try again in a few minutes.",
                                {
                                  position: "top-right",
                                  autoClose: 3000,
                                  hideProgressBar: true,
                                  closeOnClick: true,
                                  pauseOnHover: true,
                                  draggable: true,
                                  progress: undefined,
                                }
                              );
                        }
                        
                    }))
        }
    }

    const selectProfile = () => {
        if (confirmationMessage) {
            handleClose();
            // set loading screen
            dispatch(setFOILoader(true));
            dispatch(saveApplicantInfo(saveApplicantObject, (err, res) => {
                if (!err) {
                    // unset loading screen
                    dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
                }
            }));
        } else if (_.isEqual(selectedApplicant, saveApplicantObject)) {
            handleClose();
            dispatch(setFOIRequestApplicantProfile(saveApplicantObject));
        } else {
            setConfirmationMessage(true);
        }
    }

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
        if (applicantHistory) {
            setApplicantHistory(false);            
        } else if (!isBeforeOpen(requestDetails)) {
            handleClose();
        } else {
            setSelectedApplicant(false);
            setShowRequestHistory(false);
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

    const createProfile = () => {
        if (!createConfirmation) {
            setCreateConfirmation(true);
        } else {
            dispatch(setFOIRequestApplicantProfile({foiRequestApplicantID: -1}));
            handleClose();
        }
    }

    const isSaveDisabled = () => {
        if (isBeforeOpen(requestDetails)) {
            return false
        } else {
            return _.isEqual(selectedApplicant, saveApplicantObject)
        }
    }

    const warning = (field) => {
        if ([FOI_COMPONENT_CONSTANTS.DOB, FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS].includes(field)) {
            return requestDetails.additionalPersonalInfo?.[field] && requestDetails.additionalPersonalInfo[field] !== saveApplicantObject?.additionalPersonalInfo[field]
        } else {
            return requestDetails[field] && requestDetails[field] !== saveApplicantObject?.[field]
        }
    }

    
    return (
      <div className={"applicant-profile-modal-div"}>
        <ReactModal
          initWidth={800}
          initHeight={600}
          minWidth={400}
          minHeight={200}
          className={`${classes.root} applicant-profile-modal state-change-dialog`}
          onRequestClose={handleClose}
          isOpen={modalOpen}
        >
          <DialogTitle disableTypography id="request-history-dialog-title">
            {selectedApplicant ? 
                <h3 className="request-history-header search-applicants-header applicant-profile-header">
                    <ButtonBase
                        onClick={() => setShowRequestHistory(false)}
                        disableRipple
                        className={clsx("request-history-header applicant-profile-header", {
                            [classes.disabledTitle]: showRequestHistory
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
                        position: "relative"
                        }}
                        flexItem
                        orientation="vertical"
                    />
                    <ButtonBase
                        onClick={() => setShowRequestHistory(true)}
                        disableRipple
                        className={clsx("request-history-header applicant-profile-header", {
                            [classes.disabledTitle]: !showRequestHistory
                        })}
                    >
                        Request History ({requestHistory?.length})
                    </ButtonBase>
                </h3>
                :
                <h2 className="request-history-header search-applicants-header">
                Search Applicants
                </h2>
            }
            <IconButton onClick={handleClose} value="close">
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
        <div style={{ overflowY: "scroll", height: "calc(100% - 181px)" }}>
          <DialogContent sx={{padding: "15px 50px 0 50px", height: "100%"}}>
                {selectedApplicant ?
                    confirmationMessage ? 
                    <div style={{textAlign: "center"}}>Are you sure you would like to save changes for all open and intake in progress requests associated with this profile?<br></br> <i>Please ensure you have checked the Request History to see the request(s) that will be affected.</i></div>
                    :
                    (showRequestHistory ?
                        <>
                            <Box sx={{ height: "100%", width: "100%" }}>
                            <DataGrid
                                className="foi-data-grid foi-request-history-grid"
                                rows={requestHistory}
                                columns={requestHistoryColumns}
                                rowHeight={30}
                                headerHeight={50}
                                hideFooter={true}
                                loading={isLoading}                
                                onRowClick={selectApplicantRow}
                                getRowHeight={() => 'auto'} 
                                getRowId={(row) => row.filenumber}
                            />
                            </Box>
                        </>:
                        applicantHistory ? 
                        <>
                        {applicantHistory.map((entry, index) => {
                        return (<Accordion defaultExpanded={index === 0}>
                            <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            aria-controls="panel1a-content"         
                            >
                                <Typography className="acc-request-description">{`APPLICANT CONTACT DETAILS`}</Typography>
                                <Typography className="acc-username-date">{entry.createdby} - {entry.updatedat}</Typography>
                            </AccordionSummary>
                            <AccordionDetails className="acc-details">
                                <div className="acc-details-1">
                                    {Object.keys(entry.fields).map((field) => 
                                        <div className="acc-request-description-row">
                                            <Typography className="acc-start-date"><b>{field}: </b>{entry.fields[field]}</Typography>                                        
                                        </div>
                                    )}
                                </div>
                            </AccordionDetails>
                        </Accordion>)   
                        })} 
                        </>
                        :
                        isLoading ? <Loading /> : <>
                        {isProfileDifferent && 
                            <span style={{ fontSize: "13px" }}>
                                Some of the fields in this profile do not match your original request. 
                                <button type="button" class="btn-link btn-update-profile" onClick={copyInfo}>UPDATE ALL</button>
                            </span>
                        }
                        <ApplicantDetails
                            requestDetails={saveApplicantObject}
                            contactDetailsNotGiven={false}
                            createSaveRequestObject={createSaveApplicantObject}
                            handleApplicantDetailsInitialValue={() => {}}
                            handleApplicantDetailsValue={() => {}}
                            disableInput={false}
                            defaultExpanded={true}
                            showHistory={showApplicantHistory}
                            warning={warning}
                        />
                        <AddressContactDetails
                            requestDetails={saveApplicantObject}
                            contactDetailsNotGiven={false}
                            createSaveRequestObject={createSaveApplicantObject}
                            handleContactDetailsInitialValue={() => {}}
                            handleContanctDetailsValue={() => {}}
                            handleEmailValidation={() => {}}
                            disableInput={false}
                            defaultExpanded={false}
                            warning={warning}
                        />
                        <AdditionalApplicantDetails
                            requestDetails={saveApplicantObject}
                            createSaveRequestObject={createSaveApplicantObject}
                            disableInput={false}
                            defaultExpanded={false}
                            warning={warning}
                        />
                    </>)
                        :
                    createConfirmation ? 
                    <div style={{textAlign: "center"}}>New Profile will be created automatically when request is moved to open state.<br></br> <i>Please make any additional changes in Request Details.</i></div>
                    :
                    <>
                    <div style={{ fontSize: "13px" }}>
                    Select an applicant to view their details. Or create a new profile
                    if applicant cannot be found.
                    </div>
                    <Paper
                    component={Grid}
                    sx={{
                        border: "1px solid #38598A",
                        color: "#38598A",
                        margin: "20px 0",
                    }}
                    alignItems="center"
                    justifyContent="center"
                    direction="row"
                    container
                    item
                    xs={12}
                    elevation={0}
                    >
                    <Grid
                    item
                    container
                    alignItems="center"
                    direction="row"
                    xs={true}
                    sx={{
                        borderRight: "2px solid #38598A",
                        backgroundColor: "rgba(56,89,138,0.1)",                        
                    }}
                    >
                    <InputBase
                        id="filter"
                        placeholder="Search..."
                        defaultValue={searchText}
                        onChange={onSearchChange}
                        onKeyDown={onSearchEnter}
                        sx={{
                        color: "#38598A",
                        }}
                        startAdornment={
                        <InputAdornment position="start">
                            <IconButton sx={{ color: "#38598A" }}>
                            <span className="hideContent">Search</span>
                            <SearchIcon />
                            </IconButton>
                        </InputAdornment>
                        }
                        fullWidth
                    />
                    </Grid>                    
                    <Grid
                        item
                        container
                        alignItems="flex-start"
                        justifyContent="center"
                        xs={2.5}
                        minWidth="100px"
                    >
                        <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
                        <ClickableChip
                            label={"MANUAL"}
                            color="primary"
                            size="small"
                            onClick={() => setSearchMode("manual")}
                            clicked={searchMode === "manual"}
                        />
                        <ClickableChip
                            label={"AUTO"}
                            color="primary"
                            size="small"
                            onClick={() => setSearchMode("auto")}
                            clicked={searchMode === "auto"}
                        />
                        </Stack>
                    </Grid>
                    </Paper>
                    <Box sx={{ height: "calc(100% - 100px)", width: "100%" }}>
                    <DataGrid
                        className="foi-data-grid foi-applicant-data-grid"
                        rows={search(rows)}
                        columns={columns}
                        hideFooter={true}
                        pageSizeOptions={[5]}
                        rowHeight={30}
                        headerHeight={50}
                        loading={isLoading}                
                        onRowClick={selectApplicantRow}
                        getRowId={(row) => row.foiRequestApplicantID}
                    />
                    </Box>
                    </>                
                }
          </DialogContent>
        </div>
          <DialogActions sx={{padding: 30}}>
            {selectedApplicant ? 
                (confirmationMessage ?
                    <><button
                        className={`btn-bottom btn-save btn`}
                        onClick={selectProfile}
                    >
                    Save Changes
                    </button>
                    <button className="btn-bottom btn-cancel" onClick={() => setConfirmationMessage(false)} >
                    Back
                    </button></>:                    
                    <>{!applicantHistory && <button
                    className={`btn-bottom btn-save btn`}
                      onClick={selectProfile}
                      disabled={isSaveDisabled()}
                    >
                    Select & Save
                    </button>}
                    <button className="btn-bottom btn-cancel" onClick={back} >
                    Back
                    </button></>
                ):
                <><button
                    className={`btn-bottom btn-save btn`}
                    onClick={createProfile}
                >
                Create New Profile
                </button>
                <button className="btn-bottom btn-cancel" onClick={cancel} >
                Cancel
                </button></>
            }
          </DialogActions>
        </ReactModal>
      </div>
    );
  });

export default ApplicantProfileModal;