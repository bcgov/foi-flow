import React from "react";
import { Dialog, DialogTitle, DialogContent } from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";
import DocumentSetUI from "./DocumentSetUI";
import { toast } from "react-toastify";

import "./DocumentSet.css";

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
      maxWidth="md"
      fullWidth
      aria-labelledby="document-set-title"
    >
      {/* Close Button */}
      <IconButton aria-label="close" className="ds-close-btn" onClick={onClose}>
        <CloseIcon />
      </IconButton>

      {/* Title */}
      <DialogTitle id="document-set-title">
        <h2 className="state-change-header">
          Create or Update a Document Set
        </h2>
      </DialogTitle>

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
