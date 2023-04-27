import React, { useState, useEffect } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";

const DisableDivisionModal = ({
  initialDivision,
  disableDivision,
  showModal,
  closeModal,
}) => {
  const [division, setDivision] = useState(initialDivision);

  const handleDisable = () => {
    disableDivision(division);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };

  useEffect(() => {
    setDivision(initialDivision);
  }, [initialDivision, showModal]);

  return (
    <>
      <Dialog fullWidth maxWidth="xs" open={showModal} onClose={handleClose}>
        <DialogTitle>Delete Division</DialogTitle>
        <DialogContent>
          <DialogContentText component={"span"}>
            <div>
              Are you sure you want to delete {division ? division.name : ""}?
            </div>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button onClick={handleDisable} className="btn-bottom btn-save">
            Delete
          </button>
          <button onClick={handleClose} className="btn-bottom btn-cancel">
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DisableDivisionModal;
