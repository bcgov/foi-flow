import React, { useEffect, useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import '../confirmationmodal.scss';
import { makeStyles } from '@material-ui/core/styles';

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
}));

export default function RenameModal({ openModal, handleModal, requestNumber, requestId, attachment }) {

    const classes = useStyles();

    const [errorMessage, setErrorMessage] = useState();
    const [filename, setFilename] = useState();

    const validateFilename = (str) => {
      return /^[a-z0-9_.@()-]+\.txt$/i.test(str);
    };

    const updateFilename = (e) => {
      if(validateFilename(e.target.value)) {
        setFilename(e.target.value);
      } else {
        setErrorMessage("invalid characters");
      }
    };

    const handleClose = () => {
        //handleModal(false);
        if (files.length > 0) {
            if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
                // window.location.reload();
                handleModal(false);
            }
        }
        else {
            // window.location.reload();
            handleModal(false);
        }
    };

    const handleSave = () => {
        handleModal(true, filename);
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
        >
          <DialogTitle disableTypography id="state-change-dialog-title">
              <IconButton onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-description" component={'span'}>
              <TextField                            
                label="Rename Attachment" 
                InputLabelProps={{ shrink: true, }} 
                variant="outlined"                             
                value={attachment && attachment.filename ? attachment.filename.split('.').shift() : ""}
                fullWidth
                onChange={updateFilename}
                />
            </DialogContentText>
            {errorMessage ? errorMessage.map(error => 
              <div className="error-message-container">
                <p>{error}</p>
              </div>
              )
              : null}
          </DialogContent>
          <DialogActions>            
            <button className="btn-bottom btn-save" onClick={handleSave}>
              Continue
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
}
