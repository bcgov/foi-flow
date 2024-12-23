import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";

const OAOpenInfoApproveModal = ({ showApproveModal, saveData, setShowApproveModal }: any) => {
  const handleSave = () => {
    saveData();
    setShowApproveModal(false);
  };
  const handleClose = () => {
    setShowApproveModal(false);
  };

  return (
    <div className="state-change-dialog">
      <Dialog
        open={showApproveModal}
        onClose={() => {
          handleClose()
        }}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="restricted-modal-text"
        maxWidth={"md"}
        fullWidth={true}
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">{"Exemption Approved"}</h2>
          <IconButton className="title-col3" onClick={handleClose}>
            <i className="dialog-close-button">Close</i>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="restricted-modal-text" component={"span"}>
            <div className="modal-msg">
              <div className="confirmation-message">{"Are you sure you want to approve this exemption?"}</div>
              <div className="modal-msg-description">
                <i><span>The request will not be eligible for publication and will be removed from the OI Queue.</span></i>
              </div>
            </div>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button
            className={`btn-bottom btn-save btn`}
            onClick={handleSave}
            disabled={false}
          >
            Save Change
          </button>
          <button className="btn-bottom btn-cancel" onClick={handleClose}>
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default OAOpenInfoApproveModal;
