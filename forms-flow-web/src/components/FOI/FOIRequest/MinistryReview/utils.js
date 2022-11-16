import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { calculateDaysRemaining } from "../../../../helper/FOI/helper";
import { getExtensionsCountText } from "../utils";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";

export const getMinistryBottomTextMap = (
  requestDetails,
  requestState,
  _cfrDaysRemaining,
  requestExtensions
) => {
  const _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);

  const _daysRemainingText =
    _daysRemaining > 0
      ? `${_daysRemaining} Days Remaining`
      : `${Math.abs(_daysRemaining)} Days Overdue`;

  const _cfrDaysRemainingText = `CFR Due in ${_cfrDaysRemaining} Days`;
      

  const hideCFRDaysRemaining = [
    StateEnum.review.name.toLowerCase(),
    StateEnum.consult.name.toLowerCase(),
    StateEnum.signoff.name.toLowerCase(),
    StateEnum.response.name.toLowerCase(),
  ];

  const bottomTexts = [];

  if (!hideCFRDaysRemaining.includes(requestState?.toLowerCase())) {
    bottomTexts.push(_cfrDaysRemainingText);
  }
  bottomTexts.push(_daysRemainingText);
  bottomTexts.push(getExtensionsCountText(requestExtensions));

  return bottomTexts;
};

export const getHeaderText = (requestDetails) => {
  if(requestDetails.axisRequestId)
    return requestDetails.axisRequestId;

  if (requestDetails.idNumber)
    return `Request #${requestDetails.idNumber}`;   
  return FOI_COMPONENT_CONSTANTS.REVIEW_REQUEST;
};

export const alertUser = (e) => {
  e.returnValue = "";
  e.preventDefault();
};


export const createAssignedToDetailsObject = (
    value
) => {
  const assigneeObject = {
    assignedministrygroup: "",
    assignedministryperson: "",
    assignedministrypersonFirstName: "",
    assignedministrypersonLastName: ""
  }
  const assignedToValue = value?.split("|");
      if (
        assignedToValue.length > 1 &&
        assignedToValue[0] &&
        assignedToValue[1] &&
        assignedToValue[2] &&
        assignedToValue[3]
      ) {
        assigneeObject.assignedministrygroup = assignedToValue[0];
        assigneeObject.assignedministryperson = assignedToValue[1];
        assigneeObject.assignedministrypersonFirstName = assignedToValue[2];
        assigneeObject.assignedministrypersonLastName = assignedToValue[3];
      }
  return assigneeObject;
  
};