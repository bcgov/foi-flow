import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';

export const RemoveLinkedRequestModal = ({
    modalOpen,
    handleClose,
    handleSave,
}) => {
    const modalTitle = "Confirm Removing Linked Request";
    const modalMessage = `Are you sure you want to remove the link for this request? Clicking confirm will remove the linked request from both requests. It will not save any other detail on the request page.`;
    return (
        <>
        <div className="state-change-dialog">
          <Dialog
            open={modalOpen}
            onClose={handleClose}
            maxWidth={'md'}
            fullWidth={true}
            PaperProps={{ style: { padding: 15 } }}
          >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 style={{marginLeft: "0px"}} className="state-change-header">{modalTitle}</h2>
                <IconButton className="title-col3" onClick={handleClose}>
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
            <DialogContent className={'dialog-content-nomargin'}>
              <DialogContentText id="state-change-dialog-description" component={'span'}>
              <span className="confirmation-message">
                  {modalMessage}
                </span>
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <button
                className={`btn-bottom btn-save btn`}
                onClick={handleSave}
              >
                Confirm
              </button>
              <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
              </button>
            </DialogActions>
          </Dialog>
        </div> 
        </>
    );
}