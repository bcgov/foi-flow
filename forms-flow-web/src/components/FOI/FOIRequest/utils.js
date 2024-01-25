import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { formatDate, isProcessingTeam, isFlexTeam } from "../../../helper/FOI/helper";
import { extensionStatusId, KCProcessingTeams } from "../../../constants/FOI/enum";
import MANDATORY_FOI_REQUEST_FIELDS from '../../../constants/FOI/mandatoryFOIRequestFields';
import AXIS_SYNC_DISPLAY_FIELDS from '../../../constants/FOI/axisSyncDisplayFields';

export const getTabBottomText = ({
  _daysRemaining,
  _cfrDaysRemaining,
  _status,
  requestExtensions,
}) => {
  const _daysRemainingText = getDaysRemainingText(_daysRemaining);
  const _cfrDaysRemainingText = getcfrDaysRemainingText(_cfrDaysRemaining);
  const _extensionsCountText = getExtensionsCountText(requestExtensions);

  let bottomTextArray = []

  const statusesToNotAppearIn = [
    StateEnum.unopened.name,
    StateEnum.onhold.name,
    StateEnum.closed.name,
    StateEnum.intakeinprogress.name,
    StateEnum.redirect.name,
  ];

  if (!statusesToNotAppearIn.includes(_status)) {
    bottomTextArray.push(_daysRemainingText);
    bottomTextArray.push(_extensionsCountText);
  }

  const cfrStates = [
    StateEnum.callforrecords.name,
    StateEnum.feeassessed.name,
    StateEnum.deduplication.name,
    StateEnum.harms.name,
  ];

  if (cfrStates.includes(_status)) {
    if (bottomTextArray.length === 0) {
      bottomTextArray.push(_cfrDaysRemainingText);
    } else {
      bottomTextArray.splice(1, 0, _cfrDaysRemainingText);
    }
  }

  return bottomTextArray.join('|');
};

const getDaysRemainingText = (_daysRemaining) => {
  return _daysRemaining >= 0
    ? `${_daysRemaining} Days Remaining`
    : `${Math.abs(_daysRemaining)} Days Overdue`;
};

const getcfrDaysRemainingText = (_cfrDaysRemaining) => {  
     return`CFR Due in ${_cfrDaysRemaining} Days`    
};

export const isBeforeOpen = (requestDetails) => {
  return !requestDetails.stateTransition?.filter(s => s.status === StateEnum.open.name).length > 0;
};

export const getExtensionsCountText = (extensions) => {
  if (!extensions || extensions.length < 1) {
    return `Extensions 0`;
  }

  const approved = extensions.filter(
    (extension) => extension.extensionstatusid === extensionStatusId.approved
  ).length;

  const pending = extensions.filter(
    (extension) => extension.extensionstatusid === extensionStatusId.pending
  ).length;

  return [`Extensions ${approved || 0}`, pending ? ` (${pending})` : null].join(
    ""
  );
};

export const confirmChangesLost = (positiveCallback, negativeCallback) => {
  if (
    window.confirm("Are you sure you want to leave? Your changes will be lost.")
  ) {
    positiveCallback();
  } else {
    negativeCallback();
  }
};

export const getRedirectAfterSaveUrl = (ministryId, requestId) => {
  if (ministryId) {
    return `/foi/foirequests/${requestId}/ministryrequest/${ministryId}`;
  }

  if (requestId) {
    return `/foi/reviewrequest/${requestId}`;
  }

  return null;
};

