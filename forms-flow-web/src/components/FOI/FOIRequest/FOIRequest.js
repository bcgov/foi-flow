import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import Chip from "@mui/material/Chip";
import "./foirequest.scss";
import FOIRequestHeader from "./FOIRequestHeader";
import ApplicantDetails from "./ApplicantDetails";
import ChildDetails from "./ChildDetails";
import OnBehalfOfDetails from "./OnBehalfOfDetails";
import AddressContactDetails from "./AddressContanctInfo";
import RequestDescriptionBox from "./RequestDescriptionBox";
import RequestDetails from "./RequestDetails";
import ExtensionDetails from "./ExtensionDetails";
import AdditionalApplicantDetails from "./AdditionalApplicantDetails";
import BottomButtonGroup from "./BottomButtonGroup";
import { useParams } from "react-router-dom";
import {
  fetchFOICategoryList,
  fetchFOIProgramAreaList,
  fetchFOIAssignedToList,
  fetchFOIDeliveryModeList,
  fetchFOIReceivedModeList,
  fetchClosingReasonList,
  fetchFOIMinistryAssignedToList,
  fetchFOISubjectCodeList,
  fetchFOIPersonalDivisionsAndSections,
  fetchOIPCOutcomes,
  fetchOIPCStatuses,
  fetchOIPCReviewtypes,
  fetchOIPCInquiryoutcomes
} from "../../../apiManager/services/FOI/foiMasterDataServices";
import {
  fetchFOIRequestDetailsWrapper,
  fetchFOIRequestDescriptionList,
  fetchRequestDataFromAxis,
  fetchRestrictedRequestCommentTagList,
  deleteOIPCDetails
} from "../../../apiManager/services/FOI/foiRequestServices";
import { fetchFOIRequestAttachmentsList } from "../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchCFRForm } from "../../../apiManager/services/FOI/foiCFRFormServices";
import {
  fetchApplicantCorrespondence,
  fetchApplicantCorrespondenceTemplates,
} from "../../../apiManager/services/FOI/foiCorrespondenceServices";
import { fetchFOIRequestNotesList } from "../../../apiManager/services/FOI/foiRequestNoteServices";
import {
  fetchFOIRecords,
  fetchPDFStitchStatusForHarms,
  fetchRedactedSections,
  fetchPDFStitchStatusForRedlines,
  fetchPDFStitchStatusForResponsePackage,
  fetchPDFStitchedStatusForOIPCRedlineReview,
  fetchPDFStitchedStatusForOIPCRedline,
} from "../../../apiManager/services/FOI/foiRecordServices";
import { makeStyles } from "@material-ui/core/styles";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { push } from "connected-react-router";
import { StateDropDown } from "../customComponents";
import "./TabbedContainer.scss";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { CommentSection } from "../customComponents/Comments";
import { AttachmentSection } from "../customComponents/Attachments";
import { CFRForm } from "../customComponents/CFRForm";
import { ContactApplicant } from "../customComponents/ContactApplicant";
import Loading from "../../../containers/Loading";
import clsx from "clsx";
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
  getUniqueIdentifier,
} from "./utils";
import {
  ConditionalComponent,
  formatDate,
  isRequestRestricted,
} from "../../../helper/FOI/helper";
import DivisionalTracking from "./DivisionalTracking";
import RedactionSummary from "./RedactionSummary";
import AxisDetails from "./AxisDetails/AxisDetails";
import AxisMessageBanner from "./AxisDetails/AxisMessageBanner";
import { toast } from "react-toastify";
import HomeIcon from "@mui/icons-material/Home";
import { RecordsLog } from "../customComponents/Records";
import { UnsavedModal } from "../customComponents";
import { DISABLE_GATHERINGRECORDS_TAB } from "../../../constants/constants";
import _ from "lodash";
import { MinistryNeedsScanning } from "../../../constants/FOI/enum";
import OIPCDetails from "./OIPCDetails/Index";
import useOIPCHook from "./OIPCDetails/oipcHook";

