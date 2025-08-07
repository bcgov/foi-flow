import { useState, useEffect } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import { DialogContentText, IconButton } from "@material-ui/core";
import CloseIcon from '@material-ui/icons/Close';
import './requesthistoryexportmodal.scss';


const RequestHistoryExportModal = ({
  exportSelectedHistory,
  showModal,
  closeModal,
}) => {
  const [exportOptions, setExportOptions] = useState({
    isApplicantCorrespondenceChecked: true,
    isCommentsChecked: true,
    isRequestDetailsChecked: true,
  });

  const handleExportRequestHistory = () => {
    exportSelectedHistory(exportOptions);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };

  useEffect(() => {
    setExportOptions({
      isApplicantCorrespondenceChecked: true,
      isCommentsChecked: true,
      isRequestDetailsChecked: true,
    });
  }, [showModal]);

  return (
    <>
      <Dialog open={showModal} onClose={handleClose}>
        <div className="request-history-modal-header">
          <DialogTitle disableTypography id="request-history-dialog-title">
            <h2 className="request-history-export-header">Export Request History</h2>
          </DialogTitle>
          <IconButton className="title-col3" onClick={handleClose}>
            <i className="dialog-close-button">Close</i>
            <CloseIcon className="close-icon" />
          </IconButton>
        </div>
        <DialogContent className="request-history-dailog-content">
          <DialogContentText id="request-history-modal-text" component={'span'}>
            <div className="request-history-message">
              Are you sure you want to export request history? A PDF will be created based on your selection.
            </div>
            <div className='request-history-msg-description'>
              Select one or more you wish to export:
            </div>
          </DialogContentText>
          <div id="request-history-checkbox-selection">
            <FormControlLabel id="request-history-areas-label" control={
              <Checkbox checked={exportOptions.isApplicantCorrespondenceChecked}
                onChange={() => setExportOptions({ ...exportOptions, isApplicantCorrespondenceChecked: !exportOptions.isApplicantCorrespondenceChecked })}
              />}
              label="Applicant Correspondence"
            />
            <FormControlLabel id="request-history-areas-label" control={
              <Checkbox checked={exportOptions.isCommentsChecked}
                onChange={() => setExportOptions({ ...exportOptions, isCommentsChecked: !exportOptions.isCommentsChecked })}
              />}
              label="Comments"
            />
            <FormControlLabel id="request-history-areas-label" control={
              <Checkbox checked={exportOptions.isRequestDetailsChecked}
                onChange={() => setExportOptions({ ...exportOptions, isRequestDetailsChecked: !exportOptions.isRequestDetailsChecked })}
              />}
              label="Request Details"
            />
          </div>
        </DialogContent>
        <DialogActions>
          <button onClick={handleExportRequestHistory} disabled={!(exportOptions.isApplicantCorrespondenceChecked || exportOptions.isCommentsChecked || exportOptions.isRequestDetailsChecked)} className="btn-bottom btn-save">
            Continue
          </button>
          <button onClick={handleClose} className="export-btn-cancel">
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RequestHistoryExportModal;