export const getTabBG = (_tabStatus, _requestState) => {
  if (!_tabStatus && _requestState) _tabStatus = _requestState;
  switch (_tabStatus) {
    case StateEnum.intakeinprogress.name:
      return "foitabheadercollection foitabheaderIntakeInProgressBG";
    case StateEnum.open.name:
      return "foitabheadercollection foitabheaderOpenBG";
    case StateEnum.closed.name:
      return "foitabheadercollection foitabheaderClosedBG";
    case StateEnum.callforrecords.name:
      return "foitabheadercollection foitabheaderCFRG";
    case StateEnum.redirect.name:
      return "foitabheadercollection foitabheaderRedirectBG";
    case StateEnum.review.name:
      return "foitabheadercollection foitabheaderReviewBG";
    case StateEnum.feeassessed.name:
      return "foitabheadercollection foitabheaderFeeBG";
    case StateEnum.consult.name:
      return "foitabheadercollection foitabheaderConsultBG";
    case StateEnum.signoff.name:
      return "foitabheadercollection foitabheaderSignoffBG";
    case StateEnum.deduplication.name:
      return "foitabheadercollection foitabheaderDeduplicationBG";
    case StateEnum.harms.name:
      return "foitabheadercollection foitabheaderHarmsBG";
    case StateEnum.onhold.name:
      return "foitabheadercollection foitabheaderOnHoldBG";
    case StateEnum.response.name:
      return "foitabheadercollection foitabheaderResponseBG";
    case StateEnum.peerreview.name:
      return "foitabheadercollection foitabheaderPeerreviewBG";
    case StateEnum.tagging.name:
        return "foitabheadercollection foitabheaderTaggingBG"; 
    case StateEnum.readytoscan.name:
        return "foitabheadercollection foitabheaderReadytoScanBG";
    case StateEnum.section5pending.name:
      return "foitabheadercollection foitabheaderSection5Pending";            
    case StateEnum.appfeeowing.name:
        return "foitabheadercollection foitabheaderAppFeeOwingBG";

    default:
      return "foitabheadercollection foitabheaderdefaultBG";
  }
};

export const assignValue = (jsonObj, value, name) => {
  let _obj = { ...jsonObj };
  if (_obj[name] !== undefined) {
    _obj[name] = value;
  }
  return _obj;
};

export const updateAdditionalInfo = (name, value, requestObject) => {
  if (!requestObject.additionalPersonalInfo) {
    requestObject.additionalPersonalInfo = {
      alsoKnownAs: "",
      birthDate: "",
      childFirstName: "",
      childMiddleName: "",
      childLastName: "",
      childAlsoKnownAs: "",
      childBirthDate: "",
      anotherFirstName: "",
      anotherMiddleName: "",
      anotherLastName: "",
      anotherAlsoKnownAs: "",
      anotherBirthDate: "",
      adoptiveMotherFirstName: "",
      adoptiveMotherLastName: "",
      adoptiveFatherLastName: "",
      adoptiveFatherFirstName: "",
      personalHealthNumber: "",
      //identityVerified: "",
    };
  }
  requestObject.additionalPersonalInfo[name] = value;
  return requestObject;
};

export const createAssigneeDetails = (value, value2) => {
  const assigneeObject = {
    assignedGroup: "",
    assignedTo: "",
    assignedToFirstName: "",
    assignedToLastName: "",
    assignedToName: ""
  }
  const assignedTo = value.split("|");
      if (
        FOI_COMPONENT_CONSTANTS.ASSIGNEE_GROUPS.find(
          (groupName) =>
            groupName === assignedTo[0] && groupName === assignedTo[1]
        ) || KCProcessingTeams.find((groupName) =>
        groupName === assignedTo[0] && groupName === assignedTo[1])
      ) {
        assigneeObject.assignedGroup = assignedTo[0];
        assigneeObject.assignedTo = "";
      } else if (assignedTo.length > 3) {
        assigneeObject.assignedGroup = assignedTo[0];
        assigneeObject.assignedTo = assignedTo[1];
        assigneeObject.assignedToFirstName = assignedTo[2];
        assigneeObject.assignedToLastName = assignedTo[3];
      } else {
        assigneeObject.assignedGroup = "Unassigned";
        assigneeObject.assignedTo = assignedTo[0];
      }
        //assigneeObject.assignedToName = value2;
        assigneeObject.assignedToName = value2 ? value2 : `${assigneeObject.assignedToFirstName}, ${assigneeObject.assignedToFirstName}`;
      return assigneeObject;
}

