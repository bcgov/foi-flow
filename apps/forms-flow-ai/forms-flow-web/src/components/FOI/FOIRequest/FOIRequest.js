import React, { useEffect, useState }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import './foirequest.scss';
import FOIRequestHeader from './FOIRequestHeader';
import ApplicantDetails from './ApplicantDetails';
import ChildDetails from './ChildDetails';
import OnBehalfOfDetails from './OnBehalfOfDetails';
import AddressContactDetails from './AddressContanctInfo';
import RequestDescriptionBox from './RequestDescriptionBox';
import RequestDetails from './RequestDetails';
import AdditionalApplicantDetails from './AdditionalApplicantDetails';
import RequestNotes from './RequestNotes';
import BottomButtonGroup from './BottomButtonGroup';
import { useParams } from 'react-router-dom';
import {
  fetchFOIRawRequestDetails,
  fetchFOIRequestDetails, 
  fetchFOICategoryList, 
  fetchFOIProgramAreaList, 
  fetchFOIAssignedToList, 
  fetchFOIDeliveryModeList, 
  fetchFOIReceivedModeList,
  fetchFOIRequestDescriptionList,
  fetchClosingReasonList,
  fetchFOIRequestNotesList,
  fetchFOIFullAssignedToList,
  fetchFOIMinistryAssignedToList
    
} from "../../../apiManager/services/FOI/foiRequestServices";
import { makeStyles } from '@material-ui/core/styles';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { formatDate } from "../../../helper/FOI/helper";
import {push} from "connected-react-router";

import PropTypes from 'prop-types';

import Typography from '@material-ui/core/Typography';
import { StateDropDown } from '../customComponents';
import "./TabbedContainer.scss";
import { StateEnum } from '../../../constants/FOI/statusEnum';
import {CommentSection} from '../customComponents/Comments'
import Loading from "../../../containers/Loading";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),  
    },    
  },
  validationErrorMessage: {
    marginTop:'30px',
    color: "#fd0404",
  },
  validationMessage: {
    marginTop:'30px',
    color: "#000000",
  },
 
}));

