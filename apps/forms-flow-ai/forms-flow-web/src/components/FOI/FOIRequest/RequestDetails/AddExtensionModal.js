import React, { useState, useEffect, useContext } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import TextField from "@material-ui/core/TextField";
import IconButton from "@material-ui/core/IconButton";
import InputAdornment from "@material-ui/core/InputAdornment";
import CloseIcon from "@material-ui/icons/Close";
import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";
import { ActionContext } from "./ActionContext";
import Grid from "@material-ui/core/Grid";
import "../../customComponents/ConfirmationModal/confirmationmodal.scss";
import DateRangeIcon from "@material-ui/icons/DateRange";
import { formatDate, addBusinessDays } from "../../../../helper/FOI/helper";
import clsx from "clsx";

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
}));

export default function AddExtensionModal({ state, saveRequestObject }) {
  const classes = useStyles();

  const { modalOpen, setModalOpen } = useContext(ActionContext);

  const [reason, setReason] = useState("");
  const [publicBodySelected, setPublicBodySelected] = useState(false)
  const [extendDate, setExtendDate] = useState("");
  const [extendedDate, setExtendedDate] = useState("")

  const initialErrors = {
      reason: false,
      extendDate: false
  }
  const [errors, setErrors] = useState({
    reason: false,
    extendDate: false,
  });

  const [saveLoading, setSaveLoading] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log(modalOpen);
  }, [modalOpen]);

  const handleReasonChange = (e) => {
    setErrors({
        ...errors,
        reason: false,
        extendDate: false
    });
    setExtendDate("")
    setExtendedDate("")
    setReason(e.target.value);
  };

  const handleExtendDateChange = (e) => {
      const numDays = e.target.value
      setExtendDate(numDays);
      setExtendedDate(addBusinessDays(Date(), numDays));
  }

  const handleClose = () => {
    setModalOpen(false);
  };

  const ConditionalRenderContent = ({ children }) => {
    if (loading) {
      return (
        <>
          <DialogContent className={classes.dialogContent}>
            <Grid
              container
              direction="row"
              justifyContent="center"
              className={classes.gridContainer}
              spacing={2}
            >
              <CircularProgress />
            </Grid>
          </DialogContent>
        </>
      );
    }

    return <>{children}</>;
  };

  const errorExists = Object.values(errors).some((isError) => isError);
  const maxExtendDays = publicBodySelected ? 30 : null
  return (
    <div className="state-change-dialog">
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="state-change-dialog-description"
        maxWidth={"md"}
        fullWidth={true}
        // id="state-change-dialog"
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

        <ConditionalRenderContent>
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
                <strong>Start Date:</strong> 06-01-2022
              </Grid>
              <Grid item xs={12} lg={6}>
                <strong>Original Due Date:</strong> 06-01-2022
              </Grid>
              <Grid item xs={12} lg={6}>
                <strong>Current Due Date:</strong> 06-01-2022
              </Grid>

              <Grid item xs={12}>
                <TextField
                  id="outlined-extension-reasons"
                  name="reason"
                  variant="outlined"
                  required
                  select
                  label="Reason for Extension"
                  value={reason}
                  onChange={handleReasonChange}
                  error={errors.reason}
                  fullWidth
                ></TextField>
              </Grid>

              <Grid item xs={6}>
                <TextField
                  id="outlined-extension-reasons"
                  name="extendDate"
                  value={extendDate}
                  type="number"
                  variant="outlined"
                  required
                  label="Extend Due Date"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">Days</InputAdornment>
                    ),
                    inputProps: { min: 1, max: maxExtendDays },
                  }}
                  onChange={handleExtendDateChange}
                  fullWidth
                  error={errors.extendDate}
                ></TextField>
              </Grid>

              <Grid item xs={6}>
                <TextField
                  label="Received Date"
                  type="date"
                  value={extendedDate}
                  disabled
                  InputLabelProps={{
                    shrink: true,
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <DateRangeIcon />
                      </InputAdornment>
                    ),
                  }}
                  variant="outlined"
                  fullWidth
                />
              </Grid>
            </Grid>
          </DialogContent>
        </ConditionalRenderContent>

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
                // onClick={handleSave}
                className={clsx("btn-save", {
                  [classes.btnenabled]: !saveLoading,
                  [classes.btndisabled]: saveLoading,
                })}
                disabled={saveLoading || errorExists}
              >
                Save
                {saveLoading && (
                  <CircularProgress
                    size={14}
                    color={"warning"}
                    style={{ marginLeft: "1em" }}
                  />
                )}
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