const useStyles = makeStyles((theme) => ({
  root: {
    "& .MuiTextField-root": {
      margin: theme.spacing(1, "0px"),
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
  let requestAttachments = useSelector((state) =>
    state.foiRequests.foiRequestAttachments.filter((attachment) => {
      return (
        [
          "fee estimate - payment receipt",
          "response-onhold",
          "fee balance outstanding - payment receipt",
        ].indexOf(attachment.category.toLowerCase()) === -1
      );
    })
  );
  let applicantCorrespondence = useSelector(
    (state) => state.foiRequests.foiRequestApplicantCorrespondence
  );
  let applicantCorrespondenceTemplates = useSelector(
    (state) => state.foiRequests.foiRequestApplicantCorrespondenceTemplates
  );
  let CFRFormHistoryLength = useSelector(
    (state) => state.foiRequests.foiRequestCFRFormHistory.length
  );
  // let requestRecords = useSelector(
  //   (state) => state.foiRequests.foiRequestRecords
  // );
  const [attachments, setAttachments] = useState(requestAttachments);
  const [comment, setComment] = useState([]);
  const [requestState, setRequestState] = useState(StateEnum.unopened.name);
  const [disableInput, setDisableInput] = useState(requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase() && !requestDetails?.isoipcreview);
  const [_tabStatus, settabStatus] = React.useState(requestState);
  let foitabheaderBG = getTabBG(_tabStatus, requestState);

  const [unsavedPrompt, setUnsavedPrompt] = useState(false);
  const [unsavedMessage, setUnsavedMessage] = useState(<></>);
  const handleUnsavedContinue = () => {
    window.removeEventListener("popstate", handleOnHashChange);
    window.removeEventListener("beforeunload", handleBeforeUnload);
    dispatch(push(`/foi/dashboard`));
  };

  const returnToQueue = (e) => {
    if (unSavedRequest) {
      setUnsavedMessage(
        <>Are you sure you want to leave? Your changes will be lost.</>
      );
      setUnsavedPrompt(true);
    } else if (recordsUploading) {
      setUnsavedMessage(
        <>
          Are you sure you want to leave? Records are currently in the process
          of being uploaded.
          <br /> If you continue they will not be saved.
        </>
      );
      setUnsavedPrompt(true);
    } else {
      dispatch(push(`/foi/dashboard`));
    }
  };

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
    CFRForm: {
      display: false,
      active: false,
    },
    ContactApplicant: {
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

  const [saveRequestObject, setSaveRequestObject] =
    React.useState(requestDetails);
  const showDivisionalTracking =
    requestDetails &&
    requestDetails.divisions?.length > 0 &&
    requestState &&
    requestState.toLowerCase() !== StateEnum.open.name.toLowerCase() &&
    requestState.toLowerCase() !==
      StateEnum.intakeinprogress.name.toLowerCase();
  const [axisSyncedData, setAxisSyncedData] = useState({});
  const [checkExtension, setCheckExtension] = useState(true);
  let bcgovcode = getBCgovCode(ministryId, requestDetails);
  const [headerText, setHeaderText] = useState(
    getHeaderText({ requestDetails, ministryId, requestState })
  );
  document.title =
    requestDetails.axisRequestId || requestDetails.idNumber || headerText;
  const dispatch = useDispatch();
  const [isIAORestricted, setIsIAORestricted] = useState(false);
  const [redactedSections, setRedactedSections] = useState("");
  const [isMCFPersonal, setIsMCFPersonal] = useState(bcgovcode.replaceAll('"', '') == "MCF" && requestDetails.requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL);
  const {oipcData, addOIPC, removeOIPC, updateOIPC, isOIPCReview, setIsOIPCReview, removeAllOIPCs} = useOIPCHook();
  const [oipcDataInitial, setOipcDataInitial] = useState(oipcData);
  
  //Update disableInput when requestState changes
  useEffect(() => {
    setDisableInput(requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase() && !isOIPCReview);
  }, [requestState, isOIPCReview])

  useEffect(() => {
    if (!oipcDataInitial) {
      setOipcDataInitial(oipcData);
      return;
    }
    //check to see if oipcData has been updated, if so, enable save button
    if (JSON.stringify(oipcData) != JSON.stringify(oipcDataInitial)) {
      setDisableInput(false)
    }
  }, [oipcData]);

  useEffect(() => {
    if (window.location.href.indexOf("comments") > -1) {
      tabclick("Comments");
    } else if (window.location.href.indexOf("records") > -1) {
      tabclick("Records");
    }
  }, []);

  useEffect(async () => {
    if (isAddRequest) {
      dispatch(fetchFOIAssignedToList("", "", ""));
      dispatch(fetchFOIProgramAreaList());
    } else {
      await Promise.all([
        dispatch(fetchFOIProgramAreaList()),
        dispatch(fetchFOIRequestDetailsWrapper(requestId, ministryId)),
        dispatch(fetchFOIRequestDescriptionList(requestId, ministryId)),
      ]);
      dispatch(fetchFOIRequestNotesList(requestId, ministryId));
      dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
      dispatch(fetchFOIRecords(requestId, ministryId));
      dispatch(fetchPDFStitchStatusForHarms(requestId, ministryId));
      dispatch(fetchPDFStitchStatusForRedlines(requestId, ministryId));
      dispatch(fetchPDFStitchStatusForResponsePackage(requestId, ministryId));
      dispatch(fetchPDFStitchedStatusForOIPCRedline(requestId, ministryId));
      dispatch(fetchPDFStitchedStatusForOIPCRedlineReview(requestId, ministryId));
      fetchCFRForm(ministryId, dispatch);
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
      dispatch(fetchApplicantCorrespondenceTemplates());
      dispatch(
        fetchRedactedSections(ministryId, (_err, res) => {
          setRedactedSections(res.sections);
        })
      );
    }

    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
    dispatch(fetchFOISubjectCodeList());
    dispatch(fetchClosingReasonList());
    
    dispatch(fetchOIPCOutcomes());
    dispatch(fetchOIPCStatuses());
    dispatch(fetchOIPCReviewtypes());
    dispatch(fetchOIPCInquiryoutcomes());

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
      setHeaderText(
        getHeaderText({ requestDetails, ministryId, requestState })
      );
      requestDetails.linkedRequests = !!requestDetails.linkedRequests
        ? typeof requestDetails.linkedRequests == "string"
          ? JSON.parse(requestDetails.linkedRequests)
          : requestDetails.linkedRequests
        : [];
      if (requestDetails.axisRequestId) axisBannerCheck();
      setIsIAORestricted(isRequestRestricted(requestDetails, ministryId));
    }

    if(MinistryNeedsScanning.includes(bcgovcode.replaceAll('"', '')) && requestDetails.requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL) {
      dispatch(fetchFOIPersonalDivisionsAndSections(bcgovcode.replaceAll('"', '')));
      if(bcgovcode.replaceAll('"', '') == "MCF") {
        setIsMCFPersonal(true);
      }
    }
    if(requestDetails.isoipcreview) {
      setIsOIPCReview(true);
    } else {
      setIsOIPCReview(false);
    }
  }, [requestDetails]);

  //useEffect to manage isoipcreview attribute for requestdetails state
  useEffect(() => {
    if(Object.keys(requestDetails).length !== 0 && oipcData?.length <= 0) {
      requestDetails.isoipcreview = false;
      setIsOIPCReview(false);
    }
  }, [oipcData])

  
  useEffect(() => {
    if (isIAORestricted)
      dispatch(fetchRestrictedRequestCommentTagList(requestId, ministryId));
  }, [isIAORestricted]);

  useEffect(() => {
    if (checkExtension && Object.entries(axisSyncedData).length !== 0) {
      let axisDataUpdated = extensionComparison(axisSyncedData, "Extensions");
      if (axisDataUpdated) setAxisMessage("WARNING");
      else setAxisMessage("");
    }
  }, [axisSyncedData, requestExtensions, checkExtension]);

  const axisBannerCheck = () => {
    dispatch(
      fetchRequestDataFromAxis(
        requestDetails.axisRequestId,
        saveRequestObject,
        true,
        (err, data) => {
          if (!err) {
            if (typeof data !== "string" && Object.entries(data).length > 0) {
              data["linkedRequests"] =
                typeof data["linkedRequests"] == "string"
                  ? JSON.parse(data["linkedRequests"])
                  : data["linkedRequests"];
              setAxisSyncedData(data);
              let axisDataUpdated = checkIfAxisDataUpdated(data);
              if (axisDataUpdated) {
                setCheckExtension(false);
                setAxisMessage("WARNING");
              } else {
                setAxisMessage("");
              }
            } else if (data) {
              let responseMsg = data;
              responseMsg += "";
              if (
                responseMsg.indexOf(
                  "Exception happened while GET operations of request"
                ) >= 0
              )
                setAxisMessage("ERROR");
            }
          } else {
            setAxisMessage("ERROR");
          }
        }
      )
    );
  };

  const checkIfAxisDataUpdated = (axisData) => {
    let updateNeeded = false;
    for (let key of Object.keys(axisData)) {
      let updatedField = isAxisSyncDisplayField(key);
      if (key !== "Extensions" && updatedField)
        updateNeeded = checkValidation(key, axisData);
      if (updateNeeded) {
        return true;
      }
    }
    return false;
  };

  const checkValidation = (key, axisData) => {
    let mandatoryField = isMandatoryField(key);
    if (key === "additionalPersonalInfo") {
      if (axisData.requestType === "personal") {
        let foiReqAdditionalPersonalInfo = requestDetails[key];
        let axisAdditionalPersonalInfo = axisData[key];
        for (let axisKey of Object.keys(axisAdditionalPersonalInfo)) {
          for (let reqKey of Object.keys(foiReqAdditionalPersonalInfo)) {
            if (axisKey === reqKey) {
              if (
                axisAdditionalPersonalInfo[axisKey] !==
                foiReqAdditionalPersonalInfo[axisKey]
              ) {
                return true;
              }
            }
          }
        }
      }
    } else if (
      key === "compareReceivedDate" &&
      requestDetails["receivedDate"] !== axisData[key] &&
      requestDetails["receivedDate"] !== axisData["receivedDate"]
    ) {
      return true;
    } else if (key === "linkedRequests") {
      if (linkedRequestsChanged(axisData, key) > 0) {
        return true;
      }
    } else if (
      key !== "compareReceivedDate" &&
      ((mandatoryField && axisData[key]) || !mandatoryField)
    ) {
      if (
        (requestDetails[key] || axisData[key]) &&
        requestDetails[key] != axisData[key]
      )
        return true;
    }
    return false;
  };

  const linkedRequestsChanged = (axisData, key) => {
    let dblinkedRequests = requestDetails[key]?.map((val) =>
      Object.keys(val).toString()
    );
    let axislinkedRequests =
      typeof axisData[key] == "string"
        ? JSON.parse(axisData[key])
        : axisData[key];
    let linkedRequestsJson = axislinkedRequests.map((val) =>
      Object.keys(val).toString()
    );
    if (linkedRequestsJson?.length != dblinkedRequests?.length) return true;
    if (
      linkedRequestsJson.filter((x) => !dblinkedRequests?.includes(x))?.length >
      0
    )
      return true;
    if (
      dblinkedRequests.filter((x) => !linkedRequestsJson?.includes(x))?.length >
      0
    )
      return true;
    return false;
  };

  const extensionComparison = (axisData, key) => {
    if (requestExtensions.length !== axisData[key].length) return true;
    let axisUniqueIds = [];
    let foiUniqueIds = [];
    axisData[key]?.forEach((axisObj) => {
      axisUniqueIds.push(
        (
          axisObj.extensionstatusid +
          formatDate(axisObj.extendedduedate, "MMM dd yyyy") +
          axisObj.extensionreasonid
        ).replace(/\s+/g, "")
      );
    });
    requestExtensions.forEach((obj) => {
      foiUniqueIds.push(
        (
          obj.extensionstatusid +
          formatDate(obj.extendedduedate, "MMM dd yyyy") +
          obj.extensionreasonid
        ).replace(/\s+/g, "")
      );
    });
    if (axisUniqueIds.filter((x) => !foiUniqueIds.includes(x))?.length > 0) {
      return true;
    }

    if (requestExtensions.length > 0 && axisData[key].length > 0) {
      for (let axisObj of axisData[key]) {
        for (let foiReqObj of requestExtensions) {
          if (getUniqueIdentifier(axisObj) === getUniqueIdentifier(foiReqObj)) {
            if (
              axisObj.extensionstatusid !== foiReqObj.extensionstatusid ||
              axisObj.extendedduedays !== foiReqObj.extendedduedays ||
              !(
                foiReqObj.decisiondate === axisObj.approveddate ||
                foiReqObj.decisiondate === axisObj.denieddate
              )
            ) {
              return true;
            }
          }
        }
      }
    } else {
      if (axisData[key]?.length > 0) return true;
    }
    return false;
  };

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
    requestState: "",
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
  const [CFRUnsaved, setCFRUnsaved] = React.useState(false);
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

  const saveOIPCNoReview = () => {
    removeAllOIPCs();
    setIsOIPCReview(false);
    dispatch(
      deleteOIPCDetails(
        requestId,
        ministryId, 
        (err, _res) => {
        if(!err) {
          toast.success("OIPC details have been saved successfully.", {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
        } else {
          toast.error(
            "Temporarily unable to save the OIPC details. Please try again in a few minutes.",
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
      })
    )
  }

  const oipcSectionRef = React.useRef(null);
  const handleOipcReviewFlagChange = (isSelected) => {
    if (!isSelected) {
      saveOIPCNoReview();
    } else {
      setIsOIPCReview(isSelected);
      requestDetails.isoipcreview = isSelected;
      oipcSectionRef.current.scrollIntoView();
      //timeout to allow react state to update after setState call
      setTimeout(() => {
        oipcSectionRef.current.scrollIntoView();
      }, (10));
    }
  }

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
    requiredAxisDetails,
    isAddRequest,
    _currentrequestStatus,
    oipcData,
    requestDetails.isoipcreview,
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
    if (name !== "assignedTo") {
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
      dispatch(fetchFOIRequestAttachmentsList(id || requestId, ministryId));
      fetchCFRForm(ministryId, dispatch);
      dispatch(fetchApplicantCorrespondence(requestId, ministryId));
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
      sessionStorage.setItem("foicommentcategory", 1);
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

  const showAdvancedSearch = useSelector(
    (state) => state.foiRequests.showAdvancedSearch
  );
  const showEventQueue = useSelector(
    (state) => state.foiRequests.showEventQueue
  );

  const showRecordsTab = () => {
    return (
      requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      (requestDetails?.divisions?.length > 0 || isMCFPersonal) &&
      DISABLE_GATHERINGRECORDS_TAB?.toLowerCase() =='false'
    );
  };

  const disableBannerForClosed = () => {
    if (
      stateTransition?.find(
        ({ status }) =>
          status?.toLowerCase() ===
          StateEnum.intakeinprogress.name.toLowerCase()
      )
    ) {
      if (axisMessage === "WARNING") setAxisMessage("");
      return true;
    }
    return false;
  };

  const showCFRTab = () => {
    return (
      requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      requestDetails?.requestType ===
        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL
    );
  };

  const showContactApplicantTab = () => {
    return (
      requestState !== StateEnum.intakeinprogress.name &&
      requestState !== StateEnum.unopened.name &&
      requestState !== StateEnum.open.name &&
      requestState !== StateEnum.appfeeowing.name &&
      requestDetails?.requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL)
  }

  return (!isLoading &&
    requestDetails &&
    Object.keys(requestDetails).length !== 0) ||
    isAddRequest ? (
    <div
      className={`foiformcontent ${
        axisMessage === "WARNING" &&
        !disableBannerForClosed() &&
        "request-scrollbar-height"
      }`}
    >
      <div className="foitabbedContainer">
        <div className={foitabheaderBG}>
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
              isDivisionalCoordinator={false}
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
                {showCFRTab() && (
                  <div
                    className={clsx("tablinks", {
                      active: tabLinksStatuses.CFRForm.active,
                    })}
                    name="CFRForm"
                    onClick={() => tabclick("CFRForm")}
                  >
                    CFR Form
                    {CFRFormHistoryLength > 0
                      ? ` (${CFRFormHistoryLength})`
                      : ""}
                  </div>
                )}
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
                {showRecordsTab() && (
                  <div
                    className={clsx("tablinks", {
                      active: tabLinksStatuses.Records.active,
                    })}
                    name="Records"
                    onClick={() => tabclick("Records")}
                  >
                    Records
                  </div>
                )}
                {showContactApplicantTab() && (
                  <div
                    className={clsx("tablinks", {
                      active: tabLinksStatuses.ContactApplicant.active,
                    })}
                    name="ContactApplicant"
                    onClick={() => tabclick("ContactApplicant")}
                  >
                    Contact Applicant{" "}
                    {applicantCorrespondence?.length > 0
                      ? `(${applicantCorrespondence.length})`
                      : ""}
                  </div>
                )}
              </>
            )}
          </div>

          <div className="foileftpanelstatus">
            {isOIPCReview && requestDetails.isreopened ? "" 
            : bottomTextArray.length > 0 &&
              _requestStatus &&
              _requestStatus.toLowerCase().includes("days") &&
              bottomTextArray.map((text) => {
                return <div className="remaining-days-alert">{text}</div>;
              })}
          </div>
        </div>
        <div className="foitabpanelcollection">
          {requestState !== StateEnum.intakeinprogress.name &&
            !disableBannerForClosed() && (
              <AxisMessageBanner
                axisMessage={axisMessage}
                requestDetails={requestDetails}
              />
            )}
          <div
            id="Request"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Request.active,
              [classes.displayed]: tabLinksStatuses.Request?.display,
              [classes.hidden]: !tabLinksStatuses.Request?.display,
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
                    <Breadcrumbs
                      aria-label="breadcrumb"
                      className="foi-breadcrumb"
                    >
                      {showEventQueue && !showAdvancedSearch && (
                        <Chip
                          label={"Event Queue"}
                          sx={{
                            backgroundColor: "#fff",
                            border: "1px solid #038",
                            color: "#038",
                            height: 19,
                            cursor: "pointer",
                          }}
                          onClick={returnToQueue}
                        />
                      )}
                      {showAdvancedSearch && !showEventQueue && (
                        <Chip
                          label={"Advanced Search"}
                          sx={{
                            backgroundColor: "#fff",
                            border: "1px solid #038",
                            color: "#038",
                            height: 19,
                            cursor: "pointer",
                          }}
                          onClick={returnToQueue}
                        />
                      )}

                      {!showAdvancedSearch && !showEventQueue && (
                        <Chip
                          icon={
                            <HomeIcon
                              fontSize="small"
                              sx={{ color: "#038 !important" }}
                            />
                          }
                          label={"Request Queue"}
                          sx={{
                            backgroundColor: "#fff",
                            border: "1px solid #038",
                            color: "#038",
                            height: 19,
                            cursor: "pointer",
                          }}
                          onClick={returnToQueue}
                        />
                      )}
                      <Chip
                        label={headerText}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                        }}
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
                        isMinistry={false}
                        isAddRequest={isAddRequest}
                        handleOipcReviewFlagChange={handleOipcReviewFlagChange}
                        showOipcReviewFlag={requestState.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase() && requestState.toLowerCase() !== StateEnum.unopened.name.toLowerCase()}
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
                            requestType={requestDetails?.requestType}
                          />
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

                      {redactedSections.length > 0 && (
                        <RedactionSummary sections={redactedSections} />
                      )}

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
                      <div ref={oipcSectionRef}></div>
                      {isOIPCReview && requestState && requestState.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase() && requestState.toLowerCase() !== StateEnum.unopened.name.toLowerCase() && (
                        <OIPCDetails 
                          oipcData={oipcData}
                          updateOIPC={updateOIPC}
                          addOIPC={addOIPC}
                          removeOIPC={removeOIPC}
                          isMinistry={false}
                        />
                      )}

                      <BottomButtonGroup
                        stateChanged={stateChanged}
                        isValidationError={isValidationError}
                        urlIndexCreateRequest={urlIndexCreateRequest}
                        saveRequestObject={saveRequestObject}
                        unSavedRequest={unSavedRequest}
                        recordsUploading={recordsUploading}
                        CFRUnsaved={CFRUnsaved}
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
                        attachmentsArray={requestAttachments}
                        oipcData={oipcData}
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
              [classes.displayed]: tabLinksStatuses.Attachments?.display,
              [classes.hidden]: !tabLinksStatuses.Attachments?.display,
            })}
          >
            {!isAttachmentListLoading ? (
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
          {showCFRTab() && (
            <div
              id="CFRForm"
              className={clsx("tabcontent", {
                active: tabLinksStatuses.CFRForm.active,
                [classes.displayed]: tabLinksStatuses.CFRForm?.display,
                [classes.hidden]: !tabLinksStatuses.CFRForm?.display,
              })}
            >
              <CFRForm
                requestNumber={requestNumber}
                requestState={requestState}
                userDetail={userDetail}
                ministryId={ministryId}
                requestId={requestId}
                setCFRUnsaved={setCFRUnsaved}
              />
            </div>
          )}
          <div
            id="Comments"
            className={clsx("tabcontent", {
              active: tabLinksStatuses.Comments.active,
              [classes.displayed]: tabLinksStatuses.Comments?.display,
              [classes.hidden]: !tabLinksStatuses.Comments?.display,
            })}
          >
            {!isLoading && requestNotes ? (
              <>
                {url.indexOf("comments") > -1 ? (
                  <Breadcrumbs
                    aria-label="breadcrumb"
                    className="foi-breadcrumb foi-breadcrumb-comments"
                  >
                    {showEventQueue && !showAdvancedSearch && (
                      <Chip
                        label={"Event Queue"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}
                    {showAdvancedSearch && !showEventQueue && (
                      <Chip
                        label={"Advanced Search"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}

                    {!showAdvancedSearch && !showEventQueue && (
                      <Chip
                        icon={
                          <HomeIcon
                            fontSize="small"
                            sx={{ color: "#038 !important" }}
                          />
                        }
                        label={"Request Queue"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}
                    <Chip
                      label={headerText}
                      sx={{
                        backgroundColor: "#fff",
                        border: "1px solid #038",
                        color: "#038",
                        height: 19,
                      }}
                    />
                  </Breadcrumbs>
                ) : null}
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
                  restrictionType={
                    isRequestRestricted(requestDetails, ministryId) ? "iao" : ""
                  }
                  isRestricted={isRequestRestricted(requestDetails, ministryId)}
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
            {showRecordsTab() && (
              <>
                {url.indexOf("records") > -1 ? (
                  <Breadcrumbs
                    aria-label="breadcrumb"
                    className="foi-breadcrumb foi-breadcrumb-comments"
                  >
                    {showEventQueue && !showAdvancedSearch && (
                      <Chip
                        label={"Event Queue"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}
                    {showAdvancedSearch && !showEventQueue && (
                      <Chip
                        label={"Advanced Search"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}

                    {!showAdvancedSearch && !showEventQueue && (
                      <Chip
                        icon={
                          <HomeIcon
                            fontSize="small"
                            sx={{ color: "#038 !important" }}
                          />
                        }
                        label={"Request Queue"}
                        sx={{
                          backgroundColor: "#fff",
                          border: "1px solid #038",
                          color: "#038",
                          height: 19,
                          cursor: "pointer",
                        }}
                        onClick={returnToQueue}
                      />
                    )}
                    <Chip
                      label={headerText}
                      sx={{
                        backgroundColor: "#fff",
                        border: "1px solid #038",
                        color: "#038",
                        height: 19,
                      }}
                    />
                  </Breadcrumbs>
                ) : null}
                <RecordsLog
                  //recordsObj={requestRecords}
                  requestId={requestId}
                  ministryId={ministryId}
                  requestNumber={requestNumber}
                  iaoassignedToList={iaoassignedToList}
                  ministryAssignedToList={ministryAssignedToList}
                  isMinistryCoordinator={false}
                  bcgovcode={JSON.parse(bcgovcode)}
                  setRecordsUploading={setRecordsUploading}
                  divisions={requestDetails.divisions}
                  recordsTabSelect={tabLinksStatuses.Records.active}
                  requestType={requestDetails?.requestType}
                />
              </>
            )}
          </div>
          {showContactApplicantTab() && (
            <div
              id="ContactApplicant"
              className={clsx("tabcontent", {
                active: tabLinksStatuses.ContactApplicant.active,
                [classes.displayed]: tabLinksStatuses.ContactApplicant?.display,
                [classes.hidden]: !tabLinksStatuses.ContactApplicant?.display,
              })}
            >
              {!isLoading && applicantCorrespondence ? (
                <>
                  <ContactApplicant
                    requestNumber={requestNumber}
                    requestState={requestState}
                    userDetail={userDetail}
                    ministryId={ministryId}
                    ministryCode={requestDetails.bcgovcode}
                    applicantCorrespondence={applicantCorrespondence}
                    applicantCorrespondenceTemplates={
                      applicantCorrespondenceTemplates
                    }
                    requestId={requestId}
                  />
                </>
              ) : (
                <Loading />
              )}
            </div>
          )}
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
