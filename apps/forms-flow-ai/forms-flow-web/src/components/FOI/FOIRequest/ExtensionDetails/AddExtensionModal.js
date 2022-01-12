import React, { useState, useEffect, useContext } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import TextField from "@material-ui/core/TextField";
import IconButton from "@material-ui/core/IconButton";
import InputAdornment from "@material-ui/core/InputAdornment";
import CloseIcon from "@material-ui/icons/Close";
import MenuItem from "@material-ui/core/MenuItem";
import { toast } from "react-toastify";
import { makeStyles } from "@material-ui/core/styles";
import { ActionContext } from "./ActionContext";
import Grid from "@material-ui/core/Grid";
import "../../customComponents/ConfirmationModal/confirmationmodal.scss";
import DateRangeIcon from "@material-ui/icons/DateRange";
import {
  formatDate,
  addBusinessDays,
} from "../../../../helper/FOI/helper";
import {
  fetchExtensionReasons,
  saveExtensionRequest,
} from "../../../../apiManager/services/FOI/foiExtensionServices";
import clsx from "clsx";
import { useParams } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    marginTop: "30px",
    marginBottom: "50px",
  },
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
  btndisabled: {
    border: "none",
    backgroundColor: "#eceaea",
    color: "#FFFFFF",
  },
  btnenabled: {
    border: "none",
    backgroundColor: "#38598A",
    color: "#FFFFFF",
  },
  gridContainer: {
    padding: "2em",
  },
  DialogContent: {
    margin: "auto",
  },
  DialogLable: {
    fontWeight: theme.typography.fontWeightBold
  }

}));

