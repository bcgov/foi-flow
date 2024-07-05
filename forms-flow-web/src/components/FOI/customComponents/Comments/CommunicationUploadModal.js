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
  setFiles,
  saveResponse
}) {

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

  const [responsefiles, setResponseFiles] = useState([]);

  const updateFilesCb = (_files, _errorMessage) => {
    setResponseFiles(_files);
  };

  const isSaveDisabled = () => {
    if (responsefiles.length > 0) return false;
    return true;
  };


  const handleSave = () => {
    setFiles(responsefiles);
    saveResponse();
    setOpenModal(false);
  };

  const handleClose = (e) => {
    if (e.stopPropagation) e.stopPropagation();
    setOpenModal(false);
    setResponseFiles([]);
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
            className="btn-cancel"
            onClick={(e) => handleClose(e)}
          >
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
