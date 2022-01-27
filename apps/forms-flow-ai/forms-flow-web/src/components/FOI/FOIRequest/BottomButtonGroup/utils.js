import {
  addBusinessDays
} from "../../../../helper/FOI/helper";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

export const dueDateCalculation = (dateText, noOfBusinessDays) => {
  if (!dateText) {
    return "";
  }

  return addBusinessDays(dateText, noOfBusinessDays);
};

export const getRequestState = ({
  currentSelectedStatus,
  requestState,
  urlIndexCreateRequest,
  saveRequestObject,
}) => {
  if (currentSelectedStatus) {
    return currentSelectedStatus;
  }

  if (
    requestState === StateEnum.unopened.name &&
    saveRequestObject.sourceOfSubmission === "onlineform"
  ) {
    return StateEnum.intakeinprogress.name;
  }

  if (urlIndexCreateRequest > -1) {
    return StateEnum.intakeinprogress.name;
  }
  return requestState;
};

export const fillAssignmentFields = (request) => {
  if (request.requestType === "general") {
    request.assignedTo = "";
    request.assignedGroup = "Flex Team";
  } else if (request.requestType === "personal") {
    request.assignedTo = "";
    request.assignedGroup = "Processing Team";
  }
};

export const alertUser = (e) => {  
    e.preventDefault();
    e.returnValue = "";
};

export const returnToQueue = (e, _unSavedRequest) => { 
  if (
    !_unSavedRequest ||
    (_unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))
  ) {
    e.preventDefault();
    window.removeEventListener("beforeunload", (event) =>
      alertUser(event)
    );
    window.location.href = "/foi/dashboard";
  }
};