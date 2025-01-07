import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';

export const StateChangeDialog = ({
  modalOpen,
  handleClose,
  handleSave,
  modalMessage,
  createModalOpen,
  handleCreateClose,
  newCFRForm
}: any) => {
    return (
      <>
        <div className="state-change-dialog">
          <Dialog
            open={modalOpen}
            onClose={handleClose}
            aria-labelledby="state-change-dialog-title"
            aria-describedby="state-change-dialog-description"
            maxWidth={'md'}
            fullWidth={true}
            // id="state-change-dialog"
          >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Processing Fee Form Status</h2>
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
                Save Change
              </button>
              <button className="btn-bottom btn-cancel" onClick={handleClose}>
                Cancel
              </button>
            </DialogActions>
          </Dialog>
        </div>
        <div className="state-change-dialog">
          <Dialog
            open={createModalOpen}
            onClose={handleCreateClose}
            aria-labelledby="state-change-dialog-title"
            aria-describedby="state-change-dialog-description"
            maxWidth={'md'}
            fullWidth={true}
            // id="state-change-dialog"
          >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Create New Processing Fee Form </h2>
                <IconButton className="title-col3" onClick={handleCreateClose}>
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
            <DialogContent className={'dialog-content-nomargin'}>
              <DialogContentText id="state-change-dialog-description" component={'span'}>
                <span className="confirmation-message create-new-modal-message">
                  Are you sure you want to create a new, blank Processing Fee form? <br></br>
                  <em>
                    Any unsaved changes will be lost. The previous version will be locked for editing
                    and viewable in the Processing Fee Form History.
                  </em>
                </span>
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <button
                className={`btn-bottom btn-save btn`}
                onClick={newCFRForm}
              >
                Continue
              </button>
              <button className="btn-bottom btn-cancel" onClick={handleCreateClose}>
                Cancel
              </button>
            </DialogActions>
          </Dialog>
        </div>
        <div className="state-change-dialog">
          <Dialog
            open={createModalOpen}
            onClose={handleCreateClose}
            aria-labelledby="state-change-dialog-title"
            aria-describedby="state-change-dialog-description"
            maxWidth={'md'}
            fullWidth={true}
            // id="state-change-dialog"
          >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Create New Processing Fee Form </h2>
                <IconButton className="title-col3" onClick={handleCreateClose}>
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
            <DialogContent className={'dialog-content-nomargin'}>
              <DialogContentText id="state-change-dialog-description" component={'span'}>
                <span className="confirmation-message create-new-modal-message">
                  Are you sure you want to create a new, blank Processing Fee form? <br></br>
                  <em>
                    Any unsaved changes will be lost. The previous version will be locked for editing
                    and viewable in the Processing Fee Form History.
                  </em>
                </span>
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <button
                className={`btn-bottom btn-save btn`}
                onClick={newCFRForm}
              >
                Continue
              </button>
              <button className="btn-bottom btn-cancel" onClick={handleCreateClose}>
                Cancel
              </button>
            </DialogActions>
          </Dialog>
        </div>
      </>
    )
}