import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';

export const GenerateInvoiceModal = ({
    modalOpen,
    handleClose,
    handleSave,
    cfrFees,
}) => {
    const isAcutalFees = cfrFees?.actualtotaldue > 0;
    const modalTitle = isAcutalFees ? "Oustanding Fee Invoice" : "Fee Estimate Invoice";
    const modalMessage = `By selecting generate invoice, you will be creating a new invoice (and new invoice #) based on ${isAcutalFees ? "actual" : "estimated"} hours. Are you sure you want to generate a new invoice?`;
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
          >
            <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">{modalTitle}</h2>
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
                Generate Invoice
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