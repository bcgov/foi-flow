import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { formatDate } from "../../../helper/FOI/helper";
import { extensionStatusId, KCProcessingTeams } from "../../../constants/FOI/enum";

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
  return _daysRemaining > 0
    ? `${_daysRemaining} Days Remaining`
    : `${Math.abs(_daysRemaining)} Days Overdue`;
};

const getcfrDaysRemainingText = (_cfrDaysRemaining) => {
  return _cfrDaysRemaining > 0
    ? `CFR Due in ${_cfrDaysRemaining} Days`
    : `Records late by ${Math.abs(_cfrDaysRemaining)} Days`;
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
    case StateEnum.callforrecordsoverdue.name:
      return "foitabheadercollection foitabheaderCFROverdueBG";
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
    default:
      return "foitabheadercollection foitabheaderdefaultBG";
  }
};

export const assignValue = (jsonObj, value, name) => {
  var _obj = { ...jsonObj };
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
      identityVerified: "",
    };
  }
  requestObject.additionalPersonalInfo[name] = value;
  return requestObject;
};

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
      requestObject.receivedDate = value.receivedDate;
      requestObject.receivedDateUF = value.receivedDate
        ? new Date(value.receivedDate).toISOString()
        : "";
      requestObject.requestProcessStart = value.requestStartDate;
      requestObject.dueDate = value.dueDate;
      requestObject.receivedMode = value.receivedMode;
      requestObject.deliveryMode = value.deliveryMode;
      break;
    case FOI_COMPONENT_CONSTANTS.ASSIGNED_TO:
      const assignedTo = value.split("|");
      if (
        FOI_COMPONENT_CONSTANTS.ASSIGNEE_GROUPS.find(
          (groupName) =>
            groupName === assignedTo[0] && groupName === assignedTo[1]
        ) || KCProcessingTeams.find((groupName) =>
        groupName === assignedTo[0] && groupName === assignedTo[1])
      ) {
        requestObject.assignedGroup = assignedTo[0];
        requestObject.assignedTo = "";
      } else if (assignedTo.length > 3) {
        requestObject.assignedGroup = assignedTo[0];
        requestObject.assignedTo = assignedTo[1];
        requestObject.assignedToFirstName = assignedTo[2];
        requestObject.assignedToLastName = assignedTo[3];
      } else {
        requestObject.assignedGroup = "Unassigned";
        requestObject.assignedTo = assignedTo[0];
      }
      requestObject.assignedToName = value2;
      break;
    case FOI_COMPONENT_CONSTANTS.RECEIVED_DATE:
      requestObject.receivedDate = formatDate(value, "yyyy MMM, dd");
      const receivedDateUTC = new Date(value).toISOString();
      requestObject.receivedDateUF = receivedDateUTC;
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
    case FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER:
    case FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED:
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
    (requiredContactDetails.primaryAddress === "" ||
      requiredContactDetails.city === "" ||
      requiredContactDetails.province === "" ||
      requiredContactDetails.country === "" ||
      requiredContactDetails.postalCode === "") &&
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
  isAddRequest
) => {
  return (
    requiredApplicantDetails.firstName === "" ||
    requiredApplicantDetails.lastName === "" ||
    requiredApplicantDetails.category.toLowerCase().includes("select") ||
    contactDetailsNotGiven ||
    requiredRequestDescriptionValues.description === "" ||
    !requiredRequestDescriptionValues.isProgramAreaSelected ||
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
    (isAddRequest && !requiredAxisDetails.axisRequestId)
  );
};

export const alertUser = (e) => {
  e.preventDefault();
  e.returnValue = "";
};

export const findRequestState = (requestStatusId) => {
  if (requestStatusId != undefined) {
    var stateArray = Object.entries(StateEnum).find(
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