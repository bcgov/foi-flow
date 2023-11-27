import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';

const OutcomeModal= ({
    showModal,
    setShowModal,
    updateOIPC,
    oipc,
    setOipc,
}) =>{ 

    const handleSave = () => {
        setShowModal(false);
        updateOIPC(oipc);
    };
    const handleClose = () => {
        setShowModal(false);
        setOipc(prev => ({ ...prev, outcomeid: null }));
    };

    return (  
        <div className="state-change-dialog">
            <Dialog
            open={showModal}
            onClose={handleClose}
            maxWidth={'md'}
            fullWidth={true}
            >
            <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Remove OIPC</h2>
              <IconButton className="title-col3" onClick={handleClose}>
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent>
                <DialogContentText component={'span'}>
                    <span className="confirmation-message" style={{display: "flex", flexDirection: "row", justifyContent: "center", color: "black"}}>
                        Are you sure you are ready to select an outcome? This will complete the review and lock all fields
                    </span>
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <button
                className={`btn-bottom btn-save btn`}
                onClick={handleSave}
                >
                Continue
                </button>
                <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
                </button>
            </DialogActions>
            </Dialog>
        </div>
    );
};

export default OutcomeModal;