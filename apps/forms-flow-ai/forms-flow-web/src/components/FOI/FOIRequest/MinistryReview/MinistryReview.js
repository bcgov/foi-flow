import React, { useEffect, useState }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import './MinistryReview.scss'
import { StateDropDown } from '../../customComponents';
import '../foirequestheader.scss'
import "./MinistryReviewTabbedContainer.scss";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import {
  fetchFOIRequestDetails,
  fetchFOIMinistryViewRequestDetails,
  fetchFOIRequestDescriptionList
} from "../../../../apiManager/services/FOI/foiRequestServices";

import { calculateDaysRemaining} from "../../../../helper/FOI/helper";

import ApplicantDetails from './ApplicantDetails';
import RequestDetails from './RequestDetails';
import RequestDescription from './RequestDescription';
import RequestHeader from './RequestHeader';
import RequestNotes from './RequestNotes';
import RequestTracking from './RequestTracking';
import BottomButtonGroup from './BottomButtonGroup';

import {push} from "connected-react-router";
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';

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
  btndisabled: {
    border: 'none',
    backgroundColor: '#eceaea',
    color: '#FFFFFF'
  },
  btnenabled: {
    border: 'none',
    backgroundColor: '#38598A',
    color: '#FFFFFF'
  },
  btnsecondaryenabled: {
    border: '1px solid #38598A',
    backgroundColor: '#FFFFFF',
    color: '#38598A'
  }
 
}));


const MinistryReview = React.memo((props) => {

  const {requestId, ministryId, requestState} = useParams();
  const [_requestStatus, setRequestStatus] = React.useState(requestState);
  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  const [_tabStatus, settabStatus] = React.useState(requestState);
  const [headerValue, setHeader] = useState("");
  const [ministryAssignedToValue, setMinistryAssignedToValue] = React.useState("Unassigned");
    
  //gets the request detail from the store
  let requestDetails = useSelector(state=> state.foiRequests.foiMinistryViewRequestDetail);
  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  const [saveMinistryRequestObject, setSaveMinistryRequestObject] = React.useState({});

  const dispatch = useDispatch();
  useEffect(() => {
    if (ministryId) {
      dispatch(fetchFOIRequestDetails(requestId, ministryId));
      dispatch(fetchFOIMinistryViewRequestDetails(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
    }     
  },[requestId, dispatch]); 

  let ministryassignedtousername = "Unassigned";
  useEffect(() => {
    const requestDetailsValue = requestDetails;
    setSaveRequestObject(requestDetailsValue);
    ministryassignedtousername = requestDetailsValue && requestDetailsValue.assignedministryperson ? requestDetailsValue.assignedministryperson : "Unassigned";
    setMinistryAssignedToValue(ministryassignedtousername);
  },[requestDetails]); 

  const [unSavedRequest, setUnSavedRequest] = React.useState(false);

  let _daysRemaining = calculateDaysRemaining(requestDetails.dueDate); 
  const _cfrDaysRemaining = requestDetails.cfrDueDate ? calculateDaysRemaining(requestDetails.cfrDueDate): '';
  const _daysRemainingText = _daysRemaining > 0 ? `${_daysRemaining} Days Remaining` : `${Math.abs(_daysRemaining)} Days Overdue`;
  const _cfrDaysRemainingText = _cfrDaysRemaining > 0 ? `CFR Due in ${_cfrDaysRemaining} Days` : `Records late by ${Math.abs(_cfrDaysRemaining)} Days`;
  const bottomText =  `${_cfrDaysRemainingText}|${_daysRemainingText}`;
  const bottomTextArray = bottomText.split('|'); 
 
  //gets the latest ministry assigned to value
  const handleMinistryAssignedToValue = (value) => {   
    setMinistryAssignedToValue(value);
  }

  //Variable to find if all required fields are filled or not
  const isValidationError = ministryAssignedToValue.toLowerCase().includes("unassigned");

  const createMinistryRequestDetailsObject = (requestObject, name, value) => {
    requestObject.assignedGroup = requestDetails.assignedGroup;
    requestObject.assignedTo = requestDetails.assignedTo;
    requestObject.assignedministrygroup = requestDetails.assignedministrygroup;
    requestObject.assignedministryperson = requestDetails.assignedministryperson;
    // requestDetails.
    if (name === FOI_COMPONENT_CONSTANTS.MINISTRY_ASSIGNED_TO) {
      const assignedToValue = value.split("|");
      if (assignedToValue.length > 1 && assignedToValue[0] && assignedToValue[1]) {
        requestObject.assignedministrygroup = assignedToValue[0];
        requestObject.assignedministryperson = assignedToValue[1];
      }
    }
  }

  const createMinistrySaveRequestObject = (name, value, value2) => {
    const requestObject = {...saveMinistryRequestObject};  
    setUnSavedRequest(true);
    createMinistryRequestDetailsObject(requestObject, name, value);    
    setSaveMinistryRequestObject(requestObject);
  }

  const createRequestDetailsObject = (requestObject, name, value) => {
    requestObject.id = requestId;
    requestObject.requestProcessStart = requestDetails.requestProcessStart;
    requestObject.dueDate = requestDetails.dueDate;
    requestObject.receivedMode = requestDetails.receivedMode;
    requestObject.deliveryMode = requestDetails.deliveryMode;
    requestObject.assignedGroup = requestDetails.assignedGroup;
    requestObject.assignedTo = requestDetails.assignedTo;
    //--------------- need update this later: fn and ln should not be required field for ministry request
    requestObject.firstName = "test";
    requestObject.lastName = "test";
    requestObject.additionalPersonalInfo = {};
    requestObject.assignedministrygroup = requestDetails.assignedministrygroup;
    requestObject.assignedministryperson = requestDetails.assignedministryperson;
    // requestDetails.
    if (name === FOI_COMPONENT_CONSTANTS.MINISTRY_ASSIGNED_TO) {
      const assignedToValue = value.split("|");
      if (assignedToValue.length > 1 && assignedToValue[0] && assignedToValue[1]) {
        requestObject.assignedministrygroup = assignedToValue[0];
        requestObject.assignedministryperson = assignedToValue[1];
      }
    }
  }

  const createSaveRequestObject = (name, value, value2) => {
    const requestObject = {...saveRequestObject};  
    setUnSavedRequest(true);
    createRequestDetailsObject(requestObject, name, value);    
    setSaveRequestObject(requestObject);
  }

  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);
    setUnSavedRequest(_unSaved);
    if (!_unSaved && ministryId && requestId) {
      setTimeout(() => 
      { 
        window.location.href = `/foi/ministryreview/${requestId}/ministryrequest/${ministryId}/${_state}` 
      }
      , 1000);
    }
  }
  
  const handleStateChange =(currentStatus)=>{
    createSaveRequestObject("", "", "");
    setcurrentrequestStatus(currentStatus);
  }

  const hasStatusRequestSaved =(issavecompleted,state)=>{
    if(issavecompleted)
      {
        settabStatus(state)
        setcurrentrequestStatus("")
      }
  }


  var foitabheaderBG;
  const classes = useStyles();
 
  switch (_tabStatus){
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
  

  return (
    
    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown requestStatus={_requestStatus} handleStateChange={handleStateChange} isMinistryCoordinator={true} isValidationError={isValidationError} />
          </div>
          
        <div className="tab">
          <div className="tablinks active" name="Request" onClick={e => tabclick(e,'Request')}>Request</div>
          <div className="tablinks" name="CorrespondenceLog" onClick={e=>tabclick(e,'CorrespondenceLog')}>Correspondence Log</div>
          <div className="tablinks" name="Option3" onClick={e=>tabclick(e,'Option3')}>Option 3</div>
        </div>
        
        <div className="foileftpanelstatus"> 
          <h4>{bottomTextArray[0]}</h4>
          <h4>{bottomTextArray[1]}</h4>
        </div>        
        </div>
        <div className="foitabpanelcollection"> 
          <div id="Request" className="tabcontent active">                                
            <div className="container foi-review-request-container">

              <div className="foi-review-container">
                <form className={`${classes.root} foi-request-form`} autoComplete="off">
                  { Object.entries(requestDetails).length >0  && requestDetails !== undefined ? 
                  <>
                    <RequestHeader requestDetails={requestDetails} handleMinistryAssignedToValue={handleMinistryAssignedToValue} createMinistrySaveRequestObject={createMinistrySaveRequestObject} />
                    <ApplicantDetails requestDetails={requestDetails} /> 
                    <RequestDescription requestDetails={requestDetails} />
                    <RequestDetails requestDetails={requestDetails} />
                    <RequestTracking/>                    
                    <RequestNotes />
                    { _requestStatus.toLowerCase() == StateEnum.callforrecords.name.toLocaleLowerCase() ?
                      <BottomButtonGroup isValidationError={isValidationError} saveRequestObject={saveRequestObject} saveMinistryRequestObject={saveMinistryRequestObject} unSavedRequest={unSavedRequest} handleSaveRequest={handleSaveRequest} currentSelectedStatus={_currentrequestStatus} hasStatusRequestSaved={hasStatusRequestSaved} />
                      : null 
                    }
                  </>
                : null }
                </form>
              </div>
            </div>                            
          </div> 
          <div id="CorrespondenceLog" className="tabcontent">
              
              </div> 
          <div id="Option3" className="tabcontent">
           <h3>Option 3</h3>
          </div>        
        </div>
      </div>
    </div>

  );

  })

  export default MinistryReview
