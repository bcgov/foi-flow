import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';

const AmendModal= ({
    showModal,
    setShowModal,
    updateOIPC,
    oipc,
    setOipc,
}) =>{ 

    const handleSave = () => {
        setShowModal(false);
        const newOIPCObj = oipc;
        newOIPCObj.outcomeid = null;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    };
    const handleClose = () => {
        setShowModal(false);
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
            <h2 className="state-change-header">Amend Outcome</h2>
            <IconButton className="title-col3" onClick={handleClose}>
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
            </IconButton>
            </DialogTitle>
            <DialogContent>
                <DialogContentText component={'span'}>
                    <span className="confirmation-message" style={{display: "flex", flexDirection: "row", justifyContent: "center", color: "black", marginLeft: "35px"}}>
                        Are you sure you want to amend this completed OIPC review? You will need to re-select an outcome to close it again.
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

export default AmendModal;