export default function AddExtensionModal() {
  const classes = useStyles();
  const { requestId, ministryId } = useParams();

  const {
    modalOpen,
    setModalOpen,
    extensionReasons,
    setExtensionReasons,
    dispatch,
    startDate,
    currentDueDate,
    originalDueDate,
  } = useContext(ActionContext);

  const [reason, setReason] = useState("");
  const [publicBodySelected, setPublicBodySelected] = useState(false)

  const [numberDays, setNumberDays] = useState("");
  const maxExtendDays = reason?.defaultextendedduedays || 100
  
  const [extendedDate, setExtendedDate] = useState("")

  const initialErrors = {
    reason: true,
    numberDays: true,
  };
  const [errors, setErrors] = useState(initialErrors);

  const [saveLoading, setSaveLoading] = useState(false);
 
  const handleReasonChange = (e) => {

    const extensionReason = extensionReasons.find(er => er.extensionreasonid === e.target.value)

    setPublicBodySelected(extensionReason.extensiontype === "Public Body");
    setReason(extensionReason);

    if(extensionReason.defaultextendedduedays) {
      updateExtendedDate(extensionReason.defaultextendedduedays);
    }

  };

  const handleNumberDaysChange = (e) => {
      const numDays = Number(e.target.value)
      updateExtendedDate(numDays);
  }

  const updateExtendedDate = (days) => {
      if (days > maxExtendDays) {
        return;
      }
      
      setNumberDays(days);
      
      setExtendedDate(addBusinessDays(currentDueDate, days));
  }

  const handleClose = () => {
    setModalOpen(false);
  };

  useEffect(() => {
    checkErrors()
  }, [reason, numberDays])

  const checkErrors = () => {
    const updatedErrors = {
      reason: !reason,
      numberDays: !numberDays || numberDays < 1
    }

    let extensionTypeError = false
    if (publicBodySelected) {
      extensionTypeError = numberDays > 30;
    }

    updatedErrors.numberDays = numberDays < 1 || extensionTypeError;
    setErrors({
      ...errors,
      ...updatedErrors,
    });
  }

  const handleSave = () => {
    setSaveLoading(true)
    const extensionRequest = {
      extensionreasonid: reason.extensionreasonid,
      extendedduedays: numberDays,
      extendedduedate: formatDate(extendedDate, "yyyy-MM-dd"),
    };

    saveExtensionRequest({
      data: extensionRequest,
      ministryId: ministryId,
      requestId: requestId,
      callback: () => {
        setModalOpen(false);
        setSaveLoading(false);
        window.history.go(0)
      },
      errorCallBack: (errorMessage) => {
        setSaveLoading(false)        
        errorToast(errorMessage);
      },
      dispatch,
    });
  }

  const errorToast = (errorMessage) => {
    return toast.error(errorMessage, {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: true,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    });
  }

  useEffect(() => {
    if(requestId) {
      fetchExtensionReasons({
          callback: (data) => {
            setExtensionReasons(data)
          },
          dispatch: dispatch
      })
    }
    
  }, [requestId])
  
  const errorExists = Object.values(errors).some((isErrorTrue) => isErrorTrue);

  const getExtensionReasonMenueItems = () => {
    const reasons = extensionReasons.map((extensionReason) => {
      return (
        <MenuItem
          key={`extension-${extensionReason.extensionreasonid}`}
          value={extensionReason.extensionreasonid}
          disabled={!extensionReason.isactive}
        >
          {extensionReason.reason}
        </MenuItem>
      );
    });

    reasons.unshift(
      <MenuItem key={`extension-placeholder`} value={0} disabled={true}>
        Select Reason for Extension
      </MenuItem>
    );
    return reasons
  }

  return (
    <div className="state-change-dialog">
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="state-change-dialog-description"
        maxWidth={"md"}
        fullWidth={true}
        id="add-extension-dialog"
        TransitionProps={{
          onExited: () => {
            setNumberDays("");
            setReason("");
            setExtendedDate("");
          },
        }}
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Extension</h2>
          <IconButton
            className="title-col3"
            onClick={() => setModalOpen(false)}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent
          className="dialog-content"
          style={{
            overflowX: "hidden",
          }}
        >
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            className={classes.gridContainer}
            spacing={2}
          >
            <Grid item xs={12}>
              <span className={classes.DialogLable}>Start Date: </span>
              {startDate}
            </Grid>
            <Grid item xs={12} lg={6}>
              <span className={classes.DialogLable}>Original Due Date: </span>
              {originalDueDate}
            </Grid>
            <Grid item xs={12} lg={6}>
              <span className={classes.DialogLable}>Current Due Date: </span>
              {currentDueDate}
            </Grid>

            <Grid item xs={12}>
              <TextField
                id="outlined-extension-reasons"
                name="reason"
                variant="outlined"
                required
                select
                label="Reason for Extension"
                value={reason.extensionreasonid || 0}
                onChange={handleReasonChange}
                error={errors.reason}
                fullWidth
              >
                {extensionReasons && getExtensionReasonMenueItems()}
              </TextField>
            </Grid>

            <Grid item xs={6}>
              <TextField
                id="outlined-extension-number-days"
                name="numberDays"
                value={numberDays || 0}
                type="number"
                variant="outlined"
                required
                label="Extended Due Days"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">Days</InputAdornment>
                  ),
                  inputProps: { min: 1, max: maxExtendDays },
                }}
                onChange={handleNumberDaysChange}
                fullWidth
                error={errors.numberDays}
              ></TextField>
            </Grid>

            <Grid item xs={6}>
              <TextField
                label="Extended Due Date"
                type="date"
                value={extendedDate}
                InputLabelProps={{
                  shrink: true,
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <DateRangeIcon />
                    </InputAdornment>
                  ),
                  readOnly: true,
                }}
                variant="outlined"
                fullWidth
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions className="dialog-content-nomargin">
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            className={classes.gridContainer}
            spacing={2}
          >
            <Grid item xs={6}>
              <button
                className={`btn-save`}
                style={{ width: "100%" }}
                className={clsx("btn-save", {
                  [classes.btnenabled]: !(saveLoading || errorExists),
                  [classes.btndisabled]: saveLoading || errorExists,
                })}
                disabled={saveLoading || errorExists}
                onClick={handleSave}
              >
                Save
              </button>
            </Grid>
            <Grid item xs={6}>
              <button
                className="btn-cancel"
                style={{ width: "100%" }}
                onClick={handleClose}
                disabled={saveLoading}
              >
                Cancel
              </button>
            </Grid>
          </Grid>
        </DialogActions>
      </Dialog>
    </div>
  );
}
