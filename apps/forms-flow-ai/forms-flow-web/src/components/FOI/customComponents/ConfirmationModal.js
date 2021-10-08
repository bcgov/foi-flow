import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import './confirmationmodal.scss';
import { StateEnum } from '../../../constants/FOI/statusEnum';

export default function ConfirmationModal({ openModal, handleModal, state, saveRequestObject }) {    
    
    const handleClose = () => {
      //handleModal(false);
      window.location.reload()
    };

    const handleSave = () => {
      handleModal(true);
    }   
    const getMessage = (_state, _requestNumber) => {
      switch(_state.toLowerCase()) {     
        case StateEnum.intakeinprogress.name.toLowerCase():
            return "Are you sure you want Save the request?";
        case StateEnum.open.name.toLowerCase():
            return "Are you sure you want to Open this request?";
        case StateEnum.closed.name.toLowerCase():
            return "Are you sure you want to Close this request?"; 
        case StateEnum.redirect.name.toLowerCase():
            return "Are you sure you want to Redirect this request?";  
        case StateEnum.callforrecords.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.callforrecords.name}?`;
        case StateEnum.review.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.review.name}?`;
        case StateEnum.consult.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.consult.name}?`;
        case StateEnum.signoff.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to${StateEnum.signoff.name}?`;
        case StateEnum.feeassessed.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.feeassessed.name}?`;
        case StateEnum.callforrecordsoverdue.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.callforrecordsoverdue.name}?`;
        default:
            return [];
    }
  }
  const assignedTo= saveRequestObject.assignedTo ? saveRequestObject.assignedTo : saveRequestObject.assignedGroup;
  const selectedMinistry= saveRequestObject.selectedMinistries ? saveRequestObject.selectedMinistries[0] : "";
  const requestNumber = saveRequestObject.idNumber ? saveRequestObject.idNumber : "";
  let message = getMessage(state, requestNumber);  
    return (
      <div className="state-change-dialog">        
        <Dialog
          open={openModal}
          onClose={handleClose}
          aria-labelledby="state-change-dialog-title"
          aria-describedby="state-change-dialog-description"
          maxWidth={'md'}
          fullWidth={true}
          // id="state-change-dialog"
        >
          <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Changing the state            </h2>
              <IconButton onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-description" component={'span'}>
              {message}
              <table className="table table-bordered table-assignedto" cellSpacing="0" cellPadding="0">
                <tbody>
                  <tr>
                    <th scope="row">IAO Assigned To</th>
                    <td>{assignedTo}</td>
                  </tr>
                </tbody>
              </table>
              {state.toLowerCase() === StateEnum.callforrecords.name.toLowerCase() || state.toLowerCase() === StateEnum.review.name.toLowerCase() || state.toLowerCase() === StateEnum.consult.name.toLowerCase() || state.toLowerCase() === StateEnum.signoff.name.toLowerCase() ? 
              <table className="table table-bordered table-assignedto">
                <tbody>
                  <tr>
                    <th scope="row">Ministry Assigned To</th>
                    <td>{`${selectedMinistry.name} Queue`}</td>
                  </tr>
                </tbody>
              </table>
              : null }
            </DialogContentText>
          </DialogContent>
          <DialogActions>            
            <button className="btn-bottom btn-save" onClick={handleSave}>
              Save Change
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }