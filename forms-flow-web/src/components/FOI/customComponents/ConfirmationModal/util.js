import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { getFullnameList } from "../../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';

  export const getAssignedTo = (_saveRequestObject) => {

    if (_saveRequestObject?.assignedTo) {
      return getFullName(_saveRequestObject.assignedTo);
    }

    return _saveRequestObject?.assignedGroup
  }

  export const getFullName = (username) => {
    if(!username) {
      return null
    }

    const fullNameList = getFullnameList()
      .filter(assignee => assignee.username === username)

    if(fullNameList.length > 0) {
      return fullNameList[0].fullname
    }

    return username;
  };

  export const getMinistryGroup = (_saveRequestObject) => {
    if (_saveRequestObject.selectedMinistries?.length > 0 )
      return `${_saveRequestObject.selectedMinistries[0].name} Queue`;
  }
  export const getSelectedMinistry = (_saveRequestObject, _ministryGroup) => {
    if (_saveRequestObject?.assignedministrygroup)
      return `${_saveRequestObject.assignedministrygroup} Queue`;
    return _ministryGroup;
  }
  export const getSelectedMinistryAssignedTo = (_saveRequestObject, _selectedMinistry) => {
    if (_saveRequestObject?.assignedministryperson)
      return _saveRequestObject.assignedministryperson;
    return _selectedMinistry;
  }

  export const getMessage = (_saveRequestObject, _state, _requestNumber, _currentState, _requestId, _cfrStatus,allowStateChange,isAnyAmountPaid, estimatedTotalFeesDue) => {
    if ((_currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase() && _state.toLowerCase() !== StateEnum.closed.name.toLowerCase())) {
      _saveRequestObject.reopen = true;
      return {title: "Re-Open Request", body: <>Are you sure you want to re-open Request # {_requestNumber ? _requestNumber : `U-00${_requestId}`}? <br/> The request will be re-opened to the previous state: {_state} </>};
    }
    if ((_currentState?.toLowerCase() === StateEnum.onholdother.name.toLowerCase())){
      return {title: "Taking Request off hold", body: "Are you sure you want to take this request off hold? The legislated due date will be recalculated"};
    }
    switch(_state.toLowerCase()) {
      case StateEnum.intakeinprogress.name.toLowerCase():
          return {title: "Changing the state", body: "Are you sure you want to change the state to Intake in Progress?"};
      case StateEnum.peerreview.name.toLowerCase():
          return {title: "Changing the state", body: "Are you sure you want to change the state to Peer Review?"};
      case StateEnum.tagging.name.toLowerCase():
            return {title: "Changing the state", body: "Are you sure you want to change the state to Tagging?"};
      case StateEnum.readytoscan.name.toLowerCase():
            return {title: "Changing the state", body: "Are you sure you want to change the state to Ready to Scan?"};           
      case StateEnum.open.name.toLowerCase():
          return {title: "Changing the state", body: "Are you sure you want to Open this request?"};
      case StateEnum.closed.name.toLowerCase():
        return {title: "Close Request", body: ""};
      case StateEnum.redirect.name.toLowerCase():
          return {title: "Redirect Request", body: "Are you sure you want to Redirect this request?"};
      case StateEnum.section5pending.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.section5pending.name}?`};
      case StateEnum.callforrecords.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.callforrecords.name}?`};
      case StateEnum.recordsreadyforreview.name.toLowerCase():
        if(!allowStateChange && _saveRequestObject.requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL && isAnyAmountPaid)
          return {title: "Changing the state", body: `Unable to change state until fee estimate actuals have been completed.`};
        else
        return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.recordsreadyforreview.name}?`};
      case StateEnum.review.name.toLowerCase():
        if(!allowStateChange)
          return {title: "Changing the state", body: `Unable to change state until fee estimate actuals have been completed.`};
        else if (!isAnyAmountPaid &&  _saveRequestObject.requeststatuslabel === StateEnum.callforrecords.label)
          return {title: "Review Request", body: `Upload completed Call for Records form (if required) to change the state.`};
        else if (_saveRequestObject.requeststatuslabel === StateEnum.harms.label)
          return {title: "Review Request", body: `Upload completed Call for Records form (if required) to change the state.`};
        else
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.review.name}?`};
      case StateEnum.consult.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.consult.name}?`};
      case StateEnum.signoff.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.signoff.name}?`};
      case StateEnum.feeassessed.name.toLowerCase():
          if (_cfrStatus === 'init') {
            return {
              title: "Fee Estimate",
              body: "To update the state you must first complete the estimated hours in the CFR Form so that Total Fees are due."
            };
          } else if (estimatedTotalFeesDue <= 0) {
            return {
              title: "Fee Estimate",
              body: "To update state to Fee Estimate, Estimated Total must be greater than $0."
            }
          }
          else {
            return {title: "Fee Estimate", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.feeassessed.name}? The CFR Form will be locked for editing and sent to IAO for review.`};
          }
      case StateEnum.deduplication.name.toLowerCase():
        if(!allowStateChange)
          return {title: "Changing the state", body: `Unable to change state until fee estimate actuals have been completed.`};
        else
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.deduplication.name}?`};
      case StateEnum.harms.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.harms.name}?`};
      case StateEnum.onhold.name.toLowerCase():
          if (_cfrStatus !== 'approved' && _currentState?.toLowerCase() !== StateEnum.response.name.toLowerCase()) {
            return {
              title: "On Hold",
              body: "You must review and approve the CFR Form before you can put this request On Hold."
            };
          } else if(!_saveRequestObject.email) {
            return {
              title: "On Hold",
              body: "There is no applicant email on file. Please check the box to confirm that you have mailed the applicant a letter before you put this request On Hold."
            };
          } else {
              if (_currentState?.toLowerCase() === StateEnum.response.name.toLowerCase()) {
                return {
                  title: "On Hold",
                  body: <>Upload the completed Fee Estimate letter to change the state of this request to On Hold. When you change Request #{_requestNumber} to On Hold
                  <b> the clock will be stopped and the applicant will automatically be emailed the fee estimate letter.</b> </>};
                }
              return {
                title: "On Hold",
                body: <>Are you sure you want to change Request #{_requestNumber} to on hold? <br/> <b>This will stop the clock and automatically email the applicant the fee estimate.</b> </>};
            }
      case StateEnum.response.name.toLowerCase():
        if (_saveRequestObject.requeststatuslabel === StateEnum.signoff.label)
          return {title: "Ministry Sign Off", body: `Upload eApproval Logs, and enter in required approval fields to verify Ministry Approval and then change the state.`};
        else
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.response.name}?`};
          case StateEnum.appfeeowing.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.appfeeowing.name}?`};
      case StateEnum.onholdother.name.toLowerCase():
          return {title: "Change Request to On Hold - Other", 
                 body: <>Are you sure you want to change Request #{_requestNumber} to {StateEnum.onholdother.name}? This should be used for scenarios 
                 that are not fee related (such as Third Party notice).<b> This will stop the clock.</b></>};
      default:
          return {title: "", body: ""};
    }
  }


  export const getProcessingTeams = (_processingTeamList, _selectedMinistries) => {
    const updatedList = _processingTeamList.filter(listItem => _selectedMinistries.includes(listItem.bcgovcode))?.map(item => item.team);
    return updatedList?.filter((v, i, a) => a.indexOf(v) === i);
  }

  export const getUpdatedAssignedTo = (_assignedTo, _processingTeamList, _state, _requestType, isiaorestricted) => {
    if (_requestType?.toLowerCase() === 'personal' && _state?.toLowerCase() === StateEnum.open.name.toLowerCase()
    && !isiaorestricted)
      return _processingTeamList.join(", ");
    else if (_requestType?.toLowerCase() === 'general' && _state?.toLowerCase() === StateEnum.open.name.toLowerCase()
    && !isiaorestricted)
      return "Flex Team";
    else
      return _assignedTo;
  }