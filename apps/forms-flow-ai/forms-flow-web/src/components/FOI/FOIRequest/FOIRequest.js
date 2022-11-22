import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Chip from "@mui/material/Chip";
import './foirequest.scss';
import FOIRequestHeader from './FOIRequestHeader';
import ApplicantDetails from './ApplicantDetails';
import ChildDetails from './ChildDetails';
import OnBehalfOfDetails from './OnBehalfOfDetails';
import AddressContactDetails from './AddressContanctInfo';
import RequestDescriptionBox from './RequestDescriptionBox';
import RequestDetails from "./RequestDetails";
import ExtensionDetails from "./ExtensionDetails";
import AdditionalApplicantDetails from './AdditionalApplicantDetails';
import BottomButtonGroup from './BottomButtonGroup';
import { useParams } from 'react-router-dom';
import {
  fetchFOICategoryList,
  fetchFOIProgramAreaList,
  fetchFOIAssignedToList,
  fetchFOIDeliveryModeList,
  fetchFOIReceivedModeList,
  fetchClosingReasonList,
  fetchFOIMinistryAssignedToList,
} from "../../../apiManager/services/FOI/foiMasterDataServices";
import {
  fetchFOIRequestDetailsWrapper,
  fetchFOIRequestDescriptionList,
  fetchRequestDataFromAxis
} from "../../../apiManager/services/FOI/foiRequestServices";
import {
  fetchFOIRequestAttachmentsList
} from "../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRequestNotesList } from "../../../apiManager/services/FOI/foiRequestNoteServices";
import { fetchFOIRecords } from "../../../apiManager/services/FOI/foiRecordServices";
import { makeStyles } from '@material-ui/core/styles';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { push } from "connected-react-router";
import { StateDropDown } from '../customComponents';
import "./TabbedContainer.scss";
import { StateEnum } from '../../../constants/FOI/statusEnum';
import { CommentSection } from '../customComponents/Comments';
import { AttachmentSection } from '../customComponents/Attachments';
import Loading from "../../../containers/Loading";
import clsx from 'clsx';
import { getAssignedTo, getHeaderText } from "./FOIRequestHeader/utils";
import {
  getTabBottomText,
  confirmChangesLost,
  getRedirectAfterSaveUrl,
  getTabBG,
  assignValue,
  createRequestDetailsObjectFunc,
  checkContactGiven,
  getBCgovCode,
  checkValidationError,
  handleBeforeUnload,
  findRequestState,
  isMandatoryField,
  isAxisSyncDisplayField,
  getUniqueIdentifier
} from "./utils";
import { ConditionalComponent, formatDate } from '../../../helper/FOI/helper';
import DivisionalTracking from './DivisionalTracking';
import AxisDetails from './AxisDetails/AxisDetails';
import AxisMessageBanner from "./AxisDetails/AxisMessageBanner";
import HomeIcon from '@mui/icons-material/Home';
import { RecordsLog } from '../customComponents/Records';
import { UnsavedModal } from "../customComponents";

const useStyles = makeStyles((theme) => ({
  root: {
    "& .MuiTextField-root": {
      margin: theme.spacing(1),
    },
  },
  validationErrorMessage: {
    marginTop: "30px",
    color: "#fd0404",
  },
  validationMessage: {
    marginTop: "30px",
    color: "#000000",
  },
  displayed: {
    display: "block",
  },
  hidden: {
    display: "none",
  },
}));

