import {
  addBusinessDays
} from "../../../../helper/FOI/helper";
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { handleBeforeUnload } from "../utils";

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
    request.assignedTo = null;
    request.assignedToFirstName = null;
    request.assignedToLastName = null;
    request.assignedGroup = "Flex Team";
  }
};

export const returnToQueue = (e, _unSavedRequest) => {
  if (_unSavedRequest) {
    e.preventDefault();
    if (
      window.confirm(
        "Are you sure you want to leave? Your changes will be lost."
      )
    ) {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      window.location.href = "/foi/dashboard";
    } else {
      window.history.pushState(null, null, window.location.pathname);
    }
  } else {
    window.location.href = "/foi/dashboard";
  }
};