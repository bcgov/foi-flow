import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from "react-redux";
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Chip from "@mui/material/Chip";
import './MinistryReview.scss'
import { StateDropDown } from '../../customComponents';
import '../FOIRequestHeader/foirequestheader.scss'
import "./MinistryReviewTabbedContainer.scss";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import { push } from "connected-react-router";
import {  
  fetchFOIMinistryViewRequestDetails,
  fetchFOIRequestDescriptionList
} from "../../../../apiManager/services/FOI/foiRequestServices";

import { fetchFOIMinistryAssignedToList } from "../../../../apiManager/services/FOI/foiMasterDataServices";

import {
  fetchFOIRequestAttachmentsList,
} from "../../../../apiManager/services/FOI/foiAttachmentServices";

import {
  fetchFOIRequestNotesList
} from "../../../../apiManager/services/FOI/foiRequestNoteServices";

import {
  ConditionalComponent,
  calculateDaysRemaining,
} from "../../../../helper/FOI/helper";
import ApplicantDetails from "./ApplicantDetails";
import ChildDetails from "./ChildDetails";
import OnBehalfDetails from "./OnBehalfDetails";
import AdditionalApplicantDetails from "./AdditionalApplicantDetails";
import RequestDetails from "./RequestDetails";
import RequestDescription from "./RequestDescription";
import RequestHeader from "./RequestHeader";
import RequestTracking from "./RequestTracking";
import BottomButtonGroup from "./BottomButtonGroup";
import { CommentSection } from "../../customComponents/Comments";
import { AttachmentSection } from "../../customComponents/Attachments";
import { CFRForm } from '../../customComponents/CFRForm';
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import Loading from "../../../../containers/Loading";
import ExtensionDetails from "./ExtensionDetails";
import clsx from "clsx";
import { getMinistryBottomTextMap, alertUser, getHeaderText } from "./utils";
import DivisionalTracking from "../DivisionalTracking";

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
  btndisabled: {
    border: "none",
    backgroundColor: "#eceaea",
    color: "#FFFFFF",
  },
  btnenabled: {
    border: "none",
    backgroundColor: "#38598A",
    color: "#FFFFFF",
  },
  btnsecondaryenabled: {
    border: "1px solid #38598A",
    backgroundColor: "#FFFFFF",
    color: "#38598A",
  },
  displayed: {
    display: "block",
  },
  hidden: {
    display: "none",
  },
}));

const MinistryReview = React.memo(({ userDetail }) => {
  const { requestId, ministryId } = useParams();
  const [requestState, setRequestState] = useState();
  const [_requestStatus, setRequestStatus] = React.useState(requestState);

  const [_currentrequestStatus, setcurrentrequestStatus] = React.useState("");
  const [_tabStatus, settabStatus] = React.useState(requestState);
  //gets the request detail from the store

  let requestDetails = useSelector(
    (state) => state.foiRequests.foiMinistryViewRequestDetail
  );
  let requestNotes = useSelector(
    (state) => state.foiRequests.foiRequestComments
  );
  let requestAttachments = useSelector(
    (state) => state.foiRequests.foiRequestAttachments
  );

  const requestExtensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );

  let bcgovcode =
    ministryId && requestDetails && requestDetails["selectedMinistries"]
      ? JSON.stringify(requestDetails["selectedMinistries"][0]["code"])
      : "";
  const [comment, setComment] = useState([]);

  //editorChange and removeComment added to handle Navigate away from Comments tabs
  const [editorChange, setEditorChange] = useState(false);

  const initialStatuses = {
    Request: {
      display: false,
      active: false,
    },
    CFRForm: {
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

  const [attachments, setAttachments] = useState(requestAttachments);
  const dispatch = useDispatch();

  useEffect(() => {
    if (window.location.href.indexOf("comments") > -1) {
      tabclick("Comments");
    }
  }, []);

  useEffect(() => {
    if (ministryId) {
      dispatch(fetchFOIMinistryViewRequestDetails(requestId, ministryId));
      dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
      dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
      if (bcgovcode) dispatch(fetchFOIMinistryAssignedToList(bcgovcode));
    }
  }, [requestId, ministryId, comment, attachments]);

  const [headerValue, setHeader] = useState("");
  const [ministryAssignedToValue, setMinistryAssignedToValue] =
    React.useState("Unassigned");
  //gets the request detail from the store

  const [saveMinistryRequestObject, setSaveMinistryRequestObject] =
    React.useState(requestDetails);

  const [divstages, setdivStages] = React.useState([]);

  let ministryassignedtousername = "Unassigned";
  useEffect(() => {
    const requestDetailsValue = requestDetails;
    setSaveMinistryRequestObject(requestDetailsValue);
    ministryassignedtousername =
      requestDetailsValue && requestDetailsValue.assignedministryperson
        ? requestDetailsValue.assignedministryperson
        : "Unassigned";
    setMinistryAssignedToValue(ministryassignedtousername);
    if (requestDetails && Object.keys(requestDetails).length !== 0) {
      setRequestState(requestDetails.currentState);
      settabStatus(requestDetails.currentState);
    }
  }, [requestDetails]);

  const [unSavedRequest, setUnSavedRequest] = React.useState(false);
  const hideBottomText = [
    StateEnum.onhold.name.toLowerCase(),
    StateEnum.closed.name.toLowerCase(),
  ];

  const _cfrDaysRemaining = requestDetails.cfrDueDate
    ? calculateDaysRemaining(requestDetails.cfrDueDate)
    : "";

  const bottomTextMap = getMinistryBottomTextMap(
    requestDetails,
    requestState,
    _cfrDaysRemaining,
    requestExtensions
  );

  //gets the latest ministry assigned to value
  const handleMinistryAssignedToValue = (value) => {
    setMinistryAssignedToValue(value);
  };

  const isFalseDivStageInput = (divStageInput) =>
    divStageInput === -1 || !Boolean(divStageInput);

  const hasincompleteDivstage = divstages.some((item) => {
    // XOR or Exlusive Or operation. Returns true if only one field is set and the other is not
    return isFalseDivStageInput(item.divisionid)
      ? !isFalseDivStageInput(item.stageid)
      : isFalseDivStageInput(item.stageid);
  });

  //Variable to find if all required fields are filled or not
  const isValidationError =
    ministryAssignedToValue.toLowerCase().includes("unassigned") ||
    hasincompleteDivstage;

  const createMinistrySaveRequestObject = (propName, value, value2) => {
    const requestObject = { ...saveMinistryRequestObject };
    setUnSavedRequest(true);
    setSaveMinistryRequestObject(requestObject);
  };

  const [updateStateDropDown, setUpdateStateDropdown] = useState(false);
  const [stateChanged, setStateChanged] = useState(false);
  const handleSaveRequest = (_state, _unSaved, id) => {
    setHeader(_state);
    if (!_unSaved && ministryId && requestId) {
      setUnSavedRequest(_unSaved);
      dispatch(fetchFOIMinistryViewRequestDetails(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
      setStateChanged(false);
      setcurrentrequestStatus(_state);
      setTimeout(() => {
        dispatch(push(`/foi/ministryreview/${requestId}/ministryrequest/${ministryId}`))
        dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      }, 1000);
    } else {
      setUpdateStateDropdown(!updateStateDropDown);
      setcurrentrequestStatus(_state);
      setStateChanged(false);
    }
  };

  const handleStateChange = (currentStatus) => {
    setcurrentrequestStatus(currentStatus);
    setStateChanged(true);
  };

  const hasStatusRequestSaved = (state) => {
    settabStatus(state);
    setcurrentrequestStatus("");
  };

  var foitabheaderBG;
  const classes = useStyles();

  switch (_tabStatus) {
    case StateEnum.open.name:
      foitabheaderBG = "foitabheadercollection foitabheaderOpenBG";
      break;
    case StateEnum.closed.name:
      foitabheaderBG = "foitabheadercollection foitabheaderClosedBG";
      break;
    case StateEnum.callforrecords.name:
      foitabheaderBG = "foitabheadercollection foitabheaderCFRG";
      break;
    case StateEnum.redirect.name:
      foitabheaderBG = "foitabheadercollection foitabheaderRedirectBG";
      break;
    case StateEnum.review.name:
      foitabheaderBG = "foitabheadercollection foitabheaderReviewBG";
      break;
    case StateEnum.feeassessed.name:
      foitabheaderBG = "foitabheadercollection foitabheaderFeeBG";
      break;
    case StateEnum.consult.name:
      foitabheaderBG = "foitabheadercollection foitabheaderConsultBG";
      break;
    case StateEnum.signoff.name:
      foitabheaderBG = "foitabheadercollection foitabheaderSignoffBG";
      break;
    case StateEnum.deduplication.name:
      foitabheaderBG = "foitabheadercollection foitabheaderDeduplicationBG";
      break;
    case StateEnum.harms.name:
      foitabheaderBG = "foitabheadercollection foitabheaderHarmsBG";
      break;
    case StateEnum.onhold.name:
      foitabheaderBG = "foitabheadercollection foitabheaderOnHoldBG";
      break;
    case StateEnum.response.name:
      foitabheaderBG = "foitabheadercollection foitabheaderResponseBG";
      break;
    default:
      foitabheaderBG = "foitabheadercollection foitabheaderdefaultBG";
      break;
  }

  //Below function will handle popstate event
  const handleOnHashChange = (e) => {
    e.preventDefault();
    window.removeEventListener("beforeunload", alertUser);
  };

  React.useEffect(() => {
    if (editorChange) {
      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener("popstate", handleOnHashChange);
      window.addEventListener("beforeunload", alertUser);
      return () => {
        window.removeEventListener("popstate", handleOnHashChange);
        window.removeEventListener("beforeunload", alertUser);
      };
    }
  }, [editorChange]);

  const tabclick = (param) => {
    if (param === "Comments") {
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

  const confirmChangesLost = (positiveCallback, negativeCallback) => {
    if (
      window.confirm(
        "Are you sure you want to leave? Your changes will be lost."
      )
    ) {
      positiveCallback();
    } else {
      negativeCallback();
    }
  };

  const pubmindivstagestomain = (_divstages) => {
    saveMinistryRequestObject.divisions = _divstages;
    setdivStages(_divstages);
  };

  const userId = userDetail && userDetail.preferred_username;
  const avatarUrl = "https://ui-avatars.com/api/name=Riya&background=random";
  const name = `${userDetail && userDetail.family_name}, ${
    userDetail && userDetail.given_name
  }`;
  const signinUrl = "/signin";
  const signupUrl = "/signup";

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

  const requestNumber = requestDetails?.axisRequestId
    ? requestDetails.axisRequestId
    : requestDetails?.idNumber;

  const stateBox =
    requestState?.toLowerCase() == StateEnum.closed.name.toLowerCase() ? (
      <span className="state-box">Closed</span>
    ) : (
      <StateDropDown
        requestState={requestState}
        updateStateDropDown={updateStateDropDown}
        requestStatus={_requestStatus}
        handleStateChange={handleStateChange}
        isMinistryCoordinator={true}
        isValidationError={isValidationError}
        requestType={requestDetails?.requestType}
      />
    );

  const divisions =
    requestDetails?.divisions?.length > 0 ? requestDetails.divisions : [];
  const ministrycode =
    requestDetails?.selectedMinistries?.length > 0
      ? requestDetails.selectedMinistries[0].code
      : "";
  const divisionsBox =
    requestState?.toLowerCase() == StateEnum.closed.name.toLowerCase() ? (
      <DivisionalTracking divisions={divisions} />
    ) : (
      <RequestTracking
        pubmindivstagestomain={pubmindivstagestomain}
        existingDivStages={divisions}
        ministrycode={ministrycode}
        createMinistrySaveRequestObject={createMinistrySaveRequestObject}
      />
    );

  
  const showBreadcrumbs = useSelector((state) => state.foiRequests.showAdvancedSearch)

  return !isLoading &&
    requestDetails &&
    Object.keys(requestDetails).length !== 0 &&
    requestState != undefined ? (
    <div className="foiformcontent">
      <div className="foitabbedContainer">
        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <a href="/foi/dashboard" aria-label="dashboard link"><i className='fa fa-home' style={{fontSize:"45px", color: "white"}}></i></a>
          </div>
          <div className="foileftpaneldropdown">{stateBox}</div>

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
            {(requestDetails?.requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL && <div
              className={clsx("tablinks", {
                active: tabLinksStatuses.CFRForm.active,
              })}
              name="CFRForm"
              onClick={() => tabclick("CFRForm")}
            >
              CFR Form
            </div>)}
            <div
              className={clsx("tablinks", {
                active: tabLinksStatuses.Attachments.active,
              })}
              name="Attachments"
              onClick={() => tabclick("Attachments")}
            >
              Attachments
              {requestAttachments && requestAttachments.length > 0
                ? ` (${requestAttachments.length})`
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
              {requestNotes && requestNotes.length > 0
                ? `(${requestNotes.length})`
                : ""}
            </div>
          </div>

          <div className="foileftpanelstatus">
            <ConditionalComponent
              condition={!hideBottomText.includes(requestState?.toLowerCase())}
            >
              {Array.from(bottomTextMap.values()).map((value) => (
                <div className='remaining-days-alert'>{value}</div>
              ))}
            </ConditionalComponent>
          </div>
        </div>
        <div className="foitabpanelcollection">
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

                    <ConditionalComponent condition={showBreadcrumbs}>
                      <Breadcrumbs aria-label="breadcrumb" className="foi-breadcrumb">
                        <Chip
                          label={"Advanced Search"}
                          sx={{ backgroundColor: '#929090', color: 'white', height: 19, cursor: 'pointer' }}
                          onClick={() => dispatch(push(`/foi/dashboard`))}
                        />
                        <Chip
                          label={getHeaderText(requestDetails)}
                          sx={{ backgroundColor: '#929090', color: 'white', height: 19 }}
                        />
                      </Breadcrumbs>
                    </ConditionalComponent>
                    <ConditionalComponent condition={!showBreadcrumbs}>
                      <div style={{marginTop: 20}}></div>
                    </ConditionalComponent>
                  {Object.entries(requestDetails).length > 0 &&
                    requestDetails !== undefined && (
                      <>
                        <RequestHeader
                          requestDetails={requestDetails}
                          userDetail={userDetail}
                          handleMinistryAssignedToValue={
                            handleMinistryAssignedToValue
                          }
                          setSaveMinistryRequestObject={
                            setSaveMinistryRequestObject
                          }
                        />
                        <ApplicantDetails requestDetails={requestDetails} />
                        <ChildDetails requestDetails={requestDetails} />
                        <OnBehalfDetails requestDetails={requestDetails} />
                        <RequestDescription requestDetails={requestDetails} />
                        <RequestDetails requestDetails={requestDetails} />
                        <AdditionalApplicantDetails
                          requestDetails={requestDetails}
                        />
                        <ExtensionDetails
                          requestDetails={requestDetails}
                          requestState={requestState}
                        />
                        {divisionsBox}
                        {/* <RequestNotes /> */}
                        <BottomButtonGroup
                          requestState={requestState}
                          stateChanged={stateChanged}
                          attachmentsArray={requestAttachments}
                          isValidationError={isValidationError}
                          saveMinistryRequestObject={saveMinistryRequestObject}
                          unSavedRequest={unSavedRequest}
                          handleSaveRequest={handleSaveRequest}
                          currentSelectedStatus={_currentrequestStatus}
                          hasStatusRequestSaved={hasStatusRequestSaved}
                        />
                      </>
                    )}
                </form>
              </div>
            </div>
          </div>
          {(requestDetails?.requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL && <div
            id="CFRForm"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.CFRForm.active,
              [classes.displayed]: tabLinksStatuses.CFRForm.display,
              [classes.hidden]: !tabLinksStatuses.CFRForm.display,
            })}
          >
            <CFRForm            
              requestNumber={requestNumber}
              userDetail={userDetail}
              ministryId={ministryId}
            />
          </div>)}
          <div
            id="Attachments"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Attachments.active,
              [classes.displayed]: tabLinksStatuses.Attachments.display,
              [classes.hidden]: !tabLinksStatuses.Attachments.display,
            })}
          >
            {!isAttachmentListLoading &&
            iaoassignedToList &&
            iaoassignedToList.length > 0 &&
            ministryAssignedToList &&
            ministryAssignedToList.length > 0 ? (
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
                  isMinistryCoordinator={true}
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
            iaoassignedToList.length > 0 ||
            ministryAssignedToList.length > 0 ? (
              <>
                <CommentSection
                  currentUser={
                    userId && {
                      userId: userId,
                      avatarUrl: avatarUrl,
                      name: name,
                    }
                  }
                  commentsArray={requestNotes.sort(function (a, b) {
                    return b.commentId - a.commentId;
                  })}
                  setComment={setComment}
                  signinUrl={signinUrl}
                  signupUrl={signupUrl}
                  bcgovcode={bcgovcode}
                  requestid={requestId}
                  ministryId={ministryId}
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
        </div>
      </div>
    </div>
  ) : (
    <Loading />
  );
});

export default MinistryReview
