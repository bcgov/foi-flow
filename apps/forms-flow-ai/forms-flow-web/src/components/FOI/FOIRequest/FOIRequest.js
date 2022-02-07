import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
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
import RequestNotes from './RequestNotes';
import BottomButtonGroup from './BottomButtonGroup';
import { useParams } from 'react-router-dom';
import {
  fetchFOICategoryList,
  fetchFOIProgramAreaList,
  fetchFOIAssignedToList,
  fetchFOIDeliveryModeList,
  fetchFOIReceivedModeList,
  fetchClosingReasonList,
  fetchFOIFullAssignedToList,
  fetchFOIMinistryAssignedToList
} from "../../../apiManager/services/FOI/foiMasterDataServices";
import {
  fetchFOIRequestDetailsWrapper,
  fetchFOIRequestDescriptionList
} from "../../../apiManager/services/FOI/foiRequestServices";
import {
  fetchFOIRequestAttachmentsList
} from "../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRequestNotesList } from "../../../apiManager/services/FOI/foiRequestNoteServices";
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
import { getAssignedTo } from "./FOIRequestHeader/utils";
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
  alertUser,
  findRequestState
} from "./utils";
import { ConditionalComponent } from '../../../helper/FOI/helper';
import DivisionalTracking from './DivisionalTracking';
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
  displayed: {
    display: "block"
  },
  hidden: {
    display: "none"
  }
}));

const FOIRequest = React.memo(({ userDetail }) => {
  const [_requestStatus, setRequestStatus] = React.useState(StateEnum.unopened.name);
  const { requestId, ministryId} = useParams();
  const disableInput = requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase();
  const [_tabStatus, settabStatus] = React.useState(requestState);

  var foitabheaderBG = getTabBG(_tabStatus, requestState);

  const url = window.location.href;
  const urlIndexCreateRequest = url.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST);
  const isAddRequest = urlIndexCreateRequest > -1;
  //gets the request detail from the store
  let requestDetails = useSelector(state => state.foiRequests.foiRequestDetail);
  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  let requestExtensions = useSelector(state => state.foiRequests.foiRequestExtesions);
  let requestNotes = useSelector(state => state.foiRequests.foiRequestComments);  
  let requestAttachments = useSelector(state => state.foiRequests.foiRequestAttachments);
  const [attachments, setAttachments] = useState(requestAttachments);
  const [comment, setComment] = useState([]);
  const [requestState, setRequestState] = useState(StateEnum.unopened.name);
  
  //editorChange and removeComment added to handle Navigate away from Comments tabs
  const [editorChange, setEditorChange] = useState(false);

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
    Option4: {
      display: false,
      active: false
    }
  };

  const [tabLinksStatuses, setTabLinksStatuses] = useState({
    ...initialStatuses,
    Request: {
      display: true,
      active: true
    },
  })
  const [removeComment, setRemoveComment] = useState(false);

  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  const showDivisionalTracking = requestDetails && requestDetails.divisions?.length > 0 &&
    (requestState && requestState.toLowerCase() !== StateEnum.open.name.toLowerCase() &&
      requestState.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase());

  let bcgovcode = getBCgovCode(ministryId, requestDetails);
  
  const dispatch = useDispatch();
  useEffect(() => {
    if (isAddRequest) {
      dispatch(fetchFOIAssignedToList("", ""));
    } else {
      dispatch(fetchFOIRequestDetailsWrapper(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
      dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
    }

    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
    dispatch(fetchClosingReasonList());

    if (bcgovcode)
      dispatch(fetchFOIMinistryAssignedToList(bcgovcode));
  }, [requestId, ministryId, comment, attachments]);


  useEffect(() => {
    const requestDetailsValue = isAddRequest ? {} : requestDetails;
    setSaveRequestObject(requestDetailsValue);
    const assignedTo = getAssignedTo(requestDetails);
    setAssignedToValue(assignedTo);
    if(requestDetails && Object.entries(requestDetails).length !== 0){
      var requestStateFromId = findRequestState(requestDetails.requeststatusid);
      setRequestState(requestStateFromId);
      settabStatus(requestStateFromId);
      setcurrentrequestStatus(requestStateFromId);
    }
  }, [requestDetails]);


  const requiredRequestDescriptionDefaultData = {
    startDate: "",
    endDate: "",
    description: "",
    isProgramAreaSelected: false,
    ispiiredacted: false
  }

  const requiredRequestDetailsInitialValues = {
    requestType: "",
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
  }, [])
  const handleRequestDetailsInitialValue = React.useCallback((value) => {
    setRequiredRequestDetailsValues(value);
  }, [])
  const handleApplicantDetailsInitialValue = React.useCallback((value) => {
    setRequiredApplicantDetails(value);
  }, [])
  const handleContactDetailsInitialValue = React.useCallback((value) => {
    setrequiredContactDetails(value);
  }, [])

  const handleApplicantDetailsValue = (value, name) => {
    const detailsData = assignValue(requiredApplicantDetails, value, name);
    setRequiredApplicantDetails(detailsData);
  }

  const handleContanctDetailsValue = (value, name) => {
    const detailsData = assignValue(requiredContactDetails, value, name);
    setrequiredContactDetails(detailsData);
  }

  //Update required fields of request description box with latest value
  const handleOnChangeRequiredRequestDescriptionValues = (value, name) => {
    const descriptionData = assignValue(requiredRequestDescriptionValues, value, name);
    setRequiredRequestDescriptionValues(descriptionData);
  }

  //Update required fields of request details box with latest value
  const handleRequestDetailsValue = (value, name, value2) => {
    const detailsData = assignValue(requiredRequestDetailsValues, value, name);

    if (value2) {
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

  const handleUpdatedProgramAreaList = (_programAreaList) => {
    //get the updated program area list with isChecked=true/false
    setProgramAreaList(_programAreaList);
  }

  const contactDetailsNotGiven = checkContactGiven(requiredContactDetails, requiredApplicantDetails);

  //Variable to find if all required fields are filled or not
  const isValidationError = checkValidationError(requiredApplicantDetails, contactDetailsNotGiven, requiredRequestDescriptionValues, validation, assignedToValue, requiredRequestDetailsValues);

  const classes = useStyles();

  const createRequestDetailsObject = (requestObject, name, value, value2) => {
    return createRequestDetailsObjectFunc(requestObject, requiredRequestDetailsValues, requestId, name, value, value2);
  }

  const createSaveRequestObject = (name, value, value2) => {
    let requestObject = { ...saveRequestObject };
    setUnSavedRequest(name !== FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES);

    requestObject = createRequestDetailsObject(requestObject, name, value, value2);
    setSaveRequestObject(requestObject);
  }
  const [updateStateDropDown, setUpdateStateDropdown] = useState(false);
  const [stateChanged, setStateChanged] = useState(false);
  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);
    setUnSavedRequest(_unSaved);
    
    if (!_unSaved) {
      setStateChanged(false);
      setcurrentrequestStatus(_state);
      setTimeout(() => {
        const redirectUrl = getRedirectAfterSaveUrl(ministryId, requestId);

        if (redirectUrl) {
          window.location.href = redirectUrl
        } else {
          dispatch(push(`/foi/reviewrequest/${id}`))
        }

      }
        , 1000);
    }
    else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(_state);
      setStateChanged(false);
    }
  }

  const handleOpenRequest = (parendId, _ministryId, unSaved) => {
    setUnSavedRequest(unSaved);
    if (!unSaved) {
      setStateChanged(false);
      setcurrentrequestStatus(StateEnum.open.name);

      dispatch(push(`/foi/foirequests/${parendId}/ministryrequest/${_ministryId}`));
    }
    else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(requestState); // should be revisited
    }
  }

  const handleStateChange = (currentStatus) => {
    setcurrentrequestStatus(currentStatus);
    setStateChanged(true);
  }

  const handlestatusudpate = (_daysRemaining, _status, _cfrDaysRemaining) => {
    if (_status === StateEnum.callforrecords.name && _cfrDaysRemaining < 0) {
      settabStatus(StateEnum.callforrecordsoverdue.name)
    }

    const mappedBottomText = getTabBottomText({
      _daysRemaining,
      _cfrDaysRemaining,
      _status,
      requestExtensions,
    });

    setRequestStatus(mappedBottomText);
  }

  const hasStatusRequestSaved = (state) => {
    settabStatus(state);
    setcurrentrequestStatus("");
  }

  /*******
   * alertUser(), handleOnHashChange() and useEffect() are used to handle the Navigate away from Comments tabs
   */
  //Below function will handle beforeunload event
  const handleBeforeUnload = e => {
    if (editorChange) {
      alertUser(e);
    }
  }

  //Below function will handle popstate event
  const handleOnHashChange = (e) => {
    e.preventDefault();
  };

  React.useEffect(() => {
    if (editorChange) {
      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener('popstate', handleOnHashChange);
      window.addEventListener('beforeunload', handleBeforeUnload);
      return () => {
        window.removeEventListener('popstate', handleOnHashChange);
        window.removeEventListener('beforeunload', handleBeforeUnload);
      }
    }
  }, [editorChange]);

  const tabclick = (param) => {
    if (param === 'Comments') {
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
      )
    } else {

      changeTabLinkStatuses(param);

    }

  }

  const changeTabLinkStatuses = (param) => {
    setTabLinksStatuses({
      ...initialStatuses,
      [param]: {
        ...tabLinksStatuses[param],
        active: true,
        display: true,
      },
    });
  }


  const bottomTextArray = _requestStatus.split('|');

  const userId = userDetail?.preferred_username
  const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random"
  var lastName = '', firstName = ''

  if (userDetail) {
    firstName = userDetail.given_name
    lastName = userDetail.family_name
  }
  const fullName = `${lastName}, ${firstName}`
  const signinUrl = "/signin"
  const signupUrl = "/signup"

  const requestNumber = requestDetails?.idNumber;

  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  const isLoading = useSelector(state => state.foiRequests.isLoading);
  const isAttachmentListLoading = useSelector(state => state.foiRequests.isAttachmentListLoading);

  const stateTransition = requestDetails?.stateTransition;

  return (
  (!isLoading && requestDetails && Object.keys(requestDetails).length !== 0) || isAddRequest ?
    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown requestState={requestState} updateStateDropDown={updateStateDropDown} stateTransition={stateTransition} requestStatus={_requestStatus} handleStateChange={handleStateChange} isMinistryCoordinator={false} isValidationError={isValidationError} />
          </div>

          <div className="tab">
            <div
              className={clsx("tablinks", {
                "active": tabLinksStatuses.Request.active
              })}
              name="Request"
              onClick={() => tabclick('Request')}>
              Request
            </div>
            {
              !isAddRequest
              &&
              <>
                <div
                  className={clsx("tablinks", {
                    "active": tabLinksStatuses.Attachments.active
                  })}
                  name="Attachments"
                  onClick={() => tabclick('Attachments')}
                >
                  Attachments {requestAttachments?.length > 0 ? `(${requestAttachments.length})` : ""}
                </div>
                <div
                  className={clsx("tablinks", {
                    "active": tabLinksStatuses.Comments.active
                  })}
                  name="Comments"
                  onClick={() => tabclick('Comments')}
                >
                  Comments {requestNotes?.length > 0 ? `(${requestNotes.length})` : ""}
                </div>
              </>
            }

            <div
              className="tablinks"
              className={clsx("tablinks", {
                "active": tabLinksStatuses.Option4.active
              })}
              name="Option4"
              onClick={() => tabclick('Option4')}
            >
              Option 4
            </div>
          </div>

          <div className="foileftpanelstatus">
            {bottomTextArray.length > 0 && (_requestStatus && _requestStatus.toLowerCase().includes("days")) &&
              bottomTextArray.map(text => {
                return (
                  <h4>{text}</h4>
                )
              })
            }
          </div>


        </div>
        <div className="foitabpanelcollection">
          <div
            id="Request"
            className={clsx("tabcontent", {
              "active": tabLinksStatuses.Request.active,
              [classes.displayed]: tabLinksStatuses.Request.display,
              [classes.hidden]: !tabLinksStatuses.Request.display,
            })}
          >
            <div className="container foi-review-request-container">

              <div className="foi-review-container">
                <form className={`${classes.root} foi-request-form`} autoComplete="off">
                  <ConditionalComponent condition={(!isAddRequest && Object.entries(requestDetails).length !== 0) || isAddRequest}>
                    <>
                      <FOIRequestHeader headerValue={headerValue} requestDetails={requestDetails} handleAssignedToValue={handleAssignedToValue} createSaveRequestObject={createSaveRequestObject} handlestatusudpate={handlestatusudpate} userDetail={userDetail} disableInput={disableInput} />

                      <ApplicantDetails
                        requestDetails={requestDetails}
                        contactDetailsNotGiven={contactDetailsNotGiven}
                        handleApplicantDetailsInitialValue={handleApplicantDetailsInitialValue}
                        handleEmailValidation={handleEmailValidation}
                        handleApplicantDetailsValue={handleApplicantDetailsValue}
                        createSaveRequestObject={createSaveRequestObject}
                        disableInput={disableInput}
                      />
                      {
                        requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL &&
                        <>
                          <ChildDetails
                            additionalInfo={requestDetails.additionalPersonalInfo}
                            createSaveRequestObject={createSaveRequestObject}
                            disableInput={disableInput}
                          />
                          <OnBehalfOfDetails
                            additionalInfo={requestDetails.additionalPersonalInfo}
                            createSaveRequestObject={createSaveRequestObject}
                            disableInput={disableInput}
                          />
                        </>

                      }

                      <AddressContactDetails requestDetails={requestDetails} contactDetailsNotGiven={contactDetailsNotGiven} createSaveRequestObject={createSaveRequestObject} handleContactDetailsInitialValue={handleContactDetailsInitialValue} handleContanctDetailsValue={handleContanctDetailsValue} disableInput={disableInput} />
                      
                      <RequestDescriptionBox 
                        programAreaList={programAreaList} 
                        urlIndexCreateRequest={urlIndexCreateRequest} 
                        requestDetails={requestDetails} 
                        handleUpdatedProgramAreaList={handleUpdatedProgramAreaList} 
                        handleOnChangeRequiredRequestDescriptionValues={handleOnChangeRequiredRequestDescriptionValues} 
                        handleInitialRequiredRequestDescriptionValues={handleInitialRequiredRequestDescriptionValues} 
                        createSaveRequestObject={createSaveRequestObject} 
                        disableInput={disableInput} 
                      />
                      <RequestDetails requestDetails={requestDetails} handleRequestDetailsValue={handleRequestDetailsValue} handleRequestDetailsInitialValue={handleRequestDetailsInitialValue} createSaveRequestObject={createSaveRequestObject} disableInput={disableInput} />
                      
                      <ExtensionDetails requestDetails={requestDetails} requestState={requestState}/>
                      {
                        requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL &&
                        <AdditionalApplicantDetails
                          requestDetails={requestDetails}
                          createSaveRequestObject={createSaveRequestObject}
                          disableInput={disableInput}
                        />
                      }
                      {showDivisionalTracking && <DivisionalTracking divisions={requestDetails.divisions} />}
                      <RequestNotes />

                      <BottomButtonGroup 
                        stateChanged={stateChanged} 
                        isValidationError={isValidationError} 
                        urlIndexCreateRequest={urlIndexCreateRequest} 
                        saveRequestObject={saveRequestObject} 
                        unSavedRequest={unSavedRequest} 
                        handleSaveRequest={handleSaveRequest} 
                        handleOpenRequest={handleOpenRequest} 
                        currentSelectedStatus={_currentrequestStatus} 
                        hasStatusRequestSaved={hasStatusRequestSaved} 
                        disableInput={disableInput}
                        requestState={requestState}
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
              "active": tabLinksStatuses.Attachments.active,
              [classes.displayed]: tabLinksStatuses.Attachments.display,
              [classes.hidden]: !tabLinksStatuses.Attachments.display,
            })}
          >
            {
              !isAttachmentListLoading && (iaoassignedToList?.length > 0 || ministryAssignedToList?.length > 0) ?
                <>
                  <AttachmentSection currentUser={userId} attachmentsArray={requestAttachments}
                    setAttachments={setAttachments} requestId={requestId} ministryId={ministryId}
                    requestNumber={requestNumber} requestState={requestState}
                    iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} isMinistryCoordinator={false} />
                </> : <Loading />
            }
          </div>
          <div
            id="Comments"
            className={clsx("tabcontent", {
              "active": tabLinksStatuses.Comments.active,
              [classes.displayed]: tabLinksStatuses.Comments.display,
              [classes.hidden]: !tabLinksStatuses.Comments.display,
            })}
          >
            {
              !isLoading && requestNotes && (iaoassignedToList?.length > 0 || ministryAssignedToList?.length > 0) ?
                <>
                  <CommentSection currentUser={userId && { userId: userId, avatarUrl: avatarUrl, name: fullName }} commentsArray={requestNotes.sort(function (a, b) { return b.commentId - a.commentId; })}
                    setComment={setComment} signinUrl={signinUrl} signupUrl={signupUrl} requestid={requestId} ministryId={ministryId}
                    bcgovcode={bcgovcode} iaoassignedToList={iaoassignedToList} ministryAssignedToList={ministryAssignedToList} requestNumber={requestNumber}
                    //setEditorChange, removeComment and setRemoveComment added to handle Navigate away from Comments tabs 
                    setEditorChange={setEditorChange} removeComment={removeComment} setRemoveComment={setRemoveComment} />

                </> : <Loading />
            }


          </div>
          <div
            id="Option4"
            className={clsx("tabcontent", {
              "active": tabLinksStatuses.Option4.active,
              [classes.displayed]: tabLinksStatuses.Option4.display,
              [classes.hidden]: !tabLinksStatuses.Option4.display,
            })}
          >
            <h3>Option 4</h3>
          </div>
        </div>
      </div>
    </div>
 : <Loading/>
  );


});

export default FOIRequest;
