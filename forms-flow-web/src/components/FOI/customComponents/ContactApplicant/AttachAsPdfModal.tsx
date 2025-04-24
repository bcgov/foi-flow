import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

export const AttachAsPdfModal = React.memo(({
  modalOpen,
  handleClose,
  handleAttachAsPdf,
}: any) => {

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
          <h2 className="state-change-header">Warning: Attaching As PDF File</h2>
          <IconButton aria-label= "close" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="state-change-dialog-description" component={'span'}>
          <div className="state-change-email-note">
            The current content will no longer be available for editing after attaching it as a PDF file. If you may still need to make edits, please save a draft first. 
          </div>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
      {
        <button 
        className="btn-bottom btn-save" 
        onClick={handleAttachAsPdf}
        >
          Attach as PDF
        </button>
      }
        <button className="btn-cancel" onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  </div>

  )
})
