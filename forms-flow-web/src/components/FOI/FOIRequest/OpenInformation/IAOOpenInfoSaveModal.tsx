import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";

const IAOOpenInfoSaveModal = ({ showModal, saveData, setShowModal }: any) => {
  const handleSave = () => {
    saveData();
    setShowModal(false);
  };
  const handleClose = () => {
    setShowModal(false);
  };

  return (
    <div className="state-change-dialog">
      <Dialog
        open={showModal}
        onClose={() => {
          console.log("onClose");
        }}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="restricted-modal-text"
        maxWidth={"md"}
        fullWidth={true}
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">{"Exemption Request"}</h2>
          <IconButton className="title-col3" onClick={handleClose}>
            <i className="dialog-close-button">Close</i>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="restricted-modal-text" component={"span"}>
            <div className="modal-msg">
              <div className="confirmation-message">{"Are you sure you want to change the state to Exemption Request?"}</div>
              <div className="modal-msg-description">
                <i><span>This will assign the request to the Open Information Queue.</span></i>
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

export default IAOOpenInfoSaveModal;
