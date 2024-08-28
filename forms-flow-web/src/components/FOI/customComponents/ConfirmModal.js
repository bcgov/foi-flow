
import React, { useEffect, useState }  from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@mui/material/TextField';


const ConfirmModal= ({
    modalMessage,
    modalDescription,
    showModal,
    saveAssigneeDetails,
    assigneeVal,
    assigneeName,
    resetModal
}) =>{ 

    const [modalOpen, setModalOpen] = useState(showModal);

    const handleSave = () => {
        setModalOpen(false);
        saveAssigneeDetails(assigneeVal,assigneeName);
        resetModal();
    };

    const handleClose = () => {
        setModalOpen(false);
        resetModal();
    };

    useEffect(() => {
        setModalOpen(showModal);
      }, [showModal]);

    return (  
        <>
        <div className="state-change-dialog">
            <Dialog
            open={modalOpen}
            onClose={handleClose}
            aria-labelledby="state-change-dialog-title"
            aria-describedby="restricted-modal-text"
            maxWidth={'md'}
            fullWidth={true}
            >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Restricted File</h2>
                <IconButton className="title-col3" onClick={handleClose}>
                    <i className="dialog-close-button">Close</i>
                    <CloseIcon />
                </IconButton>
                </DialogTitle>
            <DialogContent>
                <DialogContentText id="restricted-modal-text" component={'span'}>
                <div className="modal-msg">
                    <div className="confirmation-message">
                        {modalMessage}
                    </div>
                    <div className='modal-msg-description'>
                        <i>{modalDescription}</i>
                    </div>
                </div>
            </DialogContentText>
            </DialogContent>
            <DialogActions>
                <button
                className={`btn-bottom btn-save btn`}
                onClick={handleSave}
                style={{marginTop:'0px'}}
                //disabled={!isIAORestrictedFileManager || isRequestAssignedToTeam()}
                >
                Save Change
                </button>
                <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
                </button>
            </DialogActions>
            </Dialog>
        </div>
        </>
    );
};

export default ConfirmModal;
