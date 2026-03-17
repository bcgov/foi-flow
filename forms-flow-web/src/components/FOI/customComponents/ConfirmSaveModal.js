import React, { useEffect, useState } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import CloseIcon from "@material-ui/icons/CloseOutlined";
import IconButton from "@material-ui/core/IconButton";
import Checkbox from "@material-ui/core/Checkbox";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { makeStyles } from "@material-ui/core/styles";
import WarningIcon from "@material-ui/icons/Warning";

const useStyles = makeStyles((theme) => ({
  dialogPaper: {
    maxWidth: "700px",
    width: "100%",
    fontFamily: "BCSans, sans-serif !important",
  },
  dialogTitle: {
    padding: "35px 35px 10px 35px",
  },
  titleHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    margin: 0,
  },
  titleText: {
    //fontSize: "xx-large",
    fontWeight: "bold",
    margin: "0 0 8px 0",
    color: "#036",
    fontFamily: "BCSans-Bold, sans-serif !important",
    //lineHeight: "1.6",
    marginLeft: "-3px",
  },
  subtitle: {
    fontSize: "14px",
    fontWeight: "normal",
    margin: "4px 0 0 0",
    color: "#313132",
    fontFamily: "BCSans-Bold, sans-serif !important",
  },
  closeButton: {
    padding: "4px",
    marginTop: "-4px",
    marginRight: "-8px",
  },
  dialogContent: {
    color: "#2D2D2D",
    padding: "0px 35px",
  },
  selectAllContainer: {
    marginBottom: "16px",
    paddingBottom: "12px",
    color: "#2D2D2D",
  },
  ministriesGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(9, 1fr)",
    marginBottom: "20px",
  },
  ministryCheckbox: {
    "& .MuiFormControlLabel-label": {
      fontSize: "13px",
      color: "#2D2D2D",
      fontFamily: "BCSans, sans-serif !important",
      margin: "0 !important",
    },
  },
  warningBox: {
    backgroundColor: "#FEF1D8",
    border: "1px solid #F8BB47",
    borderRadius: "4px",
    padding: "12px",
    marginBottom: "16px",
  },
  warningIcon: {
    color: "#013366",
    marginRight: "8px",
    marginTop: "2px",
    fontSize: "20px",
  },
  warningText: {
    fontSize: "13px",
    color: "#313132",
    margin: 0,
    lineHeight: "2.0",
    fontFamily: "BCSans, sans-serif !important",
  },
  infoText: {
    fontSize: "13px",
    color: "#313132",
    margin: "0px 30px",
    lineHeight: "1.6",
    fontFamily: "BCSans, sans-serif !important",
  },
  callForRecords: {
    fontWeight: "600",
    color: "#313132",
    fontFamily: "BCSans-Bold, sans-serif !important",
  },
  dialogActions: {
    padding: "20px 35px 35px 35px",
    borderTop: "1px solid #e0e0e0",
    justifyContent: "flex-end",
    gap: "12px",
  },
  proceedButton: {
    backgroundColor: "#003366",
    color: "#fff",
    padding: "8px 32px",
    border: "none",
    borderRadius: "4px",
    fontSize: "14px",
    fontWeight: "500",
    cursor: "pointer",
    fontFamily: "BCSans-Bold, sans-serif !important",
    "&:hover": {
      backgroundColor: "#002447",
    },
  },
  cancelButton: {
    marginRight: "20px",
    marginTop: "10px",
    position: "relative",
    width: "30%",
    fontFamily: "BCSans-Bold, sans-serif !important",
    border: "1px solid #38598A",
    backgroundColor: "#FFFFFF",
    color: "#38598A",
    borderRadius: "3px",
    fontSize: "small",
    height: "30px",
    flexBasis: "50%",
    fontFamily: "BCSans-Bold, sans-serif !important",
    marginTop: "10px",
  },
}));

const ConfirmSaveModal = ({
  showModal,
  selectedMinistries = [],
  allMinistries = [],
  onProceed,
  onCancel,
}) => {
  const classes = useStyles();
  const [modalOpen, setModalOpen] = useState(showModal);
  const [ministries, setMinistries] = useState({});
  const [selectAll, setSelectAll] = useState(false);

  // Initialize ministries state
  useEffect(() => {
    if (allMinistries.length > 0) {
      const initialState = {};
      allMinistries.forEach((ministry) => {
        initialState[ministry.code] = selectedMinistries.includes(
          ministry.code
        );
      });
      setMinistries(initialState);

      // Check if all are selected
      const allSelected = Object.values(initialState).every((val) => val);
      setSelectAll(allSelected);
    }
  }, [allMinistries, selectedMinistries]);

  useEffect(() => {
    setModalOpen(showModal);
  }, [showModal]);

  const handleSelectAll = (event) => {
    const checked = event.target.checked;
    setSelectAll(checked);

    const updatedMinistries = {};
    Object.keys(ministries).forEach((key) => {
      updatedMinistries[key] = checked;
    });
    setMinistries(updatedMinistries);
  };

  const handleMinistryChange = (code) => (event) => {
    const updatedMinistries = {
      ...ministries,
      [code]: event.target.checked,
    };
    setMinistries(updatedMinistries);

    // Update select all if all are checked
    const allSelected = Object.values(updatedMinistries).every((val) => val);
    setSelectAll(allSelected);
  };

  const handleProceed = () => {
    const selected = Object.keys(ministries).filter((key) => ministries[key]);
    setModalOpen(false);
    onProceed?.(selected);
  };

  const handleClose = () => {
    setModalOpen(false);
    onCancel?.();
  };

  const selectedCount = Object.values(ministries).filter(Boolean).length;

  return (
    <Dialog
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="confirm-proceed-dialog-title"
      classes={{ paper: classes.dialogPaper }}
    >
      <DialogTitle
        id="confirm-proceed-dialog-title"
        className={classes.dialogTitle}
      >
        <div className={classes.titleHeader}>
          <div>
            <h2 className={classes.titleText}>Confirm and Proceed</h2>
            <h6 className={classes.subtitle}>
              You've selected {selectedCount} ministries and public bodies.
            </h6>
          </div>
          <IconButton
            className={classes.closeButton}
            onClick={handleClose}
            aria-label="close"
          >
            <CloseIcon />
          </IconButton>
        </div>
      </DialogTitle>

      <DialogContent className={classes.dialogContent}>
        <DialogContentText component="div">
          {/* Select All Checkbox */}
          <div>
            <FormControlLabel
              control={
                <Checkbox
                  checked={selectAll}
                  onChange={handleSelectAll}
                //color="primary"
                />
              }
              label="Select all"
            />
          </div>

          {/* Ministries Grid */}
          <div className={classes.ministriesGrid}>
            {allMinistries.map((ministry) => (
              <FormControlLabel
                key={ministry.code}
                className={classes.ministryCheckbox}
                control={
                  <Checkbox
                    checked={ministries[ministry.code] || false}
                    onChange={handleMinistryChange(ministry.code)}
                    color="primary"
                    size="small"
                  />
                }
                label={ministry.code}
              />
            ))}
          </div>

          {/* Warning Message */}
          <div className={classes.warningBox}>
            <WarningIcon className={classes.warningIcon} />
            <span className={classes.warningText}>
              This screen will close, and you'll be redirected to the queue
              where you can view all related sub-tickets.
            </span>
            {/* Info Text */}
            <p className={classes.infoText}>
              When you proceed, tickets will be created for each selected
              ministry and sent to ministry coordinators as part of the{" "}
              <span className={classes.callForRecords}>"Call for Records"</span>{" "}
              process.
            </p>
          </div>
        </DialogContentText>
      </DialogContent>

      <DialogActions>
        <button className={`btn-bottom btn-save btn`} onClick={handleProceed}>
          Proceed
        </button>
        <button className={classes.cancelButton} onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmSaveModal;
