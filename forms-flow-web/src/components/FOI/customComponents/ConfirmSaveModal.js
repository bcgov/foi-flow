import React, { useEffect, useState } from "react";
import Dialog from "@material-ui/core/Dialog";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";
import Checkbox from "@material-ui/core/Checkbox";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { makeStyles } from "@material-ui/core/styles";
import WarningIcon from "@material-ui/icons/Warning";

const useStyles = makeStyles((theme) => ({
  dialogPaper: {
    maxWidth: "850px",
    width: "100%",
    borderRadius: "0px",
    overflow: "hidden",
  },
  closeButton: {
    backgroundColor: "#003366",
    color: "#fff",
    borderRadius: 0,
    padding: "10px",
    position: "absolute",
    right: "0px",
    top: "0px",
    zIndex: 1000,
    "&:hover": {
      backgroundColor: "#002447",
    },
    "& .MuiSvgIcon-root": {
      fontSize: "30px",
    }
  },
  contentFrame: {
    padding: "20px 35px 20px 40px",
    backgroundColor: "#fff",
    position: "relative",
  },
  titleText: {
    fontSize: "28px",
    fontWeight: "bold",
    margin: "0 0 2px 0",
    color: "#003366",
    fontFamily: "BCSans-Bold, sans-serif !important",
  },
  subtitle: {
    fontSize: "16px",
    fontWeight: "bold",
    margin: "0 0 10px 0",
    color: "#2D2D2D",
    fontFamily: "BCSans-Bold, sans-serif !important",
  },
  selectAllContainer: {
    marginBottom: "12px",
  },
  ministriesGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(9, 1fr)",
    marginBottom: "10px",
    gap: "4px",
  },
  ministryCheckbox: {
    marginRight: 0,
    "& .MuiFormControlLabel-label": {
      fontSize: "13px",
      //fontWeight: "600",
      color: "#000",
      //marginLeft: "-4px",
      //fontFamily: "BCSans-Bold, sans-serif !important",
    },
  },
  checkbox: {
    //color: "#2E8540 !important",
    padding: "4px",
    "&.Mui-checked": {
      color: "#2E8540 !important",
    },
    "& .MuiSvgIcon-root": {
      fontSize: "24px",
    }
  },
  warningBox: {
    backgroundColor: "#FFF9E1",
    border: "1px solid #FCBA19",
    padding: "12px",
    display: "flex",
    alignItems: "flex-start",
    marginBottom: "25px",
  },
  warningIcon: {
    color: "#003366",
    marginRight: "16px",
    fontSize: "24px",
    marginTop: "4px",
  },
  warningTextContainer: {
    display: "flex",
    flexDirection: "column",
  },
  warningContent: {
    fontSize: "15px",
    color: "#000",
    lineHeight: "1.6",
    fontFamily: "BCSans, sans-serif !important",
  },
  callForRecords: {
    fontWeight: "bold",
    fontFamily: "BCSans-Bold, sans-serif !important",
  },
  actionsContainer: {
    display: "flex",
    justifyContent: "space-between",
    gap: "20px",
    marginTop: "10px",
  },
  proceedButton: {
    backgroundColor: "#003366",
    color: "#fff",
    flex: 1,
    height: "28px",
    border: "none",
    borderRadius: "4px",
    fontSize: "13px",
    fontWeight: "bold",
    cursor: "pointer",
    fontFamily: "BCSans-Bold, sans-serif !important",
    "&:hover": {
      backgroundColor: "#002447",
    },
  },
  cancelButton: {
    backgroundColor: "#fff",
    color: "#000",
    flex: 1,
    height: "28px",
    border: "1px solid #707070",
    borderRadius: "4px",
    fontSize: "13px",
    fontWeight: "bold",
    cursor: "pointer",
    fontFamily: "BCSans-Bold, sans-serif !important",
    "&:hover": {
      backgroundColor: "#f5f5f5",
    },
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

  useEffect(() => {
    if (allMinistries.length > 0) {
      const initialState = {};
      allMinistries.forEach((ministry) => {
        initialState[ministry.code] = selectedMinistries.includes(
          ministry.code
        );
      });
      setMinistries(initialState);

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
      maxWidth="md"
      fullWidth
    >
      <IconButton
        className={classes.closeButton}
        onClick={handleClose}
        aria-label="close"
      >
        <CloseIcon />
      </IconButton>

      <div className={classes.contentFrame}>
        <h2 className={classes.titleText}>Confirm and Proceed</h2>
        <h6 className={classes.subtitle}>
          You've selected {selectedCount} ministries and public bodies.
        </h6>

        <div className={classes.selectAllContainer}>
          <FormControlLabel
            control={
              <Checkbox
                checked={selectAll}
                onChange={handleSelectAll}
                className={classes.checkbox}
              />
            }
            label="Select all"
            className={classes.ministryCheckbox}
          />
        </div>

        <div className={classes.ministriesGrid}>
          {allMinistries.map((ministry) => (
            <FormControlLabel
              key={ministry.code}
              className={classes.ministryCheckbox}
              control={
                <Checkbox
                  checked={ministries[ministry.code] || false}
                  onChange={handleMinistryChange(ministry.code)}
                  className={classes.checkbox}
                  size="small"
                />
              }
              label={ministry.code}
            />
          ))}
        </div>

        <div className={classes.warningBox}>
          <WarningIcon className={classes.warningIcon} />
          <div className={classes.warningTextContainer}>
            <div className={classes.warningContent}>
              This screen will close and the request will update to Intake in progress.
            </div>
            <div className={classes.warningContent} style={{ marginTop: "12px" }}>
              When the request is moved to 'Open' then the requests will be created for each selected Ministry
              and will be ready to move to the{" "}
              <span className={classes.callForRecords}>"Call for Records"</span>{" "}
              process.
            </div>
          </div>
        </div>

        <div className={classes.actionsContainer}>
          <button className={classes.proceedButton} onClick={handleProceed}>
            Proceed
          </button>
          <button className={classes.cancelButton} onClick={handleClose}>
            Cancel
          </button>
        </div>
      </div>
    </Dialog>
  );
};

export default ConfirmSaveModal;

