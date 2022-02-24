import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { calculateDaysRemaining } from "../../../../helper/FOI/helper";

export const getMinistryBottomTextMap = (
  requestDetails,
  requestStatus,
  _cfrDaysRemaining
) => {
  const _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);

  const _daysRemainingText =
    _daysRemaining > 0
      ? `${_daysRemaining} Days Remaining`
      : `${Math.abs(_daysRemaining)} Days Overdue`;

  const _cfrDaysRemainingText =
    _cfrDaysRemaining > 0
      ? `CFR Due in ${_cfrDaysRemaining} Days`
      : `Records late by ${Math.abs(_cfrDaysRemaining)} Days`;

  const hideCFRDaysRemaining = [
    StateEnum.review.name.toLowerCase(),
    StateEnum.consult.name.toLowerCase(),
    StateEnum.signoff.name.toLowerCase(),
    StateEnum.response.name.toLowerCase(),
  ];

  const bottomTextMap = new Map();

  if (!hideCFRDaysRemaining.includes(requestStatus?.toLowerCase())) {
    bottomTextMap.set("cfrDaysRemainingText", _cfrDaysRemainingText);
  }
  bottomTextMap.set("daysRemainingText", _daysRemainingText);

  return bottomTextMap;
};
