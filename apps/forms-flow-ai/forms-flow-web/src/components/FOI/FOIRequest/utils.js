import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { formatDate } from "../../../helper/FOI/helper";

export const getTabBottomText = ({ _daysRemainingText, _cfrDaysRemainingText, _status }) => {
  const generalStates = [
    StateEnum.open.name,
    StateEnum.review.name,
    StateEnum.redirect.name,
    StateEnum.consult.name,
    StateEnum.signoff.name,
    StateEnum.response.name,
    StateEnum.closed.name
  ];

  if( generalStates.includes(_status) ) {
    return _daysRemainingText;
  }

  const cfrStates = [
    StateEnum.callforrecords.name,
    StateEnum.feeassessed.name,
    StateEnum.deduplication.name,
    StateEnum.harms.name
  ];

  if ( cfrStates.includes(_status) ) {
    return `${_cfrDaysRemainingText}|${_daysRemainingText}`;
  }

  return _status;
};

export const confirmChangesLost = (positiveCallback, negativeCallback) => {
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

export const getRedirectAfterSaveUrl = (_state, ministryId, requestId) => {
  if(ministryId) {
    return `/foi/foirequests/${requestId}/ministryrequest/${ministryId}/${_state}`;
  }

  if(requestId) {
    return `/foi/reviewrequest/${requestId}/${_state}`;
  }

  return null;
};

export const getTabBG = (_tabStatus) => {
  switch (_tabStatus){
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
  var _obj = {...jsonObj};
  if(_obj[name] !== undefined) {
    _obj[name] = value;
  }
  return _obj;
};

export const updateAdditionalInfo = (name, value, requestObject) => {
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

  if(requestObject.additionalPersonalInfo[name] !== undefined) {
    requestObject.additionalPersonalInfo[name] = value;
  }
  return requestObject;
};

export const createRequestDetailsObjectFunc = (requestObject, requiredRequestDetailsValues, requestId, name, value, value2) => {
  requestObject.id = requestId;
  requestObject.requestProcessStart = requiredRequestDetailsValues.requestStartDate;
  requestObject.dueDate = requiredRequestDetailsValues.dueDate;
  requestObject.receivedMode = requiredRequestDetailsValues.receivedMode;
  requestObject.deliveryMode = requiredRequestDetailsValues.deliveryMode;

  switch(name) {
    case FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES:
      requestObject.receivedDate = value.receivedDate;     
      requestObject.receivedDateUF = value.receivedDate? new Date(value.receivedDate).toISOString(): "";
      requestObject.requestProcessStart = value.requestStartDate;
      requestObject.dueDate = value.dueDate;
      requestObject.receivedMode = value.receivedMode;
      requestObject.deliveryMode = value.deliveryMode;
      break;
    case FOI_COMPONENT_CONSTANTS.ASSIGNED_TO:
      const assignedTo = value.split("|");
      if (FOI_COMPONENT_CONSTANTS.ASSIGNEE_GROUPS.find(groupName => (groupName === assignedTo[0] && groupName === assignedTo[1]))) {
        requestObject.assignedGroup = assignedTo[0];
        requestObject.assignedTo = "";
      }
      else if (assignedTo.length > 1) {
        requestObject.assignedGroup = assignedTo[0];
        requestObject.assignedTo = assignedTo[1];
      }
      else {
        requestObject.assignedGroup = "Unassigned";
        requestObject.assignedTo = assignedTo[0];
      }   
      requestObject.assignedToName = value2;
      break;
    case FOI_COMPONENT_CONSTANTS.RECEIVED_DATE:
      requestObject.receivedDate = formatDate(value, 'yyyy MMM, dd');
      const receivedDateUTC = new Date(value).toISOString();
      requestObject.receivedDateUF = receivedDateUTC;
      break;
    case FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE:
      requestObject.requestProcessStart = value;
      requestObject.dueDate = value2;
      break;
    case FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST:
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
      break;
    default:
      requestObject[name] = value;
      break;
  }
  return requestObject;
};