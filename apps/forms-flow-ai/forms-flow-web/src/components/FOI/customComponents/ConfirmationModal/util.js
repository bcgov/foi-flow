import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { getFullnameList } from "../../../../helper/FOI/helper"
  
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

  export const getMessage = (_saveRequestObject, _state, _requestNumber, _currentState, _requestId) => {
    if ((_currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase() && _state.toLowerCase() !== StateEnum.closed.name.toLowerCase())) {
      _saveRequestObject.reopen = true;
      return {title: "Re-Open Request", body: <>Are you sure you want to re-open Request # {_requestNumber ? _requestNumber : `U-00${_requestId}`}? <br/> <span className="confirm-message-2"> The request will be re-opened to the previous state: {_state}</span> </>}; 
    }
    switch(_state.toLowerCase()) {
      case StateEnum.intakeinprogress.name.toLowerCase():
          return {title: "Changing the state", body: "Are you sure you want to change the state to Intake in Progress?"};
      case StateEnum.open.name.toLowerCase():
          return {title: "Changing the state", body: "Are you sure you want to Open this request?"};
      case StateEnum.closed.name.toLowerCase():
        return {title: "Close Request", body: ""}; 
      case StateEnum.redirect.name.toLowerCase():
          return {title: "Redirect Request", body: "Are you sure you want to Redirect this request?"};  
      case StateEnum.callforrecords.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.callforrecords.name}?`};
      case StateEnum.review.name.toLowerCase():
        if (_saveRequestObject.requeststatusid === StateEnum.callforrecords.id)
          return {title: "Review Request", body: `Upload completed Call for Records form to change the state.`};
        else if (_saveRequestObject.requeststatusid === StateEnum.harms.id)
          return {title: "Review Request", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.review.name}?`};
        else
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.review.name}?`};
      case StateEnum.consult.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.consult.name}?`};
      case StateEnum.signoff.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.signoff.name}?`};
      case StateEnum.feeassessed.name.toLowerCase():
          return {title: "Fee Estimate", body: `Upload Fee Estimate in order to change the state.`};
      case StateEnum.deduplication.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.deduplication.name}?`};
      case StateEnum.harms.name.toLowerCase():
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.harms.name}?`};       
      case StateEnum.onhold.name.toLowerCase():
          return {title: "Hold Request", body: <>Are you sure you want to change Request #{_requestNumber} to on hold? <br/> <span className="confirm-message-2">This will <b>stop</b> the clock.</span> </>};
      case StateEnum.response.name.toLowerCase():
        if (_saveRequestObject.requeststatusid === StateEnum.signoff.id)
          return {title: "Ministry Sign Off", body: `Upload eApproval Logs to verify Ministry Approval and change the state.`};
        else
          return {title: "Changing the state", body: `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.response.name}?`};
      default:
          return {title: "", body: ""};
    }
  }


  export const getProcessingTeams = (_processingTeamList, _selectedMinistries) => {
    const updatedList = _processingTeamList.filter(listItem => _selectedMinistries.includes(listItem.bcgovcode))?.map(item => item.team);
    return updatedList?.filter((v, i, a) => a.indexOf(v) === i);
  }

  export const getUpdatedAssignedTo = (_assignedTo, _processingTeamList, _state, _requestType) => {
    if (_requestType?.toLowerCase() === 'personal' && _state?.toLowerCase() === StateEnum.open.name.toLowerCase()) 
      return _processingTeamList.join(", ");    
    else if (_requestType?.toLowerCase() === 'general' && _state?.toLowerCase() === StateEnum.open.name.toLowerCase())
      return "Flex Team";
    else
      return _assignedTo;
  }