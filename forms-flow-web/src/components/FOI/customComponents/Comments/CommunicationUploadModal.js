import { useState } from "react";
import { useDispatch } from "react-redux";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import "../ConfirmationModal/confirmationmodal.scss";
import "./communicationuploadmodal.scss";
import FileUpload from "../FileUpload";
import { makeStyles } from "@material-ui/core/styles";
import {
  completeMultiPartUpload,
  postFOIS3DocumentPreSignedUrl,
  saveFilesinS3,
} from "../../../../apiManager/services/FOI/foiOSSServices";
import { toast } from "react-toastify";
import { readUploadedFileAsBytes } from "../../../../helper/FOI/helper";
import { saveFOIRequestAttachmentsList } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { OSS_S3_CHUNK_SIZE } from "../../../../constants/constants";
import { useParams } from "react-router-dom";

export default function CommunicationUploadModal({
  openModal,
  setOpenModal,
  message,
//   bcgovcode,
//   requestNumber
}) {
  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  //THIS NEEDS TO BE PASSED IN
  let bcgovcode = 1;
  let requestNumber = 1;

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
  const classes = useStyles();

  const [files, setFiles] = useState([]);

  const updateFilesCb = (_files, _errorMessage) => {
    setFiles(_files);
  };

  const isSaveDisabled = () => {
    if (files.length > 0) return false;
    return true;
  };

  const saveDocument = (value, fileInfoList, files) => {
    if (value) {
      if (files.length !== 0) {
        // setAttachmentLoading(true);
        postFOIS3DocumentPreSignedUrl(
          ministryId,
          fileInfoList.map((file) => ({ ...file, multipart: true })),
          "attachments",
          bcgovcode,
          dispatch,
          async (err, res) => {
            let _documents = [];
            if (!err) {
              let completed = 0;
              let failed = [];
              const toastID = toast.loading(
                "Uploading files (" +
                  completed +
                  "/" +
                  fileInfoList.length +
                  ")"
              );
              for (let header of res) {
                const _file = files.find(
                  (file) => file.filename === header.filename
                );
                const _fileInfo = fileInfoList.find(
                  (fileInfo) => fileInfo.filename === header.filename
                );
                const documentDetails = {
                  documentpath: header.filepathdb,
                  filename: header.filename,
                  category: _fileInfo.filestatustransition,
                };
                let bytes = await readUploadedFileAsBytes(_file);
                const CHUNK_SIZE = OSS_S3_CHUNK_SIZE;
                const totalChunks = Math.ceil(bytes.byteLength / CHUNK_SIZE);
                let parts = [];
                for (let chunk = 0; chunk < totalChunks; chunk++) {
                  let CHUNK = bytes.slice(
                    chunk * CHUNK_SIZE,
                    (chunk + 1) * CHUNK_SIZE
                  );
                  let response = await saveFilesinS3(
                    { filepath: header.filepaths[chunk] },
                    CHUNK,
                    dispatch,
                    (_err, _res) => {
                      if (_err) {
                        failed.push(header.filename);
                      }
                    }
                  );
                  if (response.status === 200) {
                    parts.push({
                      PartNumber: chunk + 1,
                      ETag: response.headers.etag,
                    });
                  } else {
                    failed.push(header.filename);
                  }
                }
                await completeMultiPartUpload(
                  {
                    uploadid: header.uploadid,
                    filepath: header.filepathdb,
                    parts: parts,
                  },
                  ministryId,
                  "attachments",
                  bcgovcode,
                  dispatch,
                  (_err, _res) => {
                    if (!_err && _res.ResponseMetadata.HTTPStatusCode === 200) {
                      completed++;
                      toast.update(toastID, {
                        render:
                          "Uploading files (" +
                          completed +
                          "/" +
                          fileInfoList.length +
                          ")",
                        isLoading: true,
                      });
                      _documents.push(documentDetails);
                    } else {
                      failed.push(header.filename);
                    }
                  }
                );
              }
              if (_documents.length > 0) {
                dispatch(
                  saveFOIRequestAttachmentsList(
                    requestId,
                    ministryId,
                    { documents: _documents },
                    (err, _res) => {
                      // dispatchRequestAttachment(err);
                    }
                  )
                );
              }
              var toastOptions = {
                render:
                  failed.length > 0
                    ? "The following " +
                      failed.length +
                      " file uploads failed\n- " +
                      failed.join("\n- ")
                    : fileInfoList.length + " Files successfully saved",
                type: failed.length > 0 ? "error" : "success",
              };
              toast.update(toastID, {
                ...toastOptions,
                className: "file-upload-toast",
                isLoading: false,
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                closeButton: true,
              });
              // setAttachmentLoading(false)
            }
          }
        );
      }
    }
  };

  const handleSave = () => {
    const fileInfoList = files?.map((file) => {
      return {
        ministrycode: "Misc",
        requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
        filestatustransition: "email-reply",
        filename: file.filename ? file.filename : file.name,
        filesize: file.size,
      };
    });
    saveDocument(true, fileInfoList, files);
  };

  const handleClose = (e) => {
    if (e.stopPropagation) e.stopPropagation();
    setOpenModal(false);
    setFiles([]);
  };

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
          <IconButton aria-label="close" onClick={(e) => handleClose(e)}>
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
            <FileUpload
              attachment={{}}
              //   attchmentFileNameList={}
              multipleFiles={true}
              mimeTypes={["application/pdf", ".pdf"]}
              maxFileSize={1000}
              totalFileSize={10000}
              updateFilesCb={updateFilesCb}
              //   modalFor={modalFor}
              //   uploadFor={"reply"}
              //   tagList={["tag", "tag2"]}
              //   handleTagChange={() => {}}
              //   tagValue={""}
              maxNumberOfFiles={10}
              isMinistryCoordinator={false}
              //   existingDocuments={[]}
              totalUploadedRecordSize={1000}
              totalRecordUploadLimit={10000}
            />
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button
            className={`btn-bottom btn-save ${
              isSaveDisabled() ? classes.btndisabled : classes.btnenabled
            }`}
            disabled={isSaveDisabled()}
            onClick={handleSave}
          >
            Continue
          </button>
          <button
            className="btn-bottom btn-cancel"
            onClick={(e) => handleClose(e)}
          >
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