const FOIRequest = React.memo(({userDetail}) => {
  const [_requestStatus, setRequestStatus] = React.useState(StateEnum.unopened.name);
  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  

  var foitabheaderBG;


  const {requestId, ministryId, requestState} = useParams();
  const disableInput = requestState && requestState.toLowerCase() === StateEnum.closed.name.toLowerCase();

  const [_tabStatus, settabStatus] = React.useState(requestState);
  
  const url = window.location.href;
  const urlIndexCreateRequest = url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST);
  //gets the request detail from the store
  let requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
  let requestNotes = useSelector(state=> state.foiRequests.foiRequestComments) ;   
  const [comment, setComment] = useState([])
  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  let bcgovcode = ministryId && requestDetails && requestDetails["selectedMinistries"] ?JSON.stringify(requestDetails["selectedMinistries"][0]["code"]):""
  const dispatch = useDispatch();
  useEffect(() => {      
    if (ministryId) {
      dispatch(fetchFOIRequestDetails(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
      dispatch(fetchFOIRequestNotesList(requestId,ministryId));
    
    }
    else if (url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) === -1) {      
      dispatch(fetchFOIRawRequestDetails(requestId));
      dispatch(fetchFOIRequestNotesList(requestId,null));
      dispatch(fetchFOIRequestDescriptionList(requestId, ""));
    }
    else if (url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1) {
      dispatch(fetchFOIAssignedToList(urlIndexCreateRequest,"",""));
    }
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
    dispatch(fetchClosingReasonList());
    if (bcgovcode)
      dispatch(fetchFOIMinistryAssignedToList(bcgovcode));          
  },[requestId,ministryId, dispatch,comment]);
 

  useEffect(() => {  
    const requestDetailsValue = url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1 ? {} : requestDetails;
    setSaveRequestObject(requestDetailsValue); 
    let assignedTo = requestDetails.assignedTo ? (requestDetails.assignedGroup && requestDetails.assignedGroup !== "Unassigned" ? `${requestDetails.assignedGroup}|${requestDetails.assignedTo}` : "|Unassigned") : (requestDetails.assignedGroup ? `${requestDetails.assignedGroup}|${requestDetails.assignedGroup}`: "|Unassigned");
    setAssignedToValue(assignedTo);
  },[requestDetails]);
  
  const requiredRequestDescriptionDefaultData = {
    startDate: "",
    endDate: "",
    description: "",
    isProgramAreaSelected: false,
    isPiiRedacted: false
  }  

  const requiredRequestDetailsInitialValues = {
    requestType:"",
    receivedMode: "",
    deliveryMode: "",
    receivedDate: "",
    requestStartDate: "",
    dueDate: "",
  }

  const requiredApplicantDetailsValues = {
    firstName: "",
    lastName: "",
    email: "",
    category: "",
  }

  const requiredContactDetailsValue = {
   primaryAddress: "",  
   city: "",
   province: "",
   country: "",
   postalCode: "",
  }
  
  //below states are used to find if required fields are set or not
  const [requiredRequestDescriptionValues, setRequiredRequestDescriptionValues] = React.useState(requiredRequestDescriptionDefaultData);
  const [requiredRequestDetailsValues, setRequiredRequestDetailsValues] = React.useState(requiredRequestDetailsInitialValues);  
 
  const [assignedToValue, setAssignedToValue] = React.useState("Unassigned");
  const [requiredApplicantDetails, setRequiredApplicantDetails] = React.useState(requiredApplicantDetailsValues);
  const [requiredContactDetails, setrequiredContactDetails] = React.useState(requiredContactDetailsValue);
  const [unSavedRequest, setUnSavedRequest] = React.useState(false);
  const [headerValue, setHeader] = useState("");

  //get the initial value of the required fields to enable/disable bottom button at the initial load of review request
  const handleInitialRequiredRequestDescriptionValues = React.useCallback((requestDescriptionObject) => {
    setRequiredRequestDescriptionValues(requestDescriptionObject);
  },[])
  const handleRequestDetailsInitialValue = React.useCallback((value) => {
    setRequiredRequestDetailsValues(value);
  },[])
  const handleAssignedToInitialValue = React.useCallback((value) => {    
    setAssignedToValue(value);
  },[]) 
  const handleApplicantDetailsInitialValue = React.useCallback((value) => {    
    setRequiredApplicantDetails(value);
  },[])
  const handleContactDetailsInitialValue = React.useCallback((value) => {    
    setrequiredContactDetails(value);
  },[])

  const handleApplicantDetailsValue = (value, name) => {
    const detailsData = {...requiredApplicantDetails};
    if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME) {
      detailsData.firstName = value;
    }    
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME) {
        detailsData.lastName = value;
    }    
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL) {
        detailsData.email = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.FOI_CATEGORY) {
      detailsData.category = value
    }
    setRequiredApplicantDetails(detailsData);
  }

  const handleContanctDetailsValue = (value, name) => {
    const detailsData = {...requiredContactDetails};
    if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) {
      detailsData.primaryAddress = value;
    } 
    else if (name === FOI_COMPONENT_CONSTANTS.CITY) {
        detailsData.city = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.PROVINCE) {
      detailsData.province = value
    }
    else if (name === FOI_COMPONENT_CONSTANTS.COUNTRY) {
      detailsData.country = value
    }
    else if (name === FOI_COMPONENT_CONSTANTS.POSTALCODE) {
      detailsData.postalCode = value
    }
    setrequiredContactDetails(detailsData);
  }

  //Update required fields of request description box with latest value
  const handleOnChangeRequiredRequestDescriptionValues = (value, name) => {
    const descriptionData = {...requiredRequestDescriptionValues};
    if(name === FOI_COMPONENT_CONSTANTS.START_DATE) {      
      descriptionData.startDate = value;      
    }    
    else if(name === FOI_COMPONENT_CONSTANTS.END_DATE) {    
      descriptionData.endDate = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.DESCRIPTION) {     
      descriptionData.description = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED) {
      descriptionData.isProgramAreaSelected = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.ISPIIREDACTED) {
      descriptionData.isPiiRedacted = value;
    }
    
    setRequiredRequestDescriptionValues(descriptionData);
  }
  
  //Update required fields of request details box with latest value
  const handleRequestDetailsValue = (value, name, value2) => {    
    const detailsData = {...requiredRequestDetailsValues};
    if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {      
      detailsData.requestType = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
      detailsData.receivedMode = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
      detailsData.deliveryMode = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE) {
      detailsData.receivedDate = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
      detailsData.requestStartDate = value;
      detailsData.dueDate = value2;   
    }
    setRequiredRequestDetailsValues(detailsData);
  }

  //gets the latest assigned to value
  const handleAssignedToValue = (value) => {   
    setAssignedToValue(value);
  }

  //handle email validation
  const [validation, setValidation] = React.useState({});
  const handleEmailValidation = (validationObj) => {    
    setValidation(validationObj);
  }

  //to get the updated program area list with isChecked=true/false
  const [programAreaList, setProgramAreaList] = React.useState([]);
  
  const handleUpdatedProgramAreaList = (programAreaList) => {    
    //get the updated program area list with isChecked=true/false
    setProgramAreaList(programAreaList); 
  } 

  const contactDetailsNotGiven = ((requiredContactDetails.primaryAddress === "" || requiredContactDetails.city === "" || requiredContactDetails.province === "" || requiredContactDetails.country === "" || requiredContactDetails.postalCode === "" ) && requiredApplicantDetails.email === "");

  //Variable to find if all required fields are filled or not
  const isValidationError = (
    requiredApplicantDetails.firstName === "" || requiredApplicantDetails.lastName === "" 
    || requiredApplicantDetails.category.toLowerCase().includes("select")
    || contactDetailsNotGiven
    || requiredRequestDescriptionValues.description === ""
    || !requiredRequestDescriptionValues.isProgramAreaSelected
    || !requiredRequestDescriptionValues.isPiiRedacted
    || (validation.helperTextValue !== undefined && validation.helperTextValue !== "")
    || assignedToValue.toLowerCase().includes("unassigned")
    || requiredRequestDetailsValues.requestType.toLowerCase().includes("select")
    || requiredRequestDetailsValues.receivedMode.toLowerCase().includes("select")
    || requiredRequestDetailsValues.deliveryMode.toLowerCase().includes("select")
    || (requiredRequestDetailsValues.receivedDate === undefined || requiredRequestDetailsValues.receivedDate === "")
    || (requiredRequestDetailsValues.requestStartDate === undefined || requiredRequestDetailsValues.requestStartDate === "")
    );

  const classes = useStyles();
 

  const updateAdditionalInfo = (name, value, requestObject) => {
    if (requestObject.additionalPersonalInfo === undefined) {
      requestObject.additionalPersonalInfo = {
           alsoKnownAs:"",            
           birthDate:"",
           childFirstName:"",
           childMiddleName:"",
           childLastName:"",
           childAlsoKnownAs:"",
           childBirthDate:"",
           anotherFirstName:"",
           anotherMiddleName:"",
           anotherLastName:"",
           anotherAlsoKnownAs:"",
           anotherBirthDate:"",
           adoptiveMotherFirstName:"",
           adoptiveMotherLastName:"",
           adoptiveFatherLastName:"",
           adoptiveFatherFirstName:"",
           personalHealthNumber:"",
           identityVerified:"",
        };
    }
    else {
      if (name === FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME) {
        requestObject.additionalPersonalInfo.childFirstName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME) {
        requestObject.additionalPersonalInfo.childMiddleName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME) {
        requestObject.additionalPersonalInfo.childLastName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME) {
        requestObject.additionalPersonalInfo.childAlsoKnownAs = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_DOB) {
        requestObject.additionalPersonalInfo.childBirthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME) {
        requestObject.additionalPersonalInfo.anotherFirstName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME) {
        requestObject.additionalPersonalInfo.anotherMiddleName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME) {
        requestObject.additionalPersonalInfo.anotherLastName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME) {
        requestObject.additionalPersonalInfo.anotherAlsoKnownAs = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_DOB) {
        requestObject.additionalPersonalInfo.anotherBirthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.DOB) {
        requestObject.additionalPersonalInfo.birthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER) {
        requestObject.additionalPersonalInfo.personalHealthNumber = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED) {
        requestObject.additionalPersonalInfo.identityVerified = value;
      }
    }
  }

  const createRequestDetailsObject = (requestObject, name, value, value2) => {
    requestObject.id = requestId;
    requestObject.requestProcessStart = requiredRequestDetailsValues.requestStartDate;
    requestObject.dueDate = requiredRequestDetailsValues.dueDate;
    requestObject.receivedMode = requiredRequestDetailsValues.receivedMode;
    requestObject.deliveryMode = requiredRequestDetailsValues.deliveryMode;
    if (name === FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES) {
      requestObject.receivedDate = value.receivedDate;     
      requestObject.receivedDateUF = value.receivedDate? new Date(value.receivedDate).toISOString(): "";
      requestObject.requestProcessStart = value.requestStartDate;
      requestObject.dueDate = value.dueDate;
      requestObject.receivedMode = value.receivedMode;
      requestObject.deliveryMode = value.deliveryMode;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.ASSIGNED_TO) {
      const assignedToValue = value.split("|");
      if (FOI_COMPONENT_CONSTANTS.ASSIGNEE_GROUPS.find(groupName => (groupName === assignedToValue[0] && groupName === assignedToValue[1]))) {
        requestObject.assignedGroup = assignedToValue[0];
        requestObject.assignedTo = "";
      }
      else if (assignedToValue.length > 1) {
        requestObject.assignedGroup = assignedToValue[0];
        requestObject.assignedTo = assignedToValue[1];
      }
      else {
        requestObject.assignedGroup = "Unassigned";
        requestObject.assignedTo = assignedToValue[0];
      }   
      requestObject.assignedToName = value2;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME) {       
        requestObject.firstName = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME) {        
        requestObject.middleName = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME) {
        requestObject.lastName = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.ORGANIZATION) {
        requestObject.businessName = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL) {
        requestObject.email = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.FOI_CATEGORY) {
        requestObject.category = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.HOME_PHONE) {
      requestObject.phonePrimary = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.MOBILE_PHONE) {
      requestObject.phoneSecondary = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY) {
      requestObject.workPhonePrimary = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY) {
      requestObject.workPhoneSecondary = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) {
      requestObject.address = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY) {
      requestObject.addressSecondary = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.CITY) {
      requestObject.city = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.POSTALCODE) {
      requestObject.postal = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.PROVINCE) {
      requestObject.province = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.COUNTRY) {
      requestObject.country = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE) {     
      requestObject.receivedDate = formatDate(value, 'yyyy MMM, dd');
      const receivedDateUTC = new Date(value).toISOString();
      requestObject.receivedDateUF = receivedDateUTC;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
      requestObject.requestProcessStart = value;
      requestObject.dueDate = value2;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {
      requestObject.requestType = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
      requestObject.receivedMode = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
      requestObject.deliveryMode = value;
    }
    
    else if (name === FOI_COMPONENT_CONSTANTS.DESCRIPTION) {
      requestObject.description = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.START_DATE) {
      requestObject.fromDate = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.END_DATE) {
      requestObject.toDate = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST) {
      requestObject.selectedMinistries = [];
      const filteredData = value.filter(programArea => programArea.isChecked)
      .map(filteredProgramArea => {
        return {
          code: filteredProgramArea.bcgovcode,
          name: filteredProgramArea.name,
          isSelected: filteredProgramArea.isChecked
        }
      });
      requestObject.selectedMinistries = filteredData;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER) {
      requestObject.correctionalServiceNumber = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER) {
      requestObject.publicServiceEmployeeNumber = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.ISPIIREDACTED) {
      requestObject.ispiiredacted = value;
    }
  }

  const createSaveRequestObject = (name, value, value2) => 
  {
    const requestObject = {...saveRequestObject};  
    if (name === FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES) {
      setUnSavedRequest(false);      
    }
    else {
      setUnSavedRequest(true);
    }
    updateAdditionalInfo(name, value, requestObject);
    createRequestDetailsObject(requestObject, name, value, value2);    
    setSaveRequestObject(requestObject);
  }

  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);
    setUnSavedRequest(_unSaved);
    if (!_unSaved) {      
      setTimeout(() => 
      { 
        ministryId ? window.location.href = `/foi/foirequests/${requestId}/ministryrequest/${ministryId}/${_state}` : requestId ? window.location.href = `/foi/reviewrequest/${requestId}/${_state}` : dispatch(push(`/foi/reviewrequest/${id}/${_state}`)) 
      }
      , 1000);
      // setTimeout(() => { requestId ? window.location.reload()  : window.location.href = `/foi/reviewrequest/${id}/${value}` }, 1000);
    }
  }

  const handleOpenRequest = (parendId, ministryId, unSaved) => {
    setUnSavedRequest(unSaved);
      if (!unSaved) {
        dispatch(push(`/foi/foirequests/${parendId}/ministryrequest/${ministryId}/Open`));
      }
  }

  const handleStateChange =(currentStatus)=>{    
    setcurrentrequestStatus(currentStatus);
  }

  const handlestatusudpate = (_daysRemaining,_status, _cfrDaysRemaining)=>{
    if (_status === StateEnum.callforrecords.name && _cfrDaysRemaining < 0) {      
      settabStatus(StateEnum.callforrecordsoverdue.name)
    }
    const _daysRemainingText = _daysRemaining > 0 ? `${_daysRemaining} Days Remaining` : `${Math.abs(_daysRemaining)} Days Overdue`;
    const _cfrDaysRemainingText = _cfrDaysRemaining > 0 ? `CFR Due in ${_cfrDaysRemaining} Days` : `Records late by ${Math.abs(_cfrDaysRemaining)} Days`;
    const bottomText = (_status === StateEnum.open.name || _status === StateEnum.review.name || _status === StateEnum.redirect.name || _status === StateEnum.consult.name || _status === StateEnum.signoff.name || _status === StateEnum.response.name || _status === StateEnum.closed.name) ? _daysRemainingText : (_status === StateEnum.callforrecords.name || _status === StateEnum.feeassessed.name || _status === StateEnum.deduplication.name || _status === StateEnum.harms.name) ? `${_cfrDaysRemainingText}|${_daysRemainingText}`: _status;
    setRequestStatus(bottomText);
  }

  const hasStatusRequestSaved =(issavecompleted,state)=>{
    if(issavecompleted)
      {
        settabStatus(state)
        setcurrentrequestStatus("")
      }
  }

  switch (_tabStatus){
    case StateEnum.intakeinprogress.name:
      foitabheaderBG = "foitabheadercollection foitabheaderIntakeInProgressBG"
      break;
    case StateEnum.open.name:
      foitabheaderBG = "foitabheadercollection foitabheaderOpenBG"
      break;
    case StateEnum.closed.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderClosedBG"
      break;
    case StateEnum.callforrecords.name:
      foitabheaderBG = "foitabheadercollection foitabheaderCFRG"
      break;
    case StateEnum.callforrecordsoverdue.name:
      foitabheaderBG = "foitabheadercollection foitabheaderCFROverdueBG"
      break;
    case StateEnum.redirect.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderRedirectBG"
      break;
    case StateEnum.review.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderReviewBG"
      break;
    case StateEnum.feeassessed.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderFeeBG"
      break;
    case StateEnum.consult.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderConsultBG"
      break;
    case StateEnum.signoff.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderSignoffBG"
      break;
    case StateEnum.deduplication.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderDeduplicationBG"
      break;
    case StateEnum.harms.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderHarmsBG"
      break;
    case StateEnum.onhold.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderOnHoldBG"
      break;
    case StateEnum.response.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderResponseBG"
      break;
    default:
      foitabheaderBG = "foitabheadercollection foitabheaderdefaultBG";
      break;      
  }

  const tabclick =(evt,param)=>{
   
    var i, tabcontent, tablinks;
    
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
   
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(param).style.display = "block";
    evt.currentTarget.className += " active";

  }
  const bottomTextArray = _requestStatus.split('|');
      
  const userId = userDetail.preferred_username
  const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random"
  const name = `${userDetail.family_name}, ${userDetail.given_name}`
  const signinUrl = "/signin"
  const signupUrl = "/signup"

  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  const isLoading = useSelector(state=> state.foiRequests.isLoading);
   
  return (

    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown requestStatus={_requestStatus} handleStateChange={handleStateChange} isMinistryCoordinator={false} isValidationError={isValidationError} />
          </div>
          
        <div className="tab">
          <div className="tablinks active" name="Request" onClick={e => tabclick(e,'Request')}>Request</div>
          {
            url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) === -1 ? <div className="tablinks" name="Comments" onClick={e=>tabclick(e,'Comments')}>Comments</div> : null
          }
          
          <div className="tablinks" name="Option3" onClick={e=>tabclick(e,'Option3')}>Option 3</div>
        </div>
       
        <div className="foileftpanelstatus">
        {bottomTextArray.length > 0 && (_requestStatus && _requestStatus.toLowerCase().includes("days") ) ?
        <>
          <h4>{_tabStatus && (_tabStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase() || _tabStatus.toLowerCase() === StateEnum.closed.name.toLowerCase()) ? "" : bottomTextArray[0]}</h4>
          {bottomTextArray.length > 1  ?
          <h4>{bottomTextArray[1]}</h4>
          : null }
          </>
          : null
          }
        </div>
        

        </div>
        <div className="foitabpanelcollection"> 
          <div id="Request" className="tabcontent active">                                
            <div className="container foi-review-request-container">

              <div className="foi-review-container">
                <form className={`${classes.root} foi-request-form`} autoComplete="off">
                  {(urlIndexCreateRequest === -1 && Object.entries(requestDetails).length !== 0) || urlIndexCreateRequest > -1 ? (
                    <>
                      <FOIRequestHeader headerValue={headerValue} requestDetails={requestDetails} handleAssignedToValue={handleAssignedToValue} createSaveRequestObject={createSaveRequestObject} handlestatusudpate={handlestatusudpate} userDetail={userDetail} disableInput={disableInput} />
                      <ApplicantDetails requestDetails={requestDetails} contactDetailsNotGiven={contactDetailsNotGiven} handleApplicantDetailsInitialValue={handleApplicantDetailsInitialValue} handleEmailValidation={handleEmailValidation} handleApplicantDetailsValue={handleApplicantDetailsValue} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} /> 
                       {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
                        <ChildDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} /> : null}
                      {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
                        <OnBehalfOfDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} /> : null}
                       <AddressContactDetails requestDetails={requestDetails} contactDetailsNotGiven={contactDetailsNotGiven} createSaveRequestObject={createSaveRequestObject} handleContactDetailsInitialValue={handleContactDetailsInitialValue} handleContanctDetailsValue={handleContanctDetailsValue} disableInput={disableInput} />
                      <RequestDescriptionBox programAreaList={programAreaList} urlIndexCreateRequest={urlIndexCreateRequest} requestDetails={requestDetails} handleUpdatedProgramAreaList={handleUpdatedProgramAreaList} handleOnChangeRequiredRequestDescriptionValues={handleOnChangeRequiredRequestDescriptionValues} handleInitialRequiredRequestDescriptionValues={handleInitialRequiredRequestDescriptionValues} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} />
                      <RequestDetails requestDetails={requestDetails} handleRequestDetailsValue={handleRequestDetailsValue} handleRequestDetailsInitialValue={handleRequestDetailsInitialValue} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} />
                      {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
                        <AdditionalApplicantDetails requestDetails={requestDetails} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} /> : null} 
                      <RequestNotes />

                      <BottomButtonGroup isValidationError={isValidationError} urlIndexCreateRequest={urlIndexCreateRequest} saveRequestObject={saveRequestObject} unSavedRequest={unSavedRequest} handleSaveRequest={handleSaveRequest} handleOpenRequest={handleOpenRequest} currentSelectedStatus={_currentrequestStatus} hasStatusRequestSaved={hasStatusRequestSaved} disableInput={disableInput} />
                    </>
                  ) : null}
                </form>
              </div>
            </div>                            
          </div> 
          <div id="Comments" className="tabcontent">
            {
             !isLoading && requestNotes && (iaoassignedToList.length > 0 || ministryAssignedToList.length > 0) ?
                <>
                <CommentSection currentUser={userId && { userId: userId, avatarUrl: avatarUrl, name: name }} commentsArray={requestNotes.sort(function(a, b) { return b.commentId - a.commentId;})}
                    setComment={setComment} signinUrl={signinUrl} signupUrl={signupUrl} requestid={requestId} ministryId={ministryId} bcgovcode={bcgovcode} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList}  />
                
                </> : <Loading />
            }

          
              </div> 
          <div id="Option3" className="tabcontent">
           <h3>Option 3</h3>
          </div>        
        </div>
      </div>
    </div>

  );


  });

export default FOIRequest;
