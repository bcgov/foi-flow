import React, { useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import './confirmationmodal.scss';
import { StateEnum } from '../../../constants/FOI/statusEnum';
import FileUpload from './FileUpload';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { formatDate } from "../../../helper/FOI/helper";
import { useSelector } from "react-redux";

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    marginTop:'30px',
    marginBottom:'50px'
  },
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
  btndisabled: {
    border: 'none',
    backgroundColor: '#eceaea',
    color: '#FFFFFF'
  },
  btnenabled: {
    border: 'none',
    backgroundColor: '#38598A',
    color: '#FFFFFF'
  },

}));

export default function ConfirmationModal({ openModal, handleModal, state, saveRequestObject }) {    
    const classes = useStyles();
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
            return `Upload completed Call for Records form to change the state.`;
        case StateEnum.consult.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.consult.name}?`;
        case StateEnum.signoff.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to${StateEnum.signoff.name}?`;
        case StateEnum.feeassessed.name.toLowerCase():
            return `Are you sure you want to change Request #${_requestNumber} to ${StateEnum.feeassessed.name}?`;
        default:
            return [];
      }
    }

    const assignedTo= saveRequestObject.assignedTo ? saveRequestObject.assignedTo : saveRequestObject.assignedGroup;
    const selectedMinistry = saveRequestObject.assignedministrygroup ? saveRequestObject.assignedministrygroup + " Queue" : saveRequestObject.selectedMinistries ? saveRequestObject.selectedMinistries[0].name + " Queue" : "";
    const selectedMinistryAssignedTo = saveRequestObject.assignedministryperson ? saveRequestObject.assignedministryperson : selectedMinistry;
    const requestNumber = saveRequestObject.idNumber ? saveRequestObject.idNumber : "";
    let message = getMessage(state, requestNumber);
    const multipleFiles = false;
    const [file, setFile] = useState({});
    const updateFilesCb = (file) => {
      setFile(file);
    }

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
              <h2 className="state-change-header">{`${state.toLowerCase() === StateEnum.review.name.toLowerCase() ? 'Review Recrods' : 'Changing the state'}`}</h2>
              <IconButton onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-description" component={'span'}>              
            {state.toLowerCase() === StateEnum.closed.name.toLowerCase() ? 
                <CloseForm saveRequestObject={saveRequestObject} handleClosingDateChange={handleClosingDateChange} handleClosingReasonChange={handleClosingReasonChange} /> :
              <>
              {state.toLowerCase() === StateEnum.closed.name.toLowerCase() ? 
                <CloseForm saveRequestObject={saveRequestObject} handleClosingDateChange={handleClosingDateChange} handleClosingReasonChange={handleClosingReasonChange} />
              :
                <>
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
                      <td>{selectedMinistryAssignedTo}</td>
                    </tr>
                  </tbody>
                </table>
                : null}
                </>
              }
              </>             
              } 
             
              
            </DialogContentText>
          </DialogContent>
          <DialogActions>            
            <button className={`btn-bottom btn-save ${Object.entries(file).length === 0 && (state.toLowerCase() === StateEnum.review.name.toLowerCase() || state.toLowerCase() === StateEnum.feeassessed.name.toLowerCase()) ? classes.btndisabled : classes.btnenabled }`} disabled={Object.entries(file).length === 0 && (state.toLowerCase() === StateEnum.review.name.toLowerCase() || state.toLowerCase() === StateEnum.feeassessed.name.toLowerCase())} onClick={handleSave}>
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


const CloseForm = React.memo(({saveRequestObject, handleClosingDateChange, handleClosingReasonChange}) => {

  const _requestDetails = saveRequestObject;
  const _closingReasons = useSelector(state=> state.foiRequests.closingReasons);

  const today = new Date();
  const [closingDateText, setClosingDate] = React.useState( formatDate(today) );
  const [selectedReason, setClosingReason] = React.useState( 0 );

  //############### replace this with the last status change date
  const lastStatusChangeDate = _requestDetails.requestProcessStart;

  const _handleClosingDateChange = (e) => {
    let pickedDate = e.target.value;
    if(new Date(pickedDate) > today)
      pickedDate = formatDate(today);

    setClosingDate(pickedDate);
    handleClosingDateChange(pickedDate);
  }

  const _handleReasonChange = (e) => {
    setClosingReason(e.target.value);
    handleClosingReasonChange(e.target.value);
  }
  
  const closingReasons = _closingReasons.map((reason)=>{
    return ( <MenuItem key={reason.closereasonid} value={reason.closereasonid} >{reason.name}</MenuItem> )
  });

  return (
    <>
    <div className="row foi-details-row confirm-modal-row first-row">
      <div className="col-lg-6 foi-details-col">
        <div className="confirm-label-area"><b>Application: </b><span className="confirm-label-content">{_requestDetails.firstName+" "+_requestDetails.lastName}</span></div>
      </div>
      <div className="col-lg-6 foi-details-col confirm-label-area">
        <div className="confirm-label-area"><b>Organization: </b><span className="confirm-label-content">{_requestDetails.businessName}</span></div>
      </div>
    </div>
    <div className="row foi-details-row confirm-modal-row">
      <div className="col-lg-6 foi-details-col">
        <div className="confirm-label-area"><b>Fee Waiver: </b><span className="confirm-label-content">{"N/A"}</span></div>
      </div>
      <div className="col-lg-6 foi-details-col confirm-label-area">
        <div className="confirm-label-area"><b>Fee Remaining: </b><span className="confirm-label-content">{"N/A"}</span></div>
      </div>
    </div>
    <div className="row foi-details-row confirm-modal-row">
      <div className="col-lg-6 foi-details-col">
        <TextField                
            label="Start Date"
            type="date" 
            value={_requestDetails.requestProcessStart}                            
            InputLabelProps={{
              shrink: true,
            }}
            variant="outlined" 
            required
            disabled
            fullWidth
        />
      </div>
      <div className="col-lg-6 foi-details-col">
        <TextField                
            label="Closing Date"
            type="date" 
            value={closingDateText || ''} 
            onChange={_handleClosingDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            InputProps={{inputProps: { min: lastStatusChangeDate, max: formatDate(today)} }}
            variant="outlined" 
            required
            error={closingDateText === undefined || closingDateText === ""}
            fullWidth
        />
      </div>
    </div>
    <div className="row foi-details-row confirm-modal-row">
      <div className="col-lg-12 foi-details-col">
        <TextField
            id="requestType"
            label="Reason for Closing Request"
            InputLabelProps={{ shrink: true, }}          
            select
            value={selectedReason}
            onChange={_handleReasonChange}
            input={<Input />} 
            variant="outlined"
            fullWidth
            required
            error={selectedReason==0}
        >            
          {closingReasons}
        </TextField>
      </div>
    </div>
    </>
  );
})