import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";

const OpenInfoConfirmationModal = ({
  confirm,
  setModal,
  modal,
}: any) => {
  const handleConfirmation = () => {
    if (modal.title === "Exemption Request") {
      confirm();
    }
    if (modal.title === "Change Publication Date") {
      confirm(modal.confirmationData);
    }
    if (modal.title === "Exemption Approved") {
      confirm();
    } 
    if (modal.title === "Exemption Denied") {
      confirm();
    }
    setModal((prev : any) => ({
      ...prev,     
      show: false, 
      title: "", 
      message: "", 
      description: "",
      confirmButtonTitle: "",
      confirmationData: null,
    }));
  };
  const handleClose = () => {
    setModal((prev : any) => ({
      ...prev,     
      show: false, 
      title: "", 
      message: "", 
      description: "",
      confirmButtonTitle: "",
      confirmationData: null,
    }));
  };

  return (
    <div className="state-change-dialog">
      <Dialog
        open={modal.show}
        onClose={() => {
          handleClose();
        }}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="restricted-modal-text"
        maxWidth={"md"}
        fullWidth={true}
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">{modal.title}</h2>
          <IconButton className="title-col3" onClick={handleClose}>
            <i className="dialog-close-button">Close</i>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="restricted-modal-text" component={"span"}>
            <div className="modal-msg">
              <div className="confirmation-message">{modal.description}</div>
              <div className="modal-msg-description">
                <i>
                  <span>{modal.message}</span>
                </i>
              </div>
            </div>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button
            className={`btn-bottom btn-save btn`}
            onClick={handleConfirmation}
            disabled={false}
          >
            {modal.confirmButtonTitle}
          </button>
          <button className="btn-bottom btn-cancel" onClick={handleClose}>
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default OpenInfoConfirmationModal;
