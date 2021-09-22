import React from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import './confirmationmodal.scss';

export default function ConfirmationModal({openModal, handleModal,state}) {    
    
    const handleClose = () => {
      handleModal(false);
    };

    const handleYes = () => {
      handleModal(true);
    }
  
    return (
      <div>        
        <Dialog
          open={openModal}
          onClose={handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">{state}</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              Are you sure you want to save the request?
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <button className="btn-bottom btn-no" onClick={handleClose}>
              No
            </button>
            <button className="btn-bottom btn-yes" onClick={handleYes}>
              Yes
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }