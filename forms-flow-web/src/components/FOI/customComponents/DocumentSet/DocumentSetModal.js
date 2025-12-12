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
                                           ministryId,
                                           uiState = "create",      // "create" | "tooLarge"
                                           selectedSize = null      // Only used for tooLarge
                                         }) {
  const refreshData = () => {
    toast.success("Document Set saved successfully!");
    if (onClose) onClose();
    if (onSave) onSave();
  };

  const isTooLarge = uiState === "tooLarge";

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={isTooLarge ? "sm" : "md"}
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
          {isTooLarge ? "Reduce File Size to Continue" : "Create a Document Set"}
        </h2>
      </DialogTitle>

      {/* Content */}
      <DialogContent className="ds-content" style={{ textAlign: isTooLarge ? "center" : "left" }}>
        {isTooLarge ? (
          <>
            <p style={{ marginTop: 8, fontWeight: 600 }}>
              Your selection is too large to process (over 1GB).
            </p>

            <p>Please reduce the number of files in this set.</p>

            {selectedSize && (
              <p style={{ marginTop: 12 }}>
                Total selected size: <strong>{selectedSize}</strong>
              </p>
            )}
          </>
        ) : (
          <DocumentSetUI
            records={records}
            groups={groups}
            requestId={requestId}
            ministryId={ministryId}
            onSave={refreshData}
          />
        )}
      </DialogContent>

      {/* Footer */}
      <div className="ds-footer">
        {isTooLarge ? (
          <button className="btn-bottom btn-save" onClick={onClose}>
            Close
          </button>
        ) : (
          <>
            <button className="btn-bottom btn-save" onClick={() => window._saveDocumentSet?.()}>
              Save
            </button>

            <button className="btn-bottom btn-cancel" onClick={onClose}>
              Cancel
            </button>
          </>
        )}
      </div>
    </Dialog>
  );
}