export const createRequestDetailsObjectFunc = (
  requestObject,
  requiredRequestDetailsValues,
  requestId,
  name,
  value,
  value2
) => {
  requestObject.id = requestId;
  if(requiredRequestDetailsValues.requestStartDate)
    requestObject.requestProcessStart =
    requiredRequestDetailsValues.requestStartDate;
  requestObject.dueDate = requiredRequestDetailsValues.dueDate;
  requestObject.receivedMode = requiredRequestDetailsValues.receivedMode;
  requestObject.deliveryMode = requiredRequestDetailsValues.deliveryMode;
  switch (name) {
    case FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES:
      requestObject.receivedDate = value.receivedDate?formatDate(value.receivedDate, "yyyy MMM, dd"): "";
      requestObject.receivedDateUF = value.receivedDate
        ? new Date(value.receivedDate)?.toISOString()
        : "";
      requestObject.requestProcessStart = value.requestStartDate;
      requestObject.dueDate = value.dueDate;
      requestObject.receivedMode = value.receivedMode;
      requestObject.deliveryMode = value.deliveryMode;
      break;
    case FOI_COMPONENT_CONSTANTS.ASSIGNED_TO:
      const assigneeDetails = createAssigneeDetails(value, value2);
      requestObject.assignedGroup = assigneeDetails.assignedGroup;
      requestObject.assignedTo = assigneeDetails.assignedTo;
      requestObject.assignedToFirstName = assigneeDetails.assignedToFirstName;
      requestObject.assignedToLastName = assigneeDetails.assignedToLastName;
      requestObject.assignedToName = assigneeDetails.assignedToName
      break;
    case FOI_COMPONENT_CONSTANTS.RECEIVED_DATE:
      if(!!value){
        requestObject.receivedDate = formatDate(value, "yyyy MMM, dd");
        const receivedDateUTC = new Date(value)?.toISOString();
        requestObject.receivedDateUF = receivedDateUTC;
      }
      break;
    case FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE:
      requestObject.requestProcessStart = value;
      requestObject.dueDate = value2;
      break;
    case FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST:
      requestObject.selectedMinistries = [];
      const filteredData = value
        .filter((programArea) => programArea.isChecked)
        .map((filteredProgramArea) => {
          return {
            code: filteredProgramArea.bcgovcode,
            name: filteredProgramArea.name,
            isSelected: filteredProgramArea.isChecked,
          };
        });
      requestObject.selectedMinistries = filteredData;
      break;
    case FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS:
      requestObject.linkedRequests = typeof value == 'string' ? JSON.parse(value) :value;
      break;
    case FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED:
      requestObject.identityVerified = value;
      break;
    case FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER:
    case FOI_COMPONENT_CONSTANTS.DOB:
    case FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME:
    case FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME:
    case FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME:
    case FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME:
    case FOI_COMPONENT_CONSTANTS.CHILD_DOB:
    case FOI_COMPONENT_CONSTANTS.ANOTHER_DOB:
    case FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME:
    case FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME:
    case FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME:
    case FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME:
      updateAdditionalInfo(name, value, requestObject);
      break;
    default:
      requestObject[name] = value;
      break;
  }
  return requestObject;
};

export const checkContactGiven = (requiredContactDetails) => {
  return (
    (requiredContactDetails.address === "" ||
      requiredContactDetails.city === "" ||
      requiredContactDetails.province === "" ||
      requiredContactDetails.country === "" ||
      requiredContactDetails.postal === "") &&
    requiredContactDetails.email === ""
  );
};

export const getBCgovCode = (ministryId, requestDetails) => {
  return ministryId && requestDetails?.selectedMinistries
    ? JSON.stringify(requestDetails.selectedMinistries[0]["code"])
    : "";
};

export const checkValidationError = (
  requiredApplicantDetails,
  contactDetailsNotGiven,
  requiredRequestDescriptionValues,
  validation,
  assignedToValue,
  requiredRequestDetailsValues,
  requiredAxisDetails,
  isAddRequest,
  currentrequestStatus
) => {

  return (
    requiredApplicantDetails.firstName === "" ||
    requiredApplicantDetails.lastName === "" ||
    requiredApplicantDetails.category.toLowerCase().includes("select") ||
    contactDetailsNotGiven ||
    requiredRequestDescriptionValues.description === "" ||
    (!requiredRequestDescriptionValues.isProgramAreaSelected 
      && ([StateEnum.unopened.name.toLowerCase(), StateEnum.intakeinprogress.name.toLowerCase()].includes(currentrequestStatus?.toLowerCase()) || isAddRequest)) ||
    (requiredRequestDetailsValues.requestType.toLowerCase() ===
      FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL &&
      !requiredRequestDescriptionValues.ispiiredacted) ||
    !!validation.helperTextValue ||
    assignedToValue.toLowerCase().includes("unassigned") ||
    requiredRequestDetailsValues.requestType.toLowerCase().includes("select") ||
    requiredRequestDetailsValues.receivedMode
      .toLowerCase()
      .includes("select") ||
    requiredRequestDetailsValues.deliveryMode
      .toLowerCase()
      .includes("select") ||
    !requiredRequestDetailsValues.receivedDate ||
    !requiredRequestDetailsValues.requestStartDate ||
    !requiredAxisDetails.axisRequestId
  );
};