const FOIRequest = React.memo(({ userDetail }) => {

  const [_requestStatus, setRequestStatus] = React.useState(
    StateEnum.unopened.name
  );
  const { requestId, ministryId } = useParams();
  const url = window.location.href;
  const urlIndexCreateRequest = url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST);
  const [isAddRequest, setIsAddRequest] = useState(urlIndexCreateRequest > -1);
  //gets the request detail from the store
  let requestDetails = useSelector(
    (state) => state.foiRequests.foiRequestDetail
  );
  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  let requestExtensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );
  let requestNotes = useSelector(
    (state) => state.foiRequests.foiRequestComments
  );
  let requestAttachments = useSelector(
    (state) => state.foiRequests.foiRequestAttachments
  );
  let requestRecords = useSelector(
    (state) => state.foiRequests.foiRequestRecords
  );
  const [attachments, setAttachments] = useState(requestAttachments);
  const [comment, setComment] = useState([]);
  const [requestState, setRequestState] = useState(StateEnum.unopened.name);
  const disableInput =
    requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase();
  const [_tabStatus, settabStatus] = React.useState(requestState);
  let foitabheaderBG = getTabBG(_tabStatus, requestState);

  const [unsavedPrompt, setUnsavedPrompt] = useState(false);
  const [unsavedMessage, setUnsavedMessage] = useState(<></>);
  const handleUnsavedContinue = () => {
    window.removeEventListener("popstate", handleOnHashChange);
    window.removeEventListener("beforeunload", handleBeforeUnload);
    dispatch(push(`/foi/dashboard`))
  }

  const returnToQueue = (e) => {
    if (unSavedRequest) {
      setUnsavedMessage(<>Are you sure you want to leave? Your changes will be lost.</>)
      setUnsavedPrompt(true)
    } else if (recordsUploading) {
      setUnsavedMessage(<>Are you sure you want to leave? Records are currently in the process of being uploaded.<br/> If you continue they will not be saved.</>)
      setUnsavedPrompt(true)
    } else {
      dispatch(push(`/foi/dashboard`))
    }
  }


  //editorChange and removeComment added to handle Navigate away from Comments tabs
  const [editorChange, setEditorChange] = useState(false);
  const [axisMessage, setAxisMessage] = React.useState("");

  const initialStatuses = {
    Request: {
      display: false,
      active: false,
    },
    Comments: {
      display: false,
      active: false,
    },
    Attachments: {
      display: false,
      active: false,
    },
    Records: {
      display: false,
      active: false,
    },
  };

  const [tabLinksStatuses, setTabLinksStatuses] = useState({
    ...initialStatuses,
    Request: {
      display: true,
      active: true,
    },
  });
  const [removeComment, setRemoveComment] = useState(false);

  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  const showDivisionalTracking =
    requestDetails &&
    requestDetails.divisions?.length > 0 &&
    requestState &&
    requestState.toLowerCase() !== StateEnum.open.name.toLowerCase() &&
    requestState.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase();
  const [axisSyncedData, setAxisSyncedData] = useState({});
  const [checkExtension, setCheckExtension] = useState(true);
  let bcgovcode = getBCgovCode(ministryId, requestDetails);
  const [headerText, setHeaderText]  = useState(getHeaderText({requestDetails, ministryId, requestState}));  
  document.title = requestDetails.axisRequestId || requestDetails.idNumber || headerText;

  useEffect(() => {
    if (window.location.href.indexOf("comments") > -1) {
      tabclick("Comments");
    }
  }, []);

  const dispatch = useDispatch();
  useEffect(() => {
    if (isAddRequest) {
      dispatch(fetchFOIAssignedToList("", "", ""));
    } else {
      dispatch(fetchFOIRequestDetailsWrapper(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
      dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
      dispatch(fetchFOIRecords(requestId, ministryId));
    }

    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
    dispatch(fetchClosingReasonList());

    if (bcgovcode) dispatch(fetchFOIMinistryAssignedToList(bcgovcode));
  }, [requestId, ministryId, comment, attachments]);

  useEffect(() => {
    const requestDetailsValue = requestDetails;
    setSaveRequestObject(requestDetailsValue);
    const assignedTo = getAssignedTo(requestDetails);
    setAssignedToValue(assignedTo);
    if (Object.entries(requestDetails)?.length !== 0) {
      let requestStateFromId = findRequestState(requestDetails.requeststatusid)
        ? findRequestState(requestDetails.requeststatusid)
        : StateEnum.unopened.name;
      setRequestState(requestStateFromId);
      settabStatus(requestStateFromId);
      setcurrentrequestStatus(requestStateFromId);
      setHeaderText(getHeaderText({requestDetails, ministryId, requestState}));
      if(requestDetails.axisRequestId)
        axisBannerCheck();
    }
  }, [requestDetails]);


  useEffect(() => {
    if(checkExtension && Object.entries(axisSyncedData).length !== 0){
      let axisDataUpdated = extensionComparison(axisSyncedData, 'Extensions');
      if(axisDataUpdated)
        setAxisMessage("WARNING");
      else
        setAxisMessage("");
    }
  }, [axisSyncedData, requestExtensions, checkExtension]);
  

  const axisBannerCheck = () =>{
    dispatch(fetchRequestDataFromAxis(requestDetails.axisRequestId, saveRequestObject ,true, (err, data) => {
      if(!err){
        if(typeof(data) !== "string" && Object.entries(data).length > 0){
          setAxisSyncedData(data);
          let axisDataUpdated = checkIfAxisDataUpdated(data);
          if(axisDataUpdated){
            setCheckExtension(false);
            setAxisMessage("WARNING");
          }
          else{
            setAxisMessage("");
          }
        }
        else if(data){
          let responseMsg = data;
          responseMsg+='';
          if(responseMsg.indexOf("Exception happened while GET operations of request") >= 0)
            setAxisMessage("ERROR");
        }
      }
      else{
        setAxisMessage("ERROR");
      }
    }));
  }

  const checkIfAxisDataUpdated = (axisData) => {
    let updateNeeded= false;
    for(let key of Object.keys(axisData)){
      let updatedField = isAxisSyncDisplayField(key);
      if(key !== 'Extensions' && updatedField)
        updateNeeded= checkValidation(key, axisData);
      if(updateNeeded){
        return true;
      }
    }
    return false;
  };

  const checkValidation = (key,axisData) => {
    let mandatoryField = isMandatoryField(key);
    if(key === 'additionalPersonalInfo'){
      if(axisData.requestType === 'personal'){
        let foiReqAdditionalPersonalInfo = requestDetails[key];
        let axisAdditionalPersonalInfo = axisData[key];
        for(let axisKey of Object.keys(axisAdditionalPersonalInfo)){
          for(let reqKey of Object.keys(foiReqAdditionalPersonalInfo)){
            if(axisKey === reqKey){
              if(axisAdditionalPersonalInfo[axisKey] !== foiReqAdditionalPersonalInfo[axisKey] ){
                return true;
              }
            }
          }
        }
      }
    }
    else if(key === 'compareReceivedDate' && 
        (requestDetails['receivedDate'] !== axisData[key] && requestDetails['receivedDate'] !== axisData['receivedDate'])){
        return true;
    }
    else if(key !== 'compareReceivedDate' && (mandatoryField && axisData[key] || !mandatoryField)){
      if((requestDetails[key] || axisData[key]) && requestDetails[key] != axisData[key])
        return true;
    }
    return false;
  }

  const extensionComparison = (axisData, key) => {
    if(requestExtensions.length !== axisData[key].length)
        return true;
    let axisUniqueIds = [];
    let foiUniqueIds = [];
    axisData[key]?.forEach(axisObj => {
      axisUniqueIds.push((axisObj.extensionstatusid+formatDate(axisObj.extendedduedate, "MMM dd yyyy")+
      axisObj.extensionreasonid).replace(/\s+/g, ''));
    })
    requestExtensions.forEach(obj => {
      foiUniqueIds.push((obj.extensionstatusid+formatDate(obj.extendedduedate, "MMM dd yyyy")+
      obj.extensionreasonid).replace(/\s+/g, ''));
    })
    if(axisUniqueIds.filter(x => !foiUniqueIds.includes(x))?.length > 0){
      return true;
    }
      
    if(requestExtensions.length > 0 && axisData[key].length > 0){
      for(let axisObj of axisData[key]){
        for(let foiReqObj of requestExtensions){
          if(getUniqueIdentifier(axisObj) === getUniqueIdentifier(foiReqObj)){
            if(axisObj.extensionstatusid !== foiReqObj.extensionstatusid ||
              axisObj.extendedduedays  !== foiReqObj.extendedduedays ||
              !(foiReqObj.decisiondate === axisObj.approveddate || foiReqObj.decisiondate === axisObj.denieddate)){
                return true;
            }
          }
        }
      }
    }
    else{
      if(axisData[key]?.length > 0)
        return true;
    }
   return false;
  }


  const requiredRequestDescriptionDefaultData = {
    startDate: "",
    endDate: "",
    description: "",
    isProgramAreaSelected: false,
    ispiiredacted: false,
  };

  const requiredRequestDetailsInitialValues = {
    requestType: "",
    receivedMode: "",
    deliveryMode: "",
    receivedDate: "",
    requestStartDate: "",
    dueDate: "",
  };

  const requiredApplicantDetailsValues = {
    firstName: "",
    lastName: "",
    email: "",
    category: "",
  };

  const requiredContactDetailsValue = {
    address: "",
    city: "",
    province: "",
    country: "",
    postal: "",
  };

  const requiredAxisDetailsValue = {
    axisRequestId: "",
  };

  //below states are used to find if required fields are set or not
  const [
    requiredRequestDescriptionValues,
    setRequiredRequestDescriptionValues,
  ] = React.useState(requiredRequestDescriptionDefaultData);
  const [requiredRequestDetailsValues, setRequiredRequestDetailsValues] =
    React.useState(requiredRequestDetailsInitialValues);

  const [assignedToValue, setAssignedToValue] = React.useState("Unassigned");
  const [requiredApplicantDetails, setRequiredApplicantDetails] =
    React.useState(requiredApplicantDetailsValues);
  const [requiredContactDetails, setrequiredContactDetails] = React.useState(
    requiredContactDetailsValue
  );
  const [unSavedRequest, setUnSavedRequest] = React.useState(false);
  const [recordsUploading, setRecordsUploading] = React.useState(false);
  const [headerValue, setHeader] = useState("");
  const [requiredAxisDetails, setRequiredAxisDetails] = React.useState(
    requiredAxisDetailsValue
  );
  //get the initial value of the required fields to enable/disable bottom button at the initial load of review request
  const handleInitialRequiredRequestDescriptionValues = React.useCallback(
    (requestDescriptionObject) => {
      setRequiredRequestDescriptionValues(requestDescriptionObject);
    },
    []
  );
  const handleRequestDetailsInitialValue = React.useCallback((value) => {
    setRequiredRequestDetailsValues(value);
  }, []);
  const handleApplicantDetailsInitialValue = React.useCallback((value) => {
    setRequiredApplicantDetails(value);
  }, []);
  const handleContactDetailsInitialValue = React.useCallback((value) => {
    setrequiredContactDetails(value);
  }, []);
  const handleAxisDetailsInitialValue = React.useCallback((value) => {
    setRequiredAxisDetails(value);
  }, []);

  const handleApplicantDetailsValue = (value, name) => {
    const detailsData = assignValue(requiredApplicantDetails, value, name);
    setRequiredApplicantDetails(detailsData);
  };
  const handleContanctDetailsValue = (value, name) => {
    const detailsData = assignValue(requiredContactDetails, value, name);
    setrequiredContactDetails(detailsData);
  };
  const handleAxisDetailsValue = (value, name) => {
    if (value) setUnSavedRequest(true);
    const detailsData = assignValue(requiredAxisDetailsValue, value, name);
    setRequiredAxisDetails(detailsData);
  };
  //Update required fields of request description box with latest value
  const handleOnChangeRequiredRequestDescriptionValues = (value, name) => {
    const descriptionData = assignValue(
      requiredRequestDescriptionValues,
      value,
      name
    );
    setRequiredRequestDescriptionValues(descriptionData);
  };
  //Update required fields of request details box with latest value
  const handleRequestDetailsValue = (value, name, value2) => {
    const detailsData = assignValue(requiredRequestDetailsValues, value, name);
    if (value2) {
      detailsData.dueDate = value2;
    }
    setRequiredRequestDetailsValues(detailsData);
  };
  //gets the latest assigned to value
  const handleAssignedToValue = (value) => {
    setAssignedToValue(value);
  };

  //handle email validation
  const [validation, setValidation] = React.useState({});
  const handleEmailValidation = (validationObj) => {
    setValidation(validationObj);
  };
  const handleAxisIdValidation = (validationObj) => {
    setValidation(validationObj);
  };

  //to get the updated program area list with isChecked=true/false
  const [programAreaList, setProgramAreaList] = React.useState([]);

  const handleUpdatedProgramAreaList = (_programAreaList) => {
    //get the updated program area list with isChecked=true/false
    setProgramAreaList(_programAreaList);
  };

  const contactDetailsNotGiven = checkContactGiven(requiredContactDetails);

  //Variable to find if all required fields are filled or not
  const isValidationError = checkValidationError(
    requiredApplicantDetails,
    contactDetailsNotGiven,
    requiredRequestDescriptionValues,
    validation,
    assignedToValue,
    requiredRequestDetailsValues,
    requiredAxisDetails
  );

  const classes = useStyles();

  const createRequestDetailsObject = (requestObject, name, value, value2) => {
    return createRequestDetailsObjectFunc(
      requestObject,
      requiredRequestDetailsValues,
      requestId,
      name,
      value,
      value2
    );
  };

  const createSaveRequestObject = (name, value, value2) => {
    let requestObject = { ...saveRequestObject };
    if(name !== 'assignedTo'){
      setUnSavedRequest(
        name !== FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES
      );  
    }

    requestObject = createRequestDetailsObject(
      requestObject,
      name,
      value,
      value2
    );
    setSaveRequestObject(requestObject);
  };
  const [updateStateDropDown, setUpdateStateDropdown] = useState(false);
  const [stateChanged, setStateChanged] = useState(false);

  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);

    if (!_unSaved) {
      setUnSavedRequest(_unSaved);
      dispatch(fetchFOIRequestDetailsWrapper(id || requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(id || requestId, ministryId));
      setStateChanged(false);
      setcurrentrequestStatus(_state);
      setTimeout(() => {
        dispatch(push(getRedirectAfterSaveUrl(ministryId, id || requestId)));
        dispatch(fetchFOIRequestNotesList(id || requestId, ministryId));
      }, 1000);
    } else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(_state);
      setStateChanged(false);
    }
  };

  const handleOpenRequest = (parendId, _ministryId, unSaved) => {
    if (!unSaved) {
      setUnSavedRequest(unSaved);
      setStateChanged(false);
      setcurrentrequestStatus(StateEnum.open.name);

      dispatch(
        push(`/foi/foirequests/${parendId}/ministryrequest/${_ministryId}`)
      );
    } else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(requestState); // should be revisited
      setStateChanged(false);
    }
  };

  const handleStateChange = (currentStatus) => {
    setcurrentrequestStatus(currentStatus);
    setStateChanged(true);
  };

  const handlestatusudpate = (_daysRemaining, _status, _cfrDaysRemaining) => {

    const mappedBottomText = getTabBottomText({
      _daysRemaining,
      _cfrDaysRemaining,
      _status,
      requestExtensions,
    });

    setRequestStatus(mappedBottomText);
  };

  const hasStatusRequestSaved = (state) => {
    settabStatus(state);
    setcurrentrequestStatus("");
  };

  //Below function will handle popstate event
  const handleOnHashChange = (e) => {
    e.preventDefault();
  };

  React.useEffect(() => {
    if (editorChange) {
      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener("popstate", handleOnHashChange);
      window.addEventListener("beforeunload", handleBeforeUnload);
      return () => {
        window.removeEventListener("popstate", handleOnHashChange);
        window.removeEventListener("beforeunload", handleBeforeUnload);
      };
    }
  }, [editorChange]);

  const tabclick = (param) => {
    if (param === "Comments") {
      sessionStorage.setItem('foicommentcategory',1) 
      setRemoveComment(false);
      changeTabLinkStatuses(param);
      return;
    }

    if (editorChange) {
      confirmChangesLost(
        () => {
          setEditorChange(false);
          setRemoveComment(true);
          changeTabLinkStatuses(param);
        },
        () => {
          setEditorChange(true);
          setRemoveComment(false);
        }
      );
    } else {
      changeTabLinkStatuses(param);
    }
  };

  const changeTabLinkStatuses = (param) => {
    setTabLinksStatuses({
      ...initialStatuses,
      [param]: {
        ...tabLinksStatuses[param],
        active: true,
        display: true,
      },
    });
  };

  const bottomTextArray = _requestStatus.split("|");

  const userId = userDetail?.preferred_username;
  const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random";
  let lastName = "",
    firstName = "";
  if (userDetail) {
    firstName = userDetail.given_name;
    lastName = userDetail.family_name;
  }
  const fullName = `${lastName}, ${firstName}`;
  const signinUrl = "/signin";
  const signupUrl = "/signup";

  const requestNumber = requestDetails?.axisRequestId
    ? requestDetails.axisRequestId
    : requestDetails?.idNumber;

  let iaoassignedToList = useSelector(
    (state) => state.foiRequests.foiFullAssignedToList
  );
  let ministryAssignedToList = useSelector(
    (state) => state.foiRequests.foiMinistryAssignedToList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);
  const isAttachmentListLoading = useSelector(
    (state) => state.foiRequests.isAttachmentListLoading
  );

  const stateTransition = requestDetails?.stateTransition;
  
  const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch)

  const showRecordsTab = () => {
    return (requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      requestDetails?.divisions?.length > 0
    );
  }

  const disableBannerForClosed = () => {
   if(stateTransition?.find( ({ status }) => status?.toLowerCase() === StateEnum.intakeinprogress.name.toLowerCase())){
      if(axisMessage === "WARNING")
        setAxisMessage("");
      return true;
    }
    return false;
  }

  return (!isLoading &&
    requestDetails &&
    Object.keys(requestDetails).length !== 0) ||
    isAddRequest ? (
    <div className={`foiformcontent ${axisMessage === "WARNING" && !disableBannerForClosed() && 'request-scrollbar-height'}`}>
      <div className="foitabbedContainer">
        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <i aria-label="dashboard link" onClick={returnToQueue} className='fa fa-home' style={{fontSize:"45px", color: "white", cursor: "pointer"}}></i>           
          </div>
          <h4 className="foileftpanelrequestno">{headerText}</h4>
          <div className="foileftpaneldropdown">
            <StateDropDown
              requestState={requestState}
              updateStateDropDown={updateStateDropDown}
              stateTransition={stateTransition}
              requestStatus={_requestStatus}
              handleStateChange={handleStateChange}
              isMinistryCoordinator={false}
              isValidationError={isValidationError}
              requestType={requestDetails?.requestType}
            />
          </div>

          <div className="tab">
            <div
              className={clsx("tablinks", {
                active: tabLinksStatuses.Request.active,
              })}
              name="Request"
              onClick={() => tabclick("Request")}
            >
              Request
            </div>
            {!isAddRequest && (
              <>
                <div
                  className={clsx("tablinks", {
                    active: tabLinksStatuses.Attachments.active,
                  })}
                  name="Attachments"
                  onClick={() => tabclick("Attachments")}
                >
                  Attachments{" "}
                  {requestAttachments?.length > 0
                    ? `(${requestAttachments.length})`
                    : ""}
                </div>
                <div
                  className={clsx("tablinks", {
                    active: tabLinksStatuses.Comments.active,
                  })}
                  name="Comments"
                  onClick={() => tabclick("Comments")}
                >
                  Comments{" "}
                  {requestNotes?.length > 0 ? `(${requestNotes.length})` : ""}
                </div>
                {showRecordsTab() && <div
                  className={clsx("tablinks", {
                    active: tabLinksStatuses.Records.active,
                  })}
                  name="Records"
                  onClick={() => tabclick("Records")}
                >
                  Records
                </div>}
              </>
            )}
          </div>

          <div className="foileftpanelstatus">
            {bottomTextArray.length > 0 &&
              _requestStatus &&
              _requestStatus.toLowerCase().includes("days") &&
              bottomTextArray.map((text) => {
                return <div className='remaining-days-alert'>{text}</div>;
              })}
          </div>
        </div>
        <div className="foitabpanelcollection">
        { requestState !== StateEnum.intakeinprogress.name && !disableBannerForClosed() &&
          <AxisMessageBanner axisMessage= {axisMessage} requestDetails={requestDetails}/>
        }
          <div
            id="Request"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Request.active,
              [classes.displayed]: tabLinksStatuses.Request.display,
              [classes.hidden]: !tabLinksStatuses.Request.display,
            })}
          >
            <div className="container foi-review-request-container">
              <div className="foi-review-container">
                <form
                  className={`${classes.root} foi-request-form`}
                  autoComplete="off"
                >
                  <ConditionalComponent
                    condition={
                      Object.entries(requestDetails).length !== 0 ||
                      isAddRequest
                    }
                  >
                    <Breadcrumbs aria-label="breadcrumb" className="foi-breadcrumb">
                      {showAdvancedSearch &&
                        <Chip
                          label={"Advanced Search"}
                          sx={{ backgroundColor: '#fff', border:'1px solid #038', color: '#038', height: 19, cursor: 'pointer' }}
                          onClick={returnToQueue}
                        />
                      }
                      {!showAdvancedSearch &&
                        <Chip
                          icon={<HomeIcon fontSize="small" sx={{color: '#038 !important'}}/>}
                          label={"Request Queue"}
                          sx={{ backgroundColor: '#fff', border:'1px solid #038', color: '#038', height: 19, cursor: 'pointer' }}
                          onClick={returnToQueue}
                        />
                      }
                      <Chip
                        label={headerText}
                        sx={{ backgroundColor: '#fff', border:'1px solid #038', color: '#038', height: 19 }}
                      />
                    </Breadcrumbs>
                    <>
                      <FOIRequestHeader
                        headerValue={headerValue}
                        headerText={headerText}
                        requestDetails={requestDetails}
                        handleAssignedToValue={handleAssignedToValue}
                        createSaveRequestObject={createSaveRequestObject}
                        handlestatusudpate={handlestatusudpate}
                        userDetail={userDetail}
                        disableInput={disableInput}
                        isAddRequest={isAddRequest}
                      />
                      {(isAddRequest ||
                        requestState === StateEnum.unopened.name) && (
                        <AxisDetails
                          requestDetails={requestDetails}
                          createSaveRequestObject={createSaveRequestObject}
                          handleAxisDetailsInitialValue={
                            handleAxisDetailsInitialValue
                          }
                          handleAxisDetailsValue={handleAxisDetailsValue}
                          handleAxisIdValidation={handleAxisIdValidation}
                          setAxisMessage={setAxisMessage}
                          saveRequestObject={saveRequestObject}
                        />
                      )}
                      <ApplicantDetails
                        requestDetails={requestDetails}
                        requestStatus={_requestStatus}
                        contactDetailsNotGiven={contactDetailsNotGiven}
                        handleApplicantDetailsInitialValue={
                          handleApplicantDetailsInitialValue
                        }
                        handleApplicantDetailsValue={
                          handleApplicantDetailsValue
                        }
                        createSaveRequestObject={createSaveRequestObject}
                        disableInput={disableInput}
                        userDetail={userDetail}
                      />
                      {requiredRequestDetailsValues.requestType.toLowerCase() ===
                        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL && (
                        <>
                          <ChildDetails
                            additionalInfo={
                              requestDetails.additionalPersonalInfo
                            }
                            createSaveRequestObject={createSaveRequestObject}
                            disableInput={disableInput}
                            userDetail={userDetail}
                            requestType={
                              requestDetails?.requestType
                            }                          />
                          <OnBehalfOfDetails
                            additionalInfo={
                              requestDetails.additionalPersonalInfo
                            }
                            createSaveRequestObject={createSaveRequestObject}
                            disableInput={disableInput}
                          />
                        </>
                      )}

                      <AddressContactDetails
                        requestDetails={requestDetails}
                        contactDetailsNotGiven={contactDetailsNotGiven}
                        createSaveRequestObject={createSaveRequestObject}
                        handleContactDetailsInitialValue={
                          handleContactDetailsInitialValue
                        }
                        handleContanctDetailsValue={handleContanctDetailsValue}
                        disableInput={disableInput}
                        handleEmailValidation={handleEmailValidation}
                        userDetail={userDetail}
                      />

                      <RequestDescriptionBox
                        programAreaList={programAreaList}
                        urlIndexCreateRequest={urlIndexCreateRequest}
                        requestDetails={requestDetails}
                        requiredRequestDetailsValues={
                          requiredRequestDetailsValues
                        }
                        handleUpdatedProgramAreaList={
                          handleUpdatedProgramAreaList
                        }
                        handleOnChangeRequiredRequestDescriptionValues={
                          handleOnChangeRequiredRequestDescriptionValues
                        }
                        handleInitialRequiredRequestDescriptionValues={
                          handleInitialRequiredRequestDescriptionValues
                        }
                        createSaveRequestObject={createSaveRequestObject}
                        disableInput={disableInput}
                      />
                      <RequestDetails
                        requestDetails={requestDetails}
                        requestStatus={_requestStatus}
                        handleRequestDetailsValue={handleRequestDetailsValue}
                        handleRequestDetailsInitialValue={
                          handleRequestDetailsInitialValue
                        }
                        createSaveRequestObject={createSaveRequestObject}
                        disableInput={disableInput}
                      />

                      <ExtensionDetails
                        requestDetails={requestDetails}
                        requestState={requestState}
                      />
                      {requiredRequestDetailsValues.requestType.toLowerCase() ===
                        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL && (
                        <AdditionalApplicantDetails
                          requestDetails={requestDetails}
                          createSaveRequestObject={createSaveRequestObject}
                          disableInput={disableInput}
                        />
                      )}
                      {showDivisionalTracking && (
                        <DivisionalTracking
                          divisions={requestDetails.divisions}
                        />
                      )}

                      <BottomButtonGroup
                        stateChanged={stateChanged}
                        isValidationError={isValidationError}
                        urlIndexCreateRequest={urlIndexCreateRequest}
                        saveRequestObject={saveRequestObject}
                        unSavedRequest={unSavedRequest}
                        recordsUploading={recordsUploading}
                        handleSaveRequest={handleSaveRequest}
                        handleOpenRequest={handleOpenRequest}
                        currentSelectedStatus={_currentrequestStatus}
                        hasStatusRequestSaved={hasStatusRequestSaved}
                        disableInput={disableInput}
                        requestState={requestState}
                        setSaveRequestObject={setSaveRequestObject}
                        setIsAddRequest={setIsAddRequest}
                        axisSyncedData={axisSyncedData}
                        axisMessage={axisMessage}
                      />
                    </>
                  </ConditionalComponent>
                </form>
              </div>
            </div>
          </div>
          <div
            id="Attachments"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Attachments.active,
              [classes.displayed]: tabLinksStatuses.Attachments.display,
              [classes.hidden]: !tabLinksStatuses.Attachments.display,
            })}
          >
            {!isAttachmentListLoading &&
            (iaoassignedToList?.length > 0 ||
              ministryAssignedToList?.length > 0) ? (
              <>
                <AttachmentSection
                  currentUser={userId}
                  attachmentsArray={requestAttachments}
                  setAttachments={setAttachments}
                  requestId={requestId}
                  ministryId={ministryId}
                  requestNumber={requestNumber}
                  requestState={requestState}
                  iaoassignedToList={iaoassignedToList}
                  ministryAssignedToList={ministryAssignedToList}
                  isMinistryCoordinator={false}
                />
              </>
            ) : (
              <Loading />
            )}
          </div>
          <div
            id="Comments"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Comments.active,
              [classes.displayed]: tabLinksStatuses.Comments.display,
              [classes.hidden]: !tabLinksStatuses.Comments.display,
            })}
          >
            {!isLoading &&
            requestNotes &&
            (iaoassignedToList?.length > 0 ||
              ministryAssignedToList?.length > 0) ? (
              <>
                <CommentSection
                  currentUser={
                    userId && {
                      userId: userId,
                      avatarUrl: avatarUrl,
                      name: fullName,
                    }
                  }
                  commentsArray={requestNotes.sort(function (a, b) {
                    return b.commentId - a.commentId;
                  })}
                  setComment={setComment}
                  signinUrl={signinUrl}
                  signupUrl={signupUrl}
                  requestid={requestId}
                  ministryId={ministryId}
                  bcgovcode={bcgovcode}
                  iaoassignedToList={iaoassignedToList}
                  ministryAssignedToList={ministryAssignedToList}
                  requestNumber={requestNumber}
                  //setEditorChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs
                  setEditorChange={setEditorChange}
                  removeComment={removeComment}
                  setRemoveComment={setRemoveComment}
                />
              </>
            ) : (
              <Loading />
            )}
          </div>
          <div
            id="Records"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Records.active,
              [classes.displayed]: tabLinksStatuses.Records.display,
              [classes.hidden]: !tabLinksStatuses.Records.display,
            })}
          >
            {showRecordsTab() && !isAttachmentListLoading &&
            (iaoassignedToList?.length > 0 ||
              ministryAssignedToList?.length > 0) ? (
              <>
                <RecordsLog
                  recordsArray={requestRecords}
                  requestId={requestId}
                  ministryId={ministryId}
                  requestNumber={requestNumber}
                  iaoassignedToList={iaoassignedToList}
                  ministryAssignedToList={ministryAssignedToList}
                  isMinistryCoordinator={false}
                  bcgovcode={bcgovcode}
                  setRecordsUploading={setRecordsUploading}
                  divisions={requestDetails.divisions}
                />
              </>
            ) : (
              <Loading />
            )}
          </div>
          <UnsavedModal
            modalOpen={unsavedPrompt}
            handleClose={() => setUnsavedPrompt(false)}
            handleContinue={handleUnsavedContinue}
            modalMessage={unsavedMessage}
          />
        </div>
      </div>
    </div>
  ) : (
    <Loading />
  );
});

export default FOIRequest;
