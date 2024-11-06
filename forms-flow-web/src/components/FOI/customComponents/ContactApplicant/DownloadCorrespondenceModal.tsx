import React from 'react';
import { useDispatch, useSelector } from "react-redux";
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import type { downloadCorrespondenceParams } from './types';

export const DownloadCorrespondenceModal = React.memo(({
  modalOpen,
  setModalOpen,
  handleSave,
  modalFor
}: downloadCorrespondenceParams) => {

  const handleClose = () => {
    setModalOpen(false)
  }

  return (
    <div className="state-change-dialog">        
    <Dialog
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={'md'}
      fullWidth={true}
    >
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Download Correspondence</h2>
          <IconButton aria-label= "close" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
      <DialogContent>
        <DialogContentText id="state-change-dialog-description" component={'span'}>
          Are you sure you want to save this {modalFor == "downloaddraft" ? "draft" : "correspondence"} to your computer? {modalFor == "downloaddraft" ? "Applicant information will not be included." : ""}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <button 
        className="btn-bottom btn-save" 
        onClick={handleSave}
        >
          Download
        </button>
        <button className="btn-cancel" onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  </div>

  )
})
