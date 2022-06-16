import React, { useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { useSelector } from "react-redux";

import './confirmationmodal.scss';
import { StateEnum, StateTransitionCategories } from '../../../../constants/FOI/statusEnum';
import FileUpload from '../FileUpload'
import { formatDate, calculateDaysRemaining } from "../../../../helper/FOI/helper";
import { MimeTypeList, MaxFileSizeInMB } from "../../../../constants/FOI/enum";
import { getMessage, getAssignedTo, getMinistryGroup, getSelectedMinistry, getSelectedMinistryAssignedTo, getProcessingTeams, getUpdatedAssignedTo } from './util';

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

export default function ConfirmationModal({requestId, openModal, handleModal, state, saveRequestObject,
  handleClosingDateChange, handleClosingReasonChange, attachmentsArray }) {
    const classes = useStyles();
    const processingTeamList = useSelector(reduxstate=> reduxstate.foiRequests.foiProcessingTeamList);
    const selectedMinistries = saveRequestObject?.selectedMinistries?.map(ministry => ministry.code);
    const updatedProcessingTeamList = getProcessingTeams(processingTeamList, selectedMinistries);
    const assignedTo= getAssignedTo(saveRequestObject);
    const updatedAssignedTo = getUpdatedAssignedTo(assignedTo, updatedProcessingTeamList, state, saveRequestObject?.requestType)
    const ministryGroup = getMinistryGroup(saveRequestObject);
    const selectedMinistry = getSelectedMinistry(saveRequestObject, ministryGroup);
    const selectedMinistryAssignedTo = getSelectedMinistryAssignedTo(saveRequestObject, selectedMinistry);
    const requestNumber = saveRequestObject?.idNumber;
    const axisRequestId = saveRequestObject?.axisRequestId;
    const currentState = saveRequestObject?.currentState;
    const daysRemainingLDD = calculateDaysRemaining(saveRequestObject?.dueDate);
    const multipleFiles = false;
    const reOpenRequest = currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase();
    const [files, setFiles] = useState([]);
    const updateFilesCb = (_files) => {
      setFiles(_files);
    }
    const [disableSaveBtn, setDisableSaveBtn] = React.useState( true );

    const cfrStatus = useSelector((reduxState) => reduxState.foiRequests.foiRequestCFRForm.status);

    React.useEffect(() => {
      setDisableSaveBtn(state.toLowerCase() === StateEnum.closed.name.toLowerCase());
    },[state]);

    const enableSaveBtn = () => {
      setDisableSaveBtn(false);
    }

    const isBtnDisabled = () => {
      if (state.toLowerCase() === StateEnum.feeassessed.name.toLowerCase() && cfrStatus === 'init') {
        return true;
      }
      return files.length === 0 && ((state.toLowerCase() === StateEnum.review.name.toLowerCase() && saveRequestObject.requeststatusid === StateEnum.callforrecords.id) ||
      (state.toLowerCase() === StateEnum.response.name.toLowerCase() && saveRequestObject.requeststatusid === StateEnum.signoff.id ) ||
      (state.toLowerCase() === StateEnum.review.name.toLowerCase() && saveRequestObject.requeststatusid === StateEnum.harms.id ))
    }

    const handleClose = () => {
      handleModal(false);
    };

    const handleSave = () => {
      let fileInfoList = [];
      if (files.length > 0) {
        let fileStatusTransition = "";
        if (state.toLowerCase() === StateEnum.response.name.toLowerCase())
          fileStatusTransition = StateTransitionCategories.signoffresponse.name;
        else if (saveRequestObject.requeststatusid === StateEnum.callforrecords.id
          && state.toLowerCase() === StateEnum.review.name.toLowerCase())
          fileStatusTransition = StateTransitionCategories.cfrreview.name;
        else if (saveRequestObject.requeststatusid === StateEnum.harms.id
          && state.toLowerCase() === StateEnum.review.name.toLowerCase())
          fileStatusTransition = StateTransitionCategories.harmsreview.name;
        fileInfoList = files.map(file => {
          return {
            ministrycode: requestNumber.split("-")[0],
            requestnumber: requestNumber,
            filestatustransition: fileStatusTransition,
            filename: file.filename? file.filename : file.name,
          }
        });
      }
      handleModal(true, fileInfoList, files);
    }

    let message = getMessage(saveRequestObject, state, axisRequestId, currentState, requestId, cfrStatus);
    const attchmentFileNameList = attachmentsArray?.map(_file => _file.filename);

    const getDaysRemaining = () => {
      if (currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase() && state.toLowerCase() !== StateEnum.closed.name.toLowerCase() && state.toLowerCase() !== StateEnum.onhold.name.toLowerCase()) {
        return (
          <span> <b> {daysRemainingLDD} DAYS REMAINING </b> </span>
        );
      }
    }

    const addorUpdateConfirmationModal = () => {
      if (state.toLowerCase() === StateEnum.closed.name.toLowerCase() && currentState?.toLowerCase() !== StateEnum.closed.name.toLowerCase()) {
        return (
          <CloseForm saveRequestObject={saveRequestObject} handleClosingDateChange={handleClosingDateChange} handleClosingReasonChange={handleClosingReasonChange} enableSaveBtn={enableSaveBtn} />
        );
      }
      else if ((currentState?.toLowerCase() !== StateEnum.closed.name.toLowerCase()) && ((state.toLowerCase() === StateEnum.review.name.toLowerCase() && [StateEnum.callforrecords.id, StateEnum.harms.id].includes(saveRequestObject.requeststatusid)) || (state.toLowerCase() === StateEnum.response.name.toLowerCase() && saveRequestObject.requeststatusid === StateEnum.signoff.id))) {
        return (
          <FileUpload
            attchmentFileNameList={attchmentFileNameList}
            multipleFiles={multipleFiles}
            mimeTypes={MimeTypeList.stateTransition}
            maxFileSize={MaxFileSizeInMB.stateTransition}
            updateFilesCb={updateFilesCb}
          />
        );
      }
      else if (state.toLowerCase() !== StateEnum.feeassessed.name.toLowerCase() || cfrStatus !== 'init') {
        return (
          <>
          {
          ((currentState?.toLowerCase() !== StateEnum.closed.name.toLowerCase()) ?
            <table className="table table-bordered table-assignedto" cellSpacing="0" cellPadding="0">
              <tbody>
                <tr>
                  <th scope="row">IAO Assigned To</th>
                  <td>{updatedAssignedTo}</td>
                </tr>
              </tbody>
          </table> : null
        (currentState?.toLowerCase() !== StateEnum.closed.name.toLowerCase() && [StateEnum.callforrecords.name.toLowerCase(), StateEnum.consult.name.toLowerCase(), StateEnum.onhold.name.toLowerCase()].includes(state.toLowerCase())) ?
          <table className="table table-bordered table-assignedto">
            <tbody>
              <tr>
                <th scope="row">Ministry Assigned To</th>
                <td>{selectedMinistryAssignedTo}</td>
              </tr>
            </tbody>
          </table> : null
          )}
          </>
        );

      }
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
              <h2 className="state-change-header">{message.title}</h2>
              <span className="title-col2">  {getDaysRemaining()} </span>
              <IconButton className="title-col3" onClick={handleClose}>
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent className={`${reOpenRequest ? 'dialog-content': 'dialog-content-nomargin'}`}>
            <DialogContentText id="state-change-dialog-description" component={'span'}>
            <span className="confirmation-message">
                {message.body}
              </span>
              { addorUpdateConfirmationModal()
              }
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <button className={`btn-bottom btn-save ${isBtnDisabled() ? classes.btndisabled : classes.btnenabled }`} disabled={disableSaveBtn || isBtnDisabled()} onClick={handleSave}>
              {(currentState?.toLowerCase() !== StateEnum.closed.name.toLowerCase()) ?
              "Save Change" : "Re-Open Request"}
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
}

const CloseForm = React.memo(({saveRequestObject, handleClosingDateChange, handleClosingReasonChange, enableSaveBtn}) => {

  const _requestDetails = saveRequestObject;
  const _closingReasons = useSelector(state=> state.foiRequests.closingReasons);

  const today = new Date();
  const [closingDateText, setClosingDate] = React.useState( formatDate(today) );
  const [selectedReason, setClosingReason] = React.useState( 0 );

  //############### replace this with the last status change date
  const lastStatusChangeDate = _requestDetails.lastStatusUpdateDate;

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

    enableSaveBtn();
  }

  const closingReasons = _closingReasons.map((reason)=>{
    return ( <MenuItem key={reason.closereasonid} value={reason.closereasonid} >{reason.name}</MenuItem> )
  });

  return (
    <>
    <div className="row foi-details-row confirm-modal-row first-row">
      <div className="col-lg-6 foi-details-col">
        <div className="confirm-label-area"><b>Applicant: </b><span className="confirm-label-content">{_requestDetails.firstName+" "+_requestDetails.lastName}</span></div>
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
            id="closingModalStartDate"
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
            id="closingModalCloseDate"
            label="Closing Date"
            type="date"
            value={closingDateText || ''}
            onChange={_handleClosingDateChange}
            InputLabelProps={{
              shrink: true,
            }}
            InputProps={{inputProps: { min: _requestDetails.requestProcessStart, max: formatDate(today)} }}
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
            id="closingReason"
            label="Reason for Closing Request"
            inputProps={{ "aria-labelledby": "closingReason-label"}}
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
});