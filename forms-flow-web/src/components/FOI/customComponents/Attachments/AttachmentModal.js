import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import TextField from "@material-ui/core/TextField";
import "../ConfirmationModal/confirmationmodal.scss";
import "./attachmentmodal.scss";
import FileUpload from "../FileUpload";
import FileUploadForMCFPersonal from "../FileUpload/FileUploadForMCFPersonal";
import FileUploadForMSDPersonal from "../FileUpload/FileUploadForMSDPersonal";
import { makeStyles } from "@material-ui/core/styles";
import {
  MimeTypeList,
  MaxFileSizeInMB,
  MCFPopularSections,
  MSDPopularSections,
  MinistryNeedsScanning,
} from "../../../../constants/FOI/enum";
import {
  StateTransitionCategories,
  AttachmentCategories,
} from "../../../../constants/FOI/statusEnum";
import { TOTAL_RECORDS_UPLOAD_LIMIT } from "../../../../constants/constants";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import { ClickableChip } from "../../Dashboard/utils";

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
}));

export default function AttachmentModal({
  modalFor,
  openModal,
  handleModal,
  multipleFiles,
  requestNumber,
  requestId,
  attachment,
  attachmentsArray,
  handleRename,
  handleReclassify,
  isMinistryCoordinator,
  uploadFor = "attachment",
  maxNoFiles,
  bcgovcode,
  existingDocuments = [],
  divisions = [],
  replacementfiletypes = [],
  totalUploadedRecordSize = 0,
  requestType = FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL,
  isScanningTeamMember = false
}) {
  let tagList = [];
  if (uploadFor === "attachment") {
    tagList = AttachmentCategories.categorys.filter((category) =>
      category.type.includes("tag")
    );
    if (isMinistryCoordinator) {
      tagList = tagList.filter((tag) => tag.name !== "applicant");
    }
  } else if (uploadFor === "record") {
    tagList = divisions.map((division) => {
      return {
        name: division.divisionid,
        display: division.divisionname,
      };
    });
  }

  const recordFormats = useSelector((state) => state.foiRequests.recordFormats);
  useEffect(() => {
    setMimeTypes(
      multipleFiles
        ? uploadFor === "attachment"
          ? [...recordFormats, ...MimeTypeList.additional]
          : uploadFor === "record" &&
            (modalFor === "replace" || modalFor === "replaceattachment")
          ? replacementfiletypes
          : recordFormats
        : MimeTypeList.stateTransition
    );
  }, [recordFormats]);
  const [mimeTypes, setMimeTypes] = useState(
    multipleFiles
      ? uploadFor === "attachment"
        ? [...recordFormats, ...MimeTypeList.additional]
        : uploadFor === "record" &&
          (modalFor === "replace" || modalFor === "replaceattachment")
        ? replacementfiletypes
        : recordFormats
      : MimeTypeList.stateTransition
  );
  const maxFileSize =
    uploadFor === "record"
      ? MaxFileSizeInMB.totalFileSize
      : multipleFiles
      ? MaxFileSizeInMB.attachmentLog
      : MaxFileSizeInMB.stateTransition;
  const totalFileSize = multipleFiles
    ? MaxFileSizeInMB.totalFileSize
    : MaxFileSizeInMB.stateTransition;
  const classes = useStyles();
  const [files, setFiles] = useState([]);
  const [newFilename, setNewFilename] = useState("");
  const [extension, setExtension] = useState("");
  const [errorMessage, setErrorMessage] = useState();
  const [tagValue, setTagValue] = useState(
    uploadFor === "record" ? "" : "general"
  );
  const [person, setPerson] = useState({});
  const [volume, setVolume] = useState({});
  const [fileType, setFileType] = useState({});
  const [trackingID, setTrackingID] = useState("");
  const attchmentFileNameList = attachmentsArray.map((_file) =>
    _file.filename.toLowerCase()
  );
  const totalRecordUploadLimit = TOTAL_RECORDS_UPLOAD_LIMIT;
  const [isMCFMSDPersonal, setIsMCFMSDPersonal] = useState(
    MinistryNeedsScanning.includes(bcgovcode) &&
      requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL
  );

  useEffect(() => {
    parseFileName(attachment);
  }, [attachment]);

  useEffect(() => {
    setIsMCFMSDPersonal(
      MinistryNeedsScanning.includes(bcgovcode) &&
        requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL
    );
  }, [bcgovcode, requestType]);

  const parseFileName = (_attachment) => {
    setNewFilename("");
    setExtension("");
    setErrorMessage("");
    if (_attachment && _attachment.filename) {
      let lastIndex = _attachment.filename.lastIndexOf(".");
      setNewFilename(
        lastIndex > 0
          ? _attachment.filename.substr(0, lastIndex)
          : _attachment.filename
      );
      setExtension(
        lastIndex > 0 ? _attachment.filename.substr(lastIndex + 1) : ""
      );
    }
  };

  const checkInvalidCharacters = (fname) => {
    let rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
    return !fname || rg1.test(fname);
  };

  const validateFilename = (fname) => {
    let rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
    let rg2 = /^\./; // cannot start with dot (.)
    //let rg3 = /^(nul|prn|con|lpt\d|com\d)(.|$)/i; // forbidden file names

    return fname && rg1.test(fname) && !rg2.test(fname);
  };

  const containDuplicate = (fname) => {
    if (attachment.filename !== fname + "." + extension) {
      return attchmentFileNameList.includes(
        (fname + "." + extension).toLocaleLowerCase()
      );
    } else {
      return false;
    }
  };

  const updateFilename = (e) => {
    if (checkInvalidCharacters(e.target.value)) {
      setNewFilename(e.target.value);
      setErrorMessage("");
    } else {
      setErrorMessage(
        `File name cannot contain these characters, / : * ? " < > |`
      );
    }
  };

  const saveNewCategory = () => {
    handleReclassify(attachment, tagValue);
  };

  useEffect(() => {
    if (attachment && attachment.category && modalFor == "reclassify") {
      setTagValue(attachment.category?.toLowerCase());
    }
  }, [modalFor, attachment]);

  const saveNewFilename = () => {
    if (validateFilename(newFilename)) {
      if (!containDuplicate(newFilename)) {
        setErrorMessage("");
        handleRename(attachment, newFilename + "." + extension);
      } else {
        setErrorMessage(
          `File name "${newFilename}.${extension}" already exists`
        );
      }
    } else {
      setErrorMessage(
        `File name cannot be empty and cannot contain these characters, / : * ? " < > |`
      );
    }
  };

  const updateFilesCb = (_files, _errorMessage) => {
    setFiles(_files);
  };
  const handleClose = () => {
    if (
      (files.length > 0 && files !== existingDocuments) ||
      (modalFor === "rename" &&
        attachment.filename !== newFilename + "." + extension)
    ) {
      if (
        window.confirm(
          "Are you sure you want to leave? Your changes will be lost."
        )
      ) {
        setFiles([]);
        handleModal(false);
        parseFileName(attachment);
      }
    } else {
      handleModal(false);
      parseFileName(attachment);
    }
    if (uploadFor === "record") setTagValue("");
  };

  const handleTagChange = (_tagValue) => {
    setTagValue(_tagValue);
  };

  const handlePersonChange = (_tagValue) => {
    setPerson(_tagValue);
  };

  const handleVolumeChange = (_tagValue) => {
    setVolume(_tagValue);
  };

  const handleFileTypeChange = (_tagValue) => {
    setFileType(_tagValue);
  };

  const handleTrackingIDChange = (_tagValue) => {
    setTrackingID(_tagValue);
  };

  const handleSave = () => {
    if (modalFor.toLowerCase() === "delete") {
      handleModal(true, null, null);
    } else {
      let fileInfoList = [];

      let fileStatusTransition = "";
      let personalAttributes = {};
      if (modalFor === "replace" || modalFor === "replaceattachment") {
        fileStatusTransition = attachment?.category;
      } else if (uploadFor === "record") {
        if (
          bcgovcode == "MCF" &&
          requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL
        ) {
          fileStatusTransition =
            divisions.find((division) => division.divisionid === tagValue)
              ?.divisionname ||
            MCFSections?.sections?.find(
              (division) => division.divisionid === tagValue
            )?.name;
          personalAttributes = {
            person: person.name,
            filetype: fileType.name,
            volume: volume.name,
            trackingid: trackingID
          }
        } else if (
          bcgovcode == "MSD" &&
          requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL
        ) {
          fileStatusTransition = MSDSections?.sections?.find(
            (division) => division.divisionid === tagValue
          ).name;
        } else {
          fileStatusTransition = divisions.find(
            (division) => division.divisionid === tagValue
          ).divisionname;
        }
      } else {
        fileStatusTransition = tagValue;
      }
      fileInfoList = files?.map((file) => {
        return {
          ministrycode: uploadFor === "record" ? bcgovcode : "Misc",
          requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
          filestatustransition: fileStatusTransition,
          filename: file.filename ? file.filename : file.name,
          filesize: file.size,
          personalattributes: personalAttributes,
          ...(uploadFor === "record" && { divisionid: tagValue }),
        };
      });

      handleModal(true, fileInfoList, files);
      setFiles([]);
      if (uploadFor === "record") setTagValue("");
    }
  };
  const getMessage = () => {
    let _message = {};
    switch (modalFor.toLowerCase()) {
      case "add":
        if (isMCFMSDPersonal && !isMinistryCoordinator) {
          return { title: "Add Scanned Records", body: "" };
        } else {
          return { title: "Add Attachment", body: "" };
        }
      case "replaceattachment":
        if (uploadFor === "record") {
          _message = {
            title: "Replace Records",
            body: (
              <>
                Replace the existing record with a reformatted or updated
                version of the same record.<br></br>If the file being replaced
                is also a pdf file, the replaced file will no longer be available.
              </>
            ),
          };
        }
        return _message;
      case "replace":
        if (uploadFor === "record") {
          _message = {
            title: "Replace Records",
            body: (
              <>
                Replace the existing record with a reformatted or updated
                version of the same record.<br></br>The original file that was
                uploaded will still be available for download.
              </>
            ),
          };
        } else if (attachment) {
          switch (attachment.category.toLowerCase()) {
            case StateTransitionCategories.cfrreview.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>{StateTransitionCategories.cfrreview.fromState}</b> to{" "}
                    <b>{StateTransitionCategories.cfrreview.toState}</b>.
                  </>
                ),
              };
              break;
            case StateTransitionCategories.cfrfeeassessed.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>
                      {" "}
                      {StateTransitionCategories.cfrfeeassessed.fromState}{" "}
                    </b>{" "}
                    to{" "}
                    <b> {StateTransitionCategories.cfrfeeassessed.toState} </b>.
                  </>
                ),
              };
              break;
            case StateTransitionCategories.signoffresponse.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>{StateTransitionCategories.signoffresponse.fromState}</b>{" "}
                    to{" "}
                    <b>{StateTransitionCategories.signoffresponse.toState}</b>.
                  </>
                ),
              };
              break;
            case StateTransitionCategories.harmsreview.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>{StateTransitionCategories.harmsreview.fromState}</b> to{" "}
                    <b>{StateTransitionCategories.harmsreview.toState}</b>.
                  </>
                ),
              };
              break;
            case StateTransitionCategories.responsereview.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>{StateTransitionCategories.responsereview.fromState}</b>{" "}
                    to <b>{StateTransitionCategories.responsereview.toState}</b>
                    .
                  </>
                ),
              };
              break;
            case StateTransitionCategories.signoffreview.name:
              _message = {
                title: "Replace Attachment",
                body: (
                  <>
                    This attachment must be replaced as it was uploaded during
                    the state change. Please replace attachment with document
                    from Request #{requestNumber} changing from{" "}
                    <b>{StateTransitionCategories.signoffreview.fromState}</b>{" "}
                    to <b>{StateTransitionCategories.signoffreview.toState}</b>.
                  </>
                ),
              };
              break;
            default:
              _message = {
                title: "Replace Attachment",
                body: `This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #${requestNumber}`,
              };
              break;
          }
        }
        return _message;
      case "rename":
        return { title: "Rename Attachment", body: "" };
      case "reclassify":
        return { title: "Reclassify Attachment", body: "" };
      case "delete":
        if (uploadFor === "record") {
          return {
            title: "Delete Record",
            body: (
              <>
                Are you sure you want to delete this record?<br></br>
                <i>
                  If you delete this record, the record will not appear in the
                  redaction app for review by IAO.
                </i>
              </>
            ),
          };
        } else {
          return {
            title: "Delete Attachment",
            body: "Are you sure you want to delete the attachment?",
          };
        }
      default:
        return { title: "", body: "" };
    }
  };
  let message = getMessage();

  const isSaveDisabled = () => {
    if (modalFor === "delete") {
      return false;
    } else if (files.length === 0 && existingDocuments.length === 0) {
      return true;
    } else if (modalFor === "add") {
      return tagValue === "";
    } else if (modalFor === "replace" || modalFor === "replaceattachment") {
      return false;
    }
  };

  const MCFSections = useSelector(
    (state) => state.foiRequests.foiPersonalSections
  );
  const MSDSections = useSelector(
    (state) => state.foiRequests.foiPersonalDivisionsAndSections
  );

  return (
    <div className="state-change-dialog">
      <Dialog
        open={openModal}
        onClose={handleClose}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="state-change-dialog-description"
        maxWidth={"md"}
        fullWidth={true}
      >
        <DialogTitle
          disableTypography
          id="state-change-dialog-title"
          className="add-attachment-modal-title"
        >
          <h2 className="state-change-header">{message.title}</h2>
          <IconButton aria-label="close" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <DialogContentText
            id="state-change-dialog-description"
            component={"span"}
          >
            <div className="attachment-modal-message">
              <span className="confirmation-message">{message.body}</span>
            </div>
            {modalFor === "reclassify" && (
              <div>
                <div className="tagtitle">
                  <span>
                    Select the tag that you would like to reclassify this
                    document with
                  </span>
                </div>
                <div className="taglist">
                  {tagList.map((tag) => (
                    <ClickableChip
                      id={`${tag.name}Tag`}
                      key={`${tag.name}-tag`}
                      label={tag.display.toUpperCase()}
                      sx={{
                        width: "fit-content",
                        marginRight: "8px",
                        marginBottom: "8px",
                      }}
                      color="primary"
                      size="small"
                      onClick={() => {
                        handleTagChange(tag.name);
                      }}
                      clicked={tagValue == tag.name}
                    />
                  ))}
                </div>
              </div>
            )}
            {["replaceattachment", "replace", "add"].includes(modalFor) ? (
              requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ? (
                bcgovcode == "MCF" ? (
                  <FileUploadForMCFPersonal
                    attachment={attachment}
                    attchmentFileNameList={attchmentFileNameList}
                    multipleFiles={multipleFiles}
                    mimeTypes={
                      modalFor === "replaceattachment"
                        ? ["application/pdf", ".pdf"]
                        : mimeTypes
                    }
                    maxFileSize={maxFileSize}
                    totalFileSize={totalFileSize}
                    updateFilesCb={updateFilesCb}
                    modalFor={modalFor}
                    uploadFor={uploadFor}
                    divisions={tagList}
                    tagList={MCFSections?.sections?.slice(
                      0,
                      MCFPopularSections - 1
                    )}
                    otherTagList={MCFSections?.sections?.slice(
                      MCFPopularSections
                    )}
                    handleTagChange={handleTagChange}
                    tagValue={tagValue}
                    handlePersonChange={handlePersonChange}
                    person={person}
                    handleVolumeChange={handleVolumeChange}
                    volume={volume}
                    handleFileTypeChange={handleFileTypeChange}
                    fileType={fileType}
                    handleTrackingIDChange={handleTrackingIDChange}
                    trackingID={trackingID}
                    maxNumberOfFiles={maxNoFiles}
                    isMinistryCoordinator={isMinistryCoordinator}
                    existingDocuments={existingDocuments}
                    totalUploadedRecordSize={totalUploadedRecordSize}
                    totalRecordUploadLimit={totalRecordUploadLimit}
                    isScanningTeamMember={isScanningTeamMember}
                  />
                ) : bcgovcode == "MSD" && MSDSections?.divisions?.length > 0 ? (
                  <FileUploadForMSDPersonal
                    attachment={attachment}
                    attchmentFileNameList={attchmentFileNameList}
                    multipleFiles={multipleFiles}
                    mimeTypes={
                      modalFor === "replaceattachment"
                        ? ["application/pdf", ".pdf"]
                        : mimeTypes
                    }
                    maxFileSize={maxFileSize}
                    totalFileSize={totalFileSize}
                    updateFilesCb={updateFilesCb}
                    modalFor={modalFor}
                    uploadFor={uploadFor}
                    divisions={tagList}
                    tagList={MSDSections?.divisions[0]?.sections?.slice(
                      0,
                      MSDPopularSections - 1
                    )}
                    otherTagList={MSDSections?.divisions[0]?.sections?.slice(
                      MSDPopularSections
                    )}
                    handleTagChange={handleTagChange}
                    tagValue={tagValue}
                    maxNumberOfFiles={maxNoFiles}
                    isMinistryCoordinator={isMinistryCoordinator}
                    existingDocuments={existingDocuments}
                    totalUploadedRecordSize={totalUploadedRecordSize}
                    totalRecordUploadLimit={totalRecordUploadLimit}
                  />
                ) : (
                  <FileUpload
                    attachment={attachment}
                    attchmentFileNameList={attchmentFileNameList}
                    multipleFiles={multipleFiles}
                    mimeTypes={
                      modalFor === "replaceattachment"
                        ? ["application/pdf", ".pdf"]
                        : mimeTypes
                    }
                    maxFileSize={maxFileSize}
                    totalFileSize={totalFileSize}
                    updateFilesCb={updateFilesCb}
                    modalFor={modalFor}
                    uploadFor={uploadFor}
                    tagList={tagList}
                    handleTagChange={handleTagChange}
                    tagValue={tagValue}
                    maxNumberOfFiles={maxNoFiles}
                    isMinistryCoordinator={isMinistryCoordinator}
                    existingDocuments={existingDocuments}
                    totalUploadedRecordSize={totalUploadedRecordSize}
                    totalRecordUploadLimit={totalRecordUploadLimit}
                  />
                )
              ) : (
                <FileUpload
                  attachment={attachment}
                  attchmentFileNameList={attchmentFileNameList}
                  multipleFiles={multipleFiles}
                  mimeTypes={
                    modalFor === "replaceattachment"
                      ? ["application/pdf", ".pdf"]
                      : mimeTypes
                  }
                  maxFileSize={maxFileSize}
                  totalFileSize={totalFileSize}
                  updateFilesCb={updateFilesCb}
                  modalFor={modalFor}
                  uploadFor={uploadFor}
                  tagList={tagList}
                  handleTagChange={handleTagChange}
                  tagValue={tagValue}
                  maxNumberOfFiles={maxNoFiles}
                  isMinistryCoordinator={isMinistryCoordinator}
                  existingDocuments={existingDocuments}
                  totalUploadedRecordSize={totalUploadedRecordSize}
                  totalRecordUploadLimit={totalRecordUploadLimit}
                />
              )
            ) : (
              <ModalForRename
                modalFor={modalFor}
                newFilename={newFilename}
                updateFilename={updateFilename}
                errorMessage={errorMessage}
                extension={extension}
              />
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          {modalFor === "reclassify" && (
            <button
              className={`btn-bottom btn-save ${classes.btnenabled}`}
              onClick={saveNewCategory}
            >
              Reclassify
            </button>
          )}
          {modalFor === "rename" && (
            <button
              className={`btn-bottom btn-save ${classes.btnenabled}`}
              onClick={saveNewFilename}
            >
              Save
            </button>
          )}
          {modalFor !== "rename" && modalFor !== "reclassify" && (
            <button
              className={`btn-bottom btn-save ${
                isSaveDisabled() ? classes.btndisabled : classes.btnenabled
              }`}
              disabled={isSaveDisabled()}
              onClick={handleSave}
            >
              {uploadFor === "email" ? "Save Changes" : "Continue"}
            </button>
          )}
          <button className="btn-bottom btn-cancel" onClick={handleClose}>
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

const ModalForRename = ({
  modalFor,
  newFilename,
  updateFilename,
  errorMessage,
  extension,
}) => {
  return modalFor === "rename" ? (
    <div className="row">
      <div className="col-sm-1"></div>
      <div className="col-sm-9">
        <TextField
          id="renameAttachment"
          label="Rename Attachment"
          inputProps={{ "aria-labelledby": "renameAttachment-label" }}
          InputLabelProps={{ shrink: true }}
          variant="outlined"
          fullWidth
          value={newFilename}
          onChange={updateFilename}
          error={errorMessage !== undefined && errorMessage !== ""}
          helperText={errorMessage}
        />
      </div>
      <div className="col-sm-1 extension-name">.{extension}</div>
      <div className="col-sm-1"></div>
    </div>
  ) : null;
};
