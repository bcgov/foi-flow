import React from "react";
import { Dialog, DialogTitle, DialogContent } from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";
import DocumentSetUI from "./DocumentSetUI";
import { toast } from "react-toastify";
import "../ConfirmationModal/confirmationmodal.scss";
import "./DocumentSet.css";
import Grid from "@mui/material/Grid";

export default function DocumentSetModal({
                                           open,
                                           onClose,
                                           onSave,
                                           records,
                                           groups,
                                           requestId,
                                           ministryId
                                         }) {
  const refreshData = () => {
    toast.success("Document Set saved successfully!");
    if (onClose) onClose();
    if (onSave) onSave();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={"md"}
      fullWidth={true}
    >
      <Grid container justifyContent="space-between" alignItems="center" sx={{ ml: -3 }}>
        <DialogTitle
          disableTypography
          id="document-set-title"
          className="add-attachment-modal-title"
        >
          <h2 className="state-change-header">
            Create or Update a Document Set
          </h2>
        </DialogTitle>

        <IconButton
          disableRipple
          disableFocusRipple
          aria-label="close"
          onClick={onClose}
          classes={{ root: "close-btn" }}
        >
          <CloseIcon />
        </IconButton>
      </Grid>
      {/* Content */}
      <DialogContent className="ds-content">
          <DocumentSetUI
            records={records}
            groups={groups}
            requestId={requestId}
            ministryId={ministryId}
            onSave={refreshData}
          />
      </DialogContent>

      {/* Footer */}
      <div className="ds-footer">
          <>
            <button className="btn-bottom btn-save" onClick={() => window._saveDocumentSet?.()}>
              Save
            </button>

            <button className="btn-bottom btn-cancel" onClick={onClose}>
              Cancel
            </button>
          </>
      </div>
    </Dialog>
  );
}