/*******
 * alertUser(), handleOnHashChange() and useEffect() are used to handle the Navigate away from Comments tabs
 */
//Below function will handle beforeunload event
export const alertUser = (e) => {
  e.preventDefault();
  e.returnValue = "";
};

export const findRequestState = (requestStatusId) => {
  if (requestStatusId != undefined) {
    let stateArray = Object.entries(StateEnum).find(
      (value) => value[1].id === requestStatusId
    );
    return stateArray[1].name;
  }
};

export const shouldDisableFieldForMinistryRequests = (requestStatus) => {
  if (!requestStatus) {
    return false;
  }

  if (
    requestStatus !== StateEnum.unopened.name &&
    requestStatus !== StateEnum.intakeinprogress.name
  ) {
    return true;
  }
};

export const handleBeforeUnload = (e) => {
  alertUser(e);
};

export  const isAxisSyncDisplayField = (field) => {
  return Object.entries(AXIS_SYNC_DISPLAY_FIELDS).find(([key]) => key === field)?.[1];
};

export const isMandatoryField = (field) => {
  return  Object.values(MANDATORY_FOI_REQUEST_FIELDS).find((element) =>element === field);
};

export const closeApplicantDetails = (user, requestType) => {
  const userGroups = user?.groups?.map(group => group.slice(1));
  return !!(isProcessingTeam(userGroups) && requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL);
}

export const closeChildDetails = (user, requestType) => {
  const userGroups = user?.groups?.map(group => group.slice(1));
  return !!(isProcessingTeam(userGroups) && requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL);
}

export const closeContactInfo = (user,requestDetails) => {
  const userGroups = user?.groups?.map(group => group.slice(1));
  return !!(Object.entries(requestDetails)?.length !== 0 && (isProcessingTeam(userGroups) || isFlexTeam(userGroups)));
}

export const isValidMinistryCode = (selectedMinistry, ministriesList) => {
  return ministriesList.some(ministry => ministry.bcgovcode === selectedMinistry)
}

export const countOfMinistrySelected = (selectedMinistryList) => {
  return selectedMinistryList.reduce(function(n, ministry) {
    return n + (ministry.isChecked);
  }, 0);
}

export const persistRequestFieldsNotInAxis = (newRequestDetails, existingRequestDetails) => {
  newRequestDetails.assignedGroup = existingRequestDetails.assignedGroup;
  newRequestDetails.assignedTo= existingRequestDetails.assignedTo;
  newRequestDetails.assignedToFirstName= existingRequestDetails.assignedToFirstName;
  newRequestDetails.assignedToLastName= existingRequestDetails.assignedToLastName;
  newRequestDetails.assignedToName= existingRequestDetails.assignedToName;
  let foiReqAdditionalPersonalInfo = existingRequestDetails.additionalPersonalInfo;
  let axisAdditionalPersonalInfo = newRequestDetails.additionalPersonalInfo;
  if(newRequestDetails.requestType === 'personal'){
    for(let key of Object.keys(existingRequestDetails)){
      if((key == 'correctionalServiceNumber' || key == 'publicServiceEmployeeNumber' ) && !isAxisSyncDisplayField(key))
        newRequestDetails[key] = existingRequestDetails[key];
    }
    for(let key of Object.keys(foiReqAdditionalPersonalInfo)){
      if(!isAxisSyncDisplayField(key)){
        axisAdditionalPersonalInfo[key] = foiReqAdditionalPersonalInfo[key];
      }
    }
  }
  return newRequestDetails;
}

export const getUniqueIdentifier = (obj) => {
  return (obj.extensionstatusid+formatDate(obj.extendedduedate, "MMM dd yyyy")+obj.extensionreasonid).replace(/\s+/g, '');
}

