import React from "react";
import { Dialog, DialogTitle, DialogContent } from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";

export default function DocumentSetDeleteModal({
                                                           open,
                                                           onClose,
                                                           onConfirm,
                                                           loading = false,
                                                         }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <IconButton
        aria-label="close"
        className="ds-close-btn"
        onClick={onClose}
      >
        <CloseIcon />
      </IconButton>

      <DialogTitle>
        <h2>Remove Record from Document Set</h2>
      </DialogTitle>

      <DialogContent style={{ textAlign: "center" }}>
        <p style={{ fontWeight: 600 }}>
          Are you sure you want to remove this record from the Document Set?
        </p>
      </DialogContent>

      <div className="ds-footer">
        <button
          className="btn-bottom btn-save"
          disabled={loading}
          onClick={onConfirm}
        >
          Delete
        </button>

        <button
          className="btn-bottom btn-cancel"
          disabled={loading}
          onClick={onClose}
        >
          Cancel
        </button>
      </div>
    </Dialog>
  );
}
