
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import '../ConfirmationModal/confirmationmodal.scss';


export default function UnsavedModal({modalOpen, handleClose, handleContinue, modalMessage}) {

    return (
      <div className="state-change-dialog" style={{zIndex:'1401'}}>
        <Dialog style={{zIndex:'1401'}}
          open={modalOpen}
          onClose={handleClose}
          aria-labelledby="state-change-dialog-title"
          aria-describedby="state-change-dialog-description"
          maxWidth={'sm'}
          fullWidth={true}
        >
          {/* <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">CFR Form Status</h2>
              <IconButton className="title-col3" onClick={handleClose}>
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
              </IconButton>
          </DialogTitle> */}
          <DialogContent className={'dialog-content-nomargin'}>
            <DialogContentText id="state-change-dialog-description" component={'span'}>
            <div className="confirmation-message" style={{textAlign: "center"}}>
                {modalMessage}
              </div>
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <button
              className={`btn-bottom btn-save btn`}
              onClick={handleContinue}
            >
              Continue
            </button>
            <button className="btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
}