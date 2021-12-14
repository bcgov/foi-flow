import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
import './MinistryReview.scss'
import { StateDropDown } from '../../customComponents';
import '../foirequestheader.scss'
import "./MinistryReviewTabbedContainer.scss";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import {  
  fetchFOIMinistryViewRequestDetails,
  fetchFOIRequestDescriptionList,
  fetchFOIRequestNotesList,
  fetchFOIRequestAttachmentsList,
  fetchFOIFullAssignedToList,
  fetchFOIMinistryAssignedToList
} from "../../../../apiManager/services/FOI/foiRequestServices";

import { calculateDaysRemaining } from "../../../../helper/FOI/helper";

import ApplicantDetails from './ApplicantDetails';
import RequestDetails from './RequestDetails';
import RequestDescription from './RequestDescription';
import RequestHeader from './RequestHeader';
import RequestTracking from './RequestTracking';
import BottomButtonGroup from './BottomButtonGroup';
import {CommentSection} from '../../customComponents/Comments';
import {AttachmentSection} from '../../customComponents/Attachments';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import Loading from "../../../../containers/Loading";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
    },
  },
  validationErrorMessage: {
    marginTop: '30px',
    color: "#fd0404",
  },
  validationMessage: {
    marginTop: '30px',
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


const MinistryReview = React.memo(({ userDetail }) => {

  const { requestId, ministryId, requestState} = useParams();
  const [_requestStatus, setRequestStatus] = React.useState(requestState);
  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  const [_tabStatus, settabStatus] = React.useState(requestState);
  //gets the request detail from the store


  let requestDetails = useSelector(state => state.foiRequests.foiMinistryViewRequestDetail);
  let requestNotes = useSelector(state => state.foiRequests.foiRequestComments);
  let requestAttachments = useSelector(state=> state.foiRequests.foiRequestAttachments);
  let bcgovcode = ministryId && requestDetails && requestDetails["selectedMinistries"] ?JSON.stringify(requestDetails["selectedMinistries"][0]["code"]):""
  const [comment, setComment] = useState([]);

  //quillChange and removeComment added to handle Navigate away from Comments tabs
  const [quillChange, setQuillChange] = useState(false);
  const [removeComment, setRemoveComment] = useState(false);

  const [attachments, setAttachments] = useState(requestAttachments);
  const dispatch = useDispatch();
  useEffect(() => {
    if (ministryId) {
      dispatch(fetchFOIMinistryViewRequestDetails(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
      dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId,ministryId));
      dispatch(fetchFOIFullAssignedToList());
      if (bcgovcode)
        dispatch(fetchFOIMinistryAssignedToList(bcgovcode));
    }
    
  }, [requestId, dispatch]);

  const [headerValue, setHeader] = useState("");
  const [ministryAssignedToValue, setMinistryAssignedToValue] = React.useState("Unassigned");
  //gets the request detail from the store



  const [saveMinistryRequestObject, setSaveMinistryRequestObject] = React.useState(requestDetails);


  const [divstages, setdivStages] = React.useState([])

  let ministryassignedtousername = "Unassigned";
  useEffect(() => {
    const requestDetailsValue = requestDetails;
    setSaveMinistryRequestObject(requestDetailsValue);
    ministryassignedtousername = requestDetailsValue && requestDetailsValue.assignedministryperson ? requestDetailsValue.assignedministryperson : "Unassigned";
    setMinistryAssignedToValue(ministryassignedtousername);
  }, [requestDetails]);

  const [unSavedRequest, setUnSavedRequest] = React.useState(false);

  let _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);
  const _cfrDaysRemaining = requestDetails.cfrDueDate ? calculateDaysRemaining(requestDetails.cfrDueDate) : '';
  const _daysRemainingText = _daysRemaining > 0 ? `${_daysRemaining} Days Remaining` : `${Math.abs(_daysRemaining)} Days Overdue`;
  const _cfrDaysRemainingText = _cfrDaysRemaining > 0 ? `CFR Due in ${_cfrDaysRemaining} Days` : `Records late by ${Math.abs(_cfrDaysRemaining)} Days`;
  const bottomText = `${_cfrDaysRemainingText}|${_daysRemainingText}`;
  const bottomTextArray = bottomText.split('|');

  //gets the latest ministry assigned to value
  const handleMinistryAssignedToValue = (value) => {
    setMinistryAssignedToValue(value);
  }

  let hasincompleteDivstage = false;
  divstages.forEach((item) => {
    if (item.divisionid === -1 || item.stageid === -1 || item.stageid === "" || item.divisionid === "") {
      hasincompleteDivstage = true
    }
  })

  //Variable to find if all required fields are filled or not
  const isValidationError = ministryAssignedToValue.toLowerCase().includes("unassigned") || (divstages.length === 0 || hasincompleteDivstage);

  const createMinistryRequestDetailsObject = (requestObject, propName, value) => {
    // requestDetails.
    if (propName === FOI_COMPONENT_CONSTANTS.MINISTRY_ASSIGNED_TO) {
      const assignedToValue = value.split("|");
      if (assignedToValue.length > 1 && assignedToValue[0] && assignedToValue[1]) {
        requestObject.assignedministrygroup = assignedToValue[0];
        requestObject.assignedministryperson = assignedToValue[1];
      }
    }
  }

  const createMinistrySaveRequestObject = (propName, value, value2) => {
    const requestObject = { ...saveMinistryRequestObject };
    setUnSavedRequest(true);
    createMinistryRequestDetailsObject(requestObject, propName, value);
    setSaveMinistryRequestObject(requestObject);
  }
  const [updateStateDropDown, setUpdateStateDropdown] = useState(false);
  const [stateChanged, setStateChanged] = useState(false);
  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);
    setUnSavedRequest(_unSaved);
    if (!_unSaved && ministryId && requestId) {
      setStateChanged(false);
      setcurrentrequestStatus(_state);
      setTimeout(() => {
        window.location.href = `/foi/ministryreview/${requestId}/ministryrequest/${ministryId}/${_state}`
      }
        , 1000);
    }
    else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(_state);
    }
  }

  const handleStateChange = (currentStatus) => {
    setcurrentrequestStatus(currentStatus);
    setStateChanged(true);
  }

  const hasStatusRequestSaved = (issavecompleted, state) => {
    if (issavecompleted) {
      settabStatus(state)
      setcurrentrequestStatus("")
    }
  }


  var foitabheaderBG;
  const classes = useStyles();

  switch (_tabStatus) {
    case StateEnum.open.name:
      foitabheaderBG = "foitabheadercollection foitabheaderOpenBG"
      break;
    case StateEnum.closed.name:
      foitabheaderBG = "foitabheadercollection foitabheaderClosedBG"
      break;
    case StateEnum.callforrecords.name:
      if (_cfrDaysRemaining < 0) {
        foitabheaderBG = "foitabheadercollection foitabheaderCFROverdueBG"
      }
      else {
        foitabheaderBG = "foitabheadercollection foitabheaderCFRG"
      }
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

  /*******
   * alertUser(), handleOnHashChange() and useEffect() are used to handle the Navigate away from Comments tabs
   */
  //Below function will handle beforeunload event
  const alertUser = e => {
    if (quillChange) {     
      e.returnValue = '';
      e.preventDefault();
    }
  }

  //Below function will handle popstate event
  const handleOnHashChange = (e) => {   
    e.preventDefault();
    window.removeEventListener('beforeunload', alertUser);
  };

  React.useEffect(() => {    
    window.history.pushState(null, null, window.location.pathname);
    window.addEventListener('popstate', handleOnHashChange);
    window.addEventListener('beforeunload', alertUser);
    return () => {
      window.removeEventListener('popstate', handleOnHashChange);
      window.removeEventListener('beforeunload', alertUser);
    }
  });

  const tabclick = (evt, param) => {
    let clickedOk = true;
    if (quillChange && param !== 'Comments') {
      if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
        clickedOk = true;
        setQuillChange(false);
        setRemoveComment(true);
      }
      else {
        setQuillChange(true);
        setRemoveComment(false);
        clickedOk = false;
        param = 'Comments';
        document.getElementById(param).className += " active";
        const elementsByName = document.getElementsByName(param);
        var i;
        for (i = 0; i < elementsByName.length; i++) {          
            elementsByName[i].className += " active";        
        }
      }
    }
    else {
      setRemoveComment(false);
    }
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
      tabcontent[i].className = tabcontent[i].className.replace(" active", "");
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(param).style.display = "block";
    if (clickedOk)
      evt.currentTarget.className += " active";
    
  }

  const pubmindivstagestomain = (divstages) => {

    saveMinistryRequestObject.divisions = divstages
    setdivStages(divstages)
  }



  const userId = userDetail && userDetail.preferred_username
  const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random"
  const name = `${userDetail && userDetail.family_name}, ${userDetail && userDetail.given_name}`
  const signinUrl = "/signin"
  const signupUrl = "/signup"

  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  const isLoading = useSelector(state=> state.foiRequests.isLoading);
  const isAttachmentListLoading = useSelector(state=> state.foiRequests.isAttachmentListLoading);

  const requestNumber = requestDetails && requestDetails.idNumber; 
  
  return (

    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown updateStateDropDown={updateStateDropDown} requestStatus={_requestStatus} handleStateChange={handleStateChange} isMinistryCoordinator={true} isValidationError={isValidationError} />
          </div>
          
        <div className="tab">
          <div className="tablinks active" name="Request" onClick={e => tabclick(e,'Request')}>Request</div>
          <div className="tablinks" name="Attachments" onClick={e=>tabclick(e,'Attachments')}>Attachments{requestAttachments && requestAttachments.length > 0 ? ` (${requestAttachments.length})`: ''}</div>
          <div className="tablinks" name="Comments" onClick={e=>tabclick(e,'Comments')}>Comments {requestNotes && requestNotes.length > 0  ? `(${requestNotes.length})`:""}</div>
          <div className="tablinks" name="Option4" onClick={e=>tabclick(e,'Option4')}>Option 4</div>
        </div>
        
        <div className="foileftpanelstatus">
        {_requestStatus.toLowerCase() !== StateEnum.onhold.name.toLowerCase() && _requestStatus.toLowerCase() !== StateEnum.closed.name.toLowerCase() ?  
          <>
          {(_requestStatus.toLowerCase() !== StateEnum.review.name.toLowerCase() && _requestStatus.toLowerCase() !== StateEnum.consult.name.toLowerCase() && _requestStatus.toLowerCase() !== StateEnum.signoff.name.toLowerCase() && _requestStatus.toLowerCase() !== StateEnum.response.name.toLowerCase()  )?
          <h4>{bottomTextArray[0]}</h4>
          : null }
          <h4>{bottomTextArray[1]}</h4>
          </>
        : null }
        </div>  
     
        </div>
        <div className="foitabpanelcollection">
          <div id="Request" className="tabcontent active">
            <div className="container foi-review-request-container">

              <div className="foi-review-container">
                <form className={`${classes.root} foi-request-form`} autoComplete="off">
                  { Object.entries(requestDetails).length >0  && requestDetails !== undefined ? 
                  <>
                    <RequestHeader requestDetails={requestDetails} userDetail={userDetail} handleMinistryAssignedToValue={handleMinistryAssignedToValue} createMinistrySaveRequestObject={createMinistrySaveRequestObject} />
                    <ApplicantDetails requestDetails={requestDetails} /> 
                    <RequestDescription requestDetails={requestDetails} />
                    <RequestDetails requestDetails={requestDetails}/>
                    <RequestTracking pubmindivstagestomain={pubmindivstagestomain} existingDivStages={requestDetails.divisions} ministrycode={requestDetails.selectedMinistries[0].code}/>                                                
                    {/* <RequestNotes /> */}
                    <BottomButtonGroup stateChanged={stateChanged} attachmentsArray={requestAttachments} isValidationError={isValidationError} saveMinistryRequestObject={saveMinistryRequestObject} unSavedRequest={unSavedRequest} handleSaveRequest={handleSaveRequest} currentSelectedStatus={_currentrequestStatus} hasStatusRequestSaved={hasStatusRequestSaved} />
                  </>
                : null }
                </form>
              </div>
            </div>
          </div> 
          <div id="Attachments" className="tabcontent">
            {
             !isAttachmentListLoading && iaoassignedToList && iaoassignedToList.length > 0 && ministryAssignedToList && ministryAssignedToList.length > 0 ?
                <>
                <AttachmentSection currentUser={userId} attachmentsArray={requestAttachments}
                  setAttachments={setAttachments} requestId={requestId} ministryId={ministryId} 
                  requestNumber={requestNumber} requestState={requestState}
                  iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} />
                </> : <Loading />
            }
          </div> 
          <div id="Comments" className="tabcontent">
            {
             !isLoading && requestNotes && iaoassignedToList.length > 0 && ministryAssignedToList.length > 0 ?
                <>
                  <CommentSection currentUser={userId && { userId: userId, avatarUrl: avatarUrl, name: name }} commentsArray={requestNotes.sort(function (a, b) { return b.commentId - a.commentId; })}
                    setComment={setComment} signinUrl={signinUrl} signupUrl={signupUrl} bcgovcode={bcgovcode} requestid={requestId} 
                    ministryId={ministryId} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList}
                    requestNumber={requestNumber}
                    //setQuillChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs 
                    setQuillChange={setQuillChange} removeComment={removeComment} setRemoveComment={setRemoveComment} />
                </> : <Loading />}
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
