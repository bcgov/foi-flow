import React, { useState, useContext, useEffect, useMemo } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import TextField from "@material-ui/core/TextField";
import IconButton from "@material-ui/core/IconButton";
import InputAdornment from "@material-ui/core/InputAdornment";
import CloseIcon from "@material-ui/icons/Close";
import MenuItem from "@material-ui/core/MenuItem";
import { makeStyles } from "@material-ui/core/styles";
import { ActionContext } from "./ActionContext";
import Grid from "@material-ui/core/Grid";
import "./extensionscss.scss";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormControl from "@material-ui/core/FormControl";
import CircularProgress from "@material-ui/core/CircularProgress";
import {
  formatDate,
  addBusinessDays,
  removeBusinessDays,
  ConditionalComponent,
} from "../../../../helper/FOI/helper";
import clsx from "clsx";
import {
  extensionStatusId,
  extensionStatusLabel,
  MimeTypeList,
  MaxFileSizeInMB,
} from "../../../../constants/FOI/enum";
import FileUpload from "../../customComponents/FileUpload";
import {
  uploadFiles,
  checkPublicBodyError,
  filterExtensionReason,
  errorToast,
  getPublicBodyTotalExtendedDays,
  getMaxExtendDays,
  getSelectedDays
} from "./utils";
import { fetchExtensions } from "../../../../apiManager/services/FOI/foiExtensionServices";
import { fetchFOIRequestAttachmentsList } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRequestNotesList } from "../../../../apiManager/services/FOI/foiRequestNoteServices";
import { useParams } from "react-router-dom";
import { setRequestDueDate } from "../../../../actions/FOI/foiRequestActions";

const useStyles = makeStyles((theme) => ({
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
    fontWeight: theme.typography.fontWeightBold,
  },
  fullWidth: {
    width: "100%",
    padding: 0,
  },
  fileUploadContainer: {
    padding: "0",
  },
  fileUploadPreview: {
    width: "100%",
  },
}));

const AddExtensionModal = () => {
  const classes = useStyles();
  const { requestId, ministryId } = useParams();

  const costumFormat = useMemo(() => {
    return {
      container: classes.fileUploadContainer,
      preview: classes.fileUploadPreview,
    };
  });

  const {
    saveModalOpen,
    setSaveModalOpen,
    extensionReasons,
    dispatch,
    startDate,
    currentDueDate,
    originalDueDate,
    idNumber,
    selectedExtension,
    extensionLoading,
    setExtensionLoading,
    saveExtensionRequest,
    extensions,
  } = useContext(ActionContext);

  const filteredExtensionReasons = filterExtensionReason(
    extensionReasons,
    extensions,
    selectedExtension
  );

  const [reason, setReason] = useState("");
  const publicBodySelected = reason?.extensiontype === "Public Body";

  const [numberDays, setNumberDays] = useState("");
  let maxExtendDays =
    getMaxExtendDays(
      getPublicBodyTotalExtendedDays(extensions),
      reason?.defaultextendedduedays,
      publicBodySelected,
      getSelectedDays(
        selectedExtension?.extensiontype,
        selectedExtension?.extendedduedays
      )
    ) || 999;
  const [extendedDate, setExtendedDate] = useState("");
  const [preExtendedDate, setPreExtendedDate] = useState("");
  const [status, setStatus] = useState(extensionStatusId.pending);

  const [approvedDate, setApprovedDate] = useState(formatDate(new Date()));
  const [approvedNumberDays, setApprovedNumberDays] = useState("");

  const [deniedDate, setDeniedDate] = useState(formatDate(new Date()));

  const existingFiles = selectedExtension?.documents || [];
  const [newFiles, setNewFiles] = useState([]);
  const attchmentFileNameList = existingFiles.map((file) => file.filename);

  const updateFilesCb = (_files) => {
    setNewFiles(_files);
  };

  const [saveLoading, setSaveLoading] = useState(false);

  useEffect(() => {
    if (selectedExtension && extensionReasons) {
      const existingReason = extensionReasons.find(
        (ex) => ex.extensionreasonid === selectedExtension.extensionreasonid
      );
      setReason(existingReason);
      setNumberDays(selectedExtension.extendedduedays);
      setExtendedDate(formatDate(selectedExtension.extendedduedate));
      setStatus(selectedExtension.extensionstatusid);
      setNewFiles(selectedExtension.documents || []);
      setApprovedDate(
        formatDate(selectedExtension.approveddate) || formatDate(new Date())
      );
      setApprovedNumberDays(
        selectedExtension.approvednoofdays || selectedExtension.extendedduedays
      );

      const daysToSubtract =
        selectedExtension.approvednoofdays || selectedExtension.extendedduedays;
      setPreExtendedDate(
        removeBusinessDays(
          formatDate(selectedExtension.extendedduedate),
          daysToSubtract
        )
      );

      setDeniedDate(
        formatDate(selectedExtension.denieddate) || formatDate(new Date())
      );
    }
    setExtensionLoading(false);
  }, [selectedExtension, extensionReasons]);

  const handleReasonChange = (e) => {
    const extensionReason = filteredExtensionReasons.find(
      (er) => er.extensionreasonid === e.target.value
    );

    const isPublicBody = extensionReason?.extensiontype === "Public Body";
    let days = extensionReason.defaultextendedduedays;
    const maxDays =
      getMaxExtendDays(
        getPublicBodyTotalExtendedDays(extensions),
        extensionReason.defaultextendedduedays,
        isPublicBody,
        getSelectedDays(
          selectedExtension?.extensiontype,
          selectedExtension?.extendedduedays
        )
      ) || days;
    maxExtendDays = isPublicBody ? maxDays : maxExtendDays;
    setReason(extensionReason);
    if (isPublicBody) days = maxDays;
    if (days) {
      updateExtendedDate(days);
    }
  };

  const handleNumberDaysChange = (e) => {
    const numDays = Number(e.target.value);
    updateExtendedDate(numDays);
  };

  const getCurrentDueDate = () => {
    if (!selectedExtension || !preExtendedDate) {
      return currentDueDate;
    }

    return preExtendedDate;
  };

  const handleApprovedNumberDaysChange = (e) => {
    const dueDate = getCurrentDueDate();

    const days = Number(e.target.value);

    if (days > numberDays) {
      return;
    }

    setApprovedNumberDays(days);
    setExtendedDate(addBusinessDays(dueDate, days));
  };

  const updateExtendedDate = (days) => {
    const dueDate = getCurrentDueDate();
    if (days > maxExtendDays) {
      return;
    }

    setNumberDays(days);
    setApprovedNumberDays(days);
    setExtendedDate(addBusinessDays(dueDate, days));
  };

  const handleClose = () => {
    setSaveModalOpen(false);
  };

  const handleFileChanges = async () => {
    if (publicBodySelected) {
      return [];
    }

    const existingFilesNameSet = new Set(
      existingFiles.map((EF) => EF.filename)
    );

    const filesToUpload = newFiles.filter(
      (NF) => !existingFilesNameSet.has(NF.filename)
    );

    const filesToKeep = newFiles.filter((NF) =>
      existingFilesNameSet.has(NF.filename)
    );

    if (filesToUpload.length < 1) {
      return [...filesToKeep];
    }

    const uploadedFiles = await uploadFiles(
      filesToUpload,
      idNumber,
      dispatch,
      extensionStatusLabel[status]
    );
    return [...uploadedFiles, ...filesToKeep];
  };

  const getStatusOptions = async () => {
    const documents = await handleFileChanges();

    const allOptions = {
      [extensionStatusId.pending]: {},
      [extensionStatusId.approved]: {
        approveddate: approvedDate,
        approvednoofdays: approvedNumberDays,
        extensionstatusid: status,
        documents,
      },
      [extensionStatusId.denied]: {
        denieddate: deniedDate,
        documents,
      },
    };

    return allOptions[status] || {};
  };

  const handleSave = async () => {
    try {
      setSaveLoading(true);

      const statusOptions = await getStatusOptions();
      const extensionRequest = {
        extensionreasonid: reason.extensionreasonid,
        extendedduedays: numberDays,
        extendedduedate: formatDate(extendedDate, "yyyy-MM-dd"),
        extensionstatusid: status,
        ...statusOptions,
      };

      saveExtensionRequest({
        data: extensionRequest,
        callback: (data) => {
          fetchExtensions({
            ministryId: ministryId,
            errorCallback: () => {
              errorToast("Error occurred while refreshing extensions.");
            },
            dispatch,
          });
          dispatch(fetchFOIRequestNotesList(requestId, ministryId));
          dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));

          setSaveModalOpen(false);
          setSaveLoading(false);
          if (data.newduedate) {
            dispatch(
              setRequestDueDate(formatDate(data.newduedate, "yyyy-MM-dd"))
            );
          }
        },
        errorCallback: (errorMessage) => {
          setSaveLoading(false);
          errorToast(errorMessage);
        },
      });
    } catch (error) {
      errorToast(
        error.message || "Error occured while saving extension details"
      );
    }
  };

  const errorExists = Object.values({
    reason: !reason,
    numberDays: checkPublicBodyError(numberDays, publicBodySelected),
    approvedDate:
      status === extensionStatusId.approved &&
      !publicBodySelected &&
      !approvedDate,
    approvedNumberDays:
      status === extensionStatusId.approved &&
      !publicBodySelected &&
      !approvedNumberDays,
    deniedDate:
      status === extensionStatusId.denied && !publicBodySelected && !deniedDate,
  }).some((isErrorTrue) => isErrorTrue);

  const getExtensionReasonMenueItems = () => {
    const reasons = filteredExtensionReasons.map((extensionReason) => {
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
    return reasons;
  };

  const showStatusOptions = reason && !publicBodySelected;

  return (
    <>
      <Dialog
        open={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        aria-labelledby="extension-dialog-title"
        maxWidth={"md"}
        fullWidth={true}
        id="add-extension-dialog"
        TransitionProps={{
          onExited: () => {
            setNumberDays("");
            setReason("");
            setExtendedDate("");
            setNewFiles([]);
            setApprovedDate(formatDate(new Date()));
            setDeniedDate(formatDate(new Date()));
            setApprovedNumberDays("");
            setPreExtendedDate("");
            setStatus(extensionStatusId.pending);
          },
        }}
      >
        <DialogTitle disableTypography id="extension-dialog-title">
          <h2 className="extension-header">Extension</h2>
          <IconButton
            aria-label= "close"
            className="title-col3"
            onClick={() => setSaveModalOpen(false)}
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
          <ConditionalComponent condition={!extensionLoading}>
            <Grid
              container
              direction="row"
              justifyContent="flex-start"
              alignItems="flex-start"
              className={classes.gridContainer}
              spacing={3}
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
                  id="extension-reasons"
                  name="reason"
                  variant="outlined"
                  required
                  select
                  label="Reason for Extension"
                  inputProps={{ "aria-labelledby": "extension-reasons-label"}}
                  value={reason?.extensionreasonid || 0}
                  onChange={handleReasonChange}
                  error={!reason}
                  fullWidth
                >
                  {filteredExtensionReasons && getExtensionReasonMenueItems()}
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
                  error={checkPublicBodyError(numberDays, publicBodySelected)}
                />
              </Grid>

              <Grid item xs={6}>
                <TextField
                  id="extended-due-date"
                  label="Extended Due Date"
                  type="date"
                  value={extendedDate}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  InputProps={{
                    readOnly: true,
                  }}
                  variant="outlined"
                  fullWidth
                />
              </Grid>

              <ConditionalComponent condition={showStatusOptions}>
                <Grid item xs={12} lg={6}>
                  <FormControl component="fieldset">
                    <RadioGroup
                      id="status-options"
                      row
                      name="controlled-radio-buttons-group"
                      value={status}
                      onChange={(e) => {
                        setStatus(Number(e.target.value));
                      }}
                    >
                      <FormControlLabel
                        value={extensionStatusId.pending}
                        control={<Radio color="default" />}
                        label="Pending"
                      />
                      <FormControlLabel
                        value={extensionStatusId.approved}
                        control={<Radio color="default" />}
                        label="Approved"
                      />
                      <FormControlLabel
                        value={extensionStatusId.denied}
                        control={<Radio color="default" />}
                        label="Denied"
                      />
                    </RadioGroup>
                  </FormControl>
                </Grid>
                <ConditionalComponent
                  condition={status === extensionStatusId.approved}
                >
                  <Grid item xs={6} />
                  <Grid item xs={6}>
                    <TextField
                      id="approvedDate"
                      label="Approved Date"
                      type="date"
                      value={approvedDate || ""}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      onChange={(e) => {
                        setApprovedDate(e.target.value);
                      }}
                      InputProps={{
                        inputProps: { max: formatDate(new Date()) , "aria-labelledby": "approvedDate-label"},
                      }}
                      variant="outlined"
                      fullWidth
                      error={!approvedDate}
                    />
                  </Grid>

                  <Grid item xs={6}>
                    <TextField
                      id="outlined-approved-number-days"
                      name="approvedNumberDays"
                      value={approvedNumberDays || 0}
                      type="number"
                      variant="outlined"
                      required
                      label="Approved Number of Days"
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">Days</InputAdornment>
                        ),
                        inputProps: { min: 1, max: numberDays },
                      }}
                      onChange={handleApprovedNumberDaysChange}
                      fullWidth
                      error={!approvedNumberDays}
                    />
                  </Grid>
                </ConditionalComponent>
                <ConditionalComponent
                  condition={status === extensionStatusId.denied}
                >
                  <Grid item xs={6}>
                    <TextField
                      id="deniedDate"
                      label="Denied Date"
                      type="date"
                      InputLabelProps={{
                        shrink: true,
                      }}
                      value={deniedDate}
                      onChange={(e) => {
                        setDeniedDate(e.target.value);
                      }}
                      InputProps={{
                        inputProps: { max: formatDate(new Date()) , "aria-labelledby": "deniedDate-label"},
                      }}
                      variant="outlined"
                      fullWidth
                      error={!deniedDate}
                    />
                  </Grid>
                </ConditionalComponent>
                <ConditionalComponent
                  condition={status !== extensionStatusId.pending}
                >
                  <Grid item xs={12}>
                    <FileUpload
                      className={classes.fullWidth}
                      attchmentFileNameList={attchmentFileNameList}
                      multipleFiles={false}
                      mimeTypes={MimeTypeList.extensionAttachment}
                      maxFileSize={MaxFileSizeInMB.extensionAttachment}
                      updateFilesCb={updateFilesCb}
                      customFormat={costumFormat}
                      existingDocuments={existingFiles}
                    />
                  </Grid>
                </ConditionalComponent>
              </ConditionalComponent>
            </Grid>
          </ConditionalComponent>
          <ConditionalComponent condition={extensionLoading}>
            <Grid
              container
              direction="row"
              justifyContent="center"
              alignItems="center"
              className={classes.gridContainer}
              spacing={2}
            >
              <Grid item xs={12}>
                <CircularProgress />
              </Grid>
            </Grid>
          </ConditionalComponent>
        </DialogContent>

        <DialogActions className="dialog-content-nomargin">
          <Grid
            container
            direction="row"
            justifyContent="flex-start"
            alignItems="flex-start"
            className={classes.gridContainer}
            spacing={2}
          >
            <Grid item xs={6}>
              <button
                style={{ width: "100%" }}
                className={clsx("btn-save", {
                  [classes.btnenabled]: !(saveLoading || errorExists),
                  [classes.btndisabled]: saveLoading || errorExists,
                })}
                disabled={saveLoading || errorExists}
                onClick={handleSave}
              >
                {saveLoading ? <CircularProgress size="2em" /> : "Save"}
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
    </>
  );
};

export default AddExtensionModal;
