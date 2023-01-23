import React, { useEffect, useState } from 'react';
import { useSelector } from "react-redux";
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import TextField from '@material-ui/core/TextField';
import '../ConfirmationModal/confirmationmodal.scss';
import './attachmentmodal.scss';
import FileUpload from '../FileUpload';
import { makeStyles } from '@material-ui/core/styles';
import { MimeTypeList, MaxFileSizeInMB } from "../../../../constants/FOI/enum";
import { StateTransitionCategories, AttachmentCategories } from '../../../../constants/FOI/statusEnum';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    marginTop:'30px',
    marginBottom:'50px'
  },
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
  btndisabled: {
    border: 'none',
    backgroundColor: '#eceaea',
    color: '#FFFFFF'
  },
  btnenabled: {
    border: 'none',
    backgroundColor: '#38598A',
    color: '#FFFFFF'
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
  isMinistryCoordinator,
  uploadFor="attachment",
  maxNoFiles,
  bcgovcode,
  existingDocuments=[],
  divisions=[]
}) {

    let tagList = [];
    if(uploadFor === 'attachment') {
      tagList = AttachmentCategories.categorys.filter(category => category.type.includes("tag"));
      if (isMinistryCoordinator) {
        tagList = tagList.filter(tag => tag.name !== "applicant")
      }
    } else if (uploadFor === 'record') {
      tagList = divisions.map(division => {
        return {
          name: division.divisionid,
          display: division.divisionname,
        }
      });
    }

    const mimeTypes = multipleFiles ? MimeTypeList.attachmentLog : MimeTypeList.stateTransition;
    const maxFileSize = uploadFor === 'record' ? MaxFileSizeInMB.totalFileSize : multipleFiles ? MaxFileSizeInMB.attachmentLog : MaxFileSizeInMB.stateTransition;
    const totalFileSize = multipleFiles ? MaxFileSizeInMB.totalFileSize : MaxFileSizeInMB.stateTransition;
    const classes = useStyles();
    const [files, setFiles] = useState([]);
    const [newFilename, setNewFilename] = useState("");
    const [extension, setExtension] = useState("");
    const [errorMessage, setErrorMessage] = useState();
    const [tagValue, setTagValue] = useState(uploadFor === 'record' ? "" : "general");
    const attchmentFileNameList = attachmentsArray.map(_file => _file.filename.toLowerCase());

    useEffect(() => {
      parseFileName(attachment);
    }, [attachment])

    const parseFileName = (_attachment) => {
      setNewFilename("");
      setExtension("");
      setErrorMessage("");
      if(_attachment && _attachment.filename) {
        let lastIndex = _attachment.filename.lastIndexOf(".");
        setNewFilename(lastIndex>0?_attachment.filename.substr(0, lastIndex):_attachment.filename);
        setExtension(lastIndex>0?_attachment.filename.substr(lastIndex+1):"");
      }
    }

    const checkInvalidCharacters = (fname) => {
      let rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
      return !fname || rg1.test(fname);
    };

    const validateFilename = (fname) => {
      let rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
      let rg2 = /^\./; // cannot start with dot (.)
      let rg3 = /^(nul|prn|con|lpt\d|com\d)(.|$)/i; // forbidden file names

      return fname && rg1.test(fname) && !rg2.test(fname) && !rg3.test(fname);
    };

    const containDuplicate = (fname) => {
      if(attachment.filename !== (fname+"."+extension)) {
        return attchmentFileNameList.includes((fname+"."+extension).toLocaleLowerCase());
      } else {
        return false;
      }
    }

    const updateFilename = (e) => {
      if(checkInvalidCharacters(e.target.value)) {
        setNewFilename(e.target.value);
        setErrorMessage("");
      } else {
        setErrorMessage(`File name cannot contain these characters, / : * ? " < > |`);
      }
    };

    const saveNewFilename = () => {
      if(validateFilename(newFilename)) {
        if(!containDuplicate(newFilename)) {
          setErrorMessage("");
          handleRename(attachment, newFilename+"."+extension);
        } else {
          setErrorMessage(`File name "${newFilename}.${extension}" already exists`);
        }
      } else {
        setErrorMessage(`File name cannot be empty and cannot contain these characters, / : * ? " < > |`);
      }
    };

    const updateFilesCb = (_files, _errorMessage) => {
      setFiles(_files);
    }
    const handleClose = () => {
        if ((files.length > 0 && files !== existingDocuments) || (modalFor === 'rename' && attachment.filename !== (newFilename+"."+extension))) {
            if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
                setFiles([]);
                handleModal(false);
                parseFileName(attachment);
            }
        }
        else {
            handleModal(false);
            parseFileName(attachment);
        }
        if (uploadFor === 'record') setTagValue("");
    };

    const handleTagChange = (_tagValue) => {
      setTagValue(_tagValue);
    };

    const handleSave = () => {
      if (modalFor.toLowerCase() === "delete") {
        handleModal(true, null, null);
      }
      else {
        let fileInfoList = [];

        let fileStatusTransition = "";
        if (modalFor === 'replace') {
          fileStatusTransition = attachment?.category;
        } else if (uploadFor === "record") {
          fileStatusTransition = divisions.find(division => division.divisionid === tagValue).divisionname;
        } else {
          fileStatusTransition = tagValue
        }
        fileInfoList = files?.map(file => {
          return {
              ministrycode: uploadFor === "record" ? bcgovcode : "Misc",
              requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
              filestatustransition: fileStatusTransition,
              filename: file.filename? file.filename : file.name,
              ...(uploadFor === "record") && {divisionid: tagValue}
          }
        });
        
        handleModal(true, fileInfoList, files);
        setFiles([]);
        if (uploadFor === 'record') setTagValue("");
      }
    }  
    const getMessage = () => {
      switch(modalFor.toLowerCase()) { 
        case "add":
          return {title: "Add Attachment", body: ""};
        case "replace":
          let _message = {};
            if (uploadFor === 'record') {
              _message = {title: "Replace Records", body:`Replace record with manually converted PDF of the same document. The original file will still be available for download.` }
            } else if (attachment) {
              switch(attachment.category.toLowerCase()) {
                case StateTransitionCategories.cfrreview.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b>{StateTransitionCategories.cfrreview.fromState}</b> to <b>{StateTransitionCategories.cfrreview.toState}</b>.</>};
                  break;
                case StateTransitionCategories.cfrfeeassessed.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b> {StateTransitionCategories.cfrfeeassessed.fromState} </b> to <b> {StateTransitionCategories.cfrfeeassessed.toState} </b>.</>};
                  break;
                case StateTransitionCategories.signoffresponse.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b>{StateTransitionCategories.signoffresponse.fromState}</b> to <b>{StateTransitionCategories.signoffresponse.toState}</b>.</>};
                  break;
                case StateTransitionCategories.harmsreview.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b>{StateTransitionCategories.harmsreview.fromState}</b> to <b>{StateTransitionCategories.harmsreview.toState}</b>.</>};
                  break;
                default:
                  _message = {title: "Replace Attachment", body:`This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #${requestNumber}` }                  
                  break;
              }
            }
            return _message;
        case "rename":
          return {title: "Rename Attachment", body: ""};
        case "delete":
          return {title: "Delete Attachment", body: "Are you sure you want to delete the attachment?"};            
        default:
            return {title: "", body: ""};
      }
    }
    let message = getMessage();

    const isSaveDisabled = () => {
      if (modalFor === 'delete') {
        return false;
      } else if (files.length === 0 && existingDocuments.length === 0) {
        return true;
      } else if (modalFor === 'add') {
        return tagValue === "";
      } else if (modalFor === 'replace') {
        return false;
      }
    }
  
    return (
      <div className="state-change-dialog">        
        <Dialog
          open={openModal}
          onClose={handleClose}
          aria-labelledby="state-change-dialog-title"
          aria-describedby="state-change-dialog-description"
          maxWidth={'md'}
          fullWidth={true}
        >
          <DialogTitle disableTypography id="state-change-dialog-title" className="add-attachment-modal-title">
              <h2 className="state-change-header">{message.title}</h2>
              <IconButton aria-label= "close" onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-dialog-description" component={'span'}>
              <div className="modal-message">
                <span className="confirmation-message">
                  {message.body}                               
                </span>                
              </div>
              {
                (['replace','add'].includes(modalFor)) ?
                <FileUpload 
                  attachment={attachment}  
                  attchmentFileNameList={attchmentFileNameList}  
                  multipleFiles={multipleFiles} 
                  mimeTypes={mimeTypes} 
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
                /> 
                :
                <ModalForRename modalFor={modalFor} newFilename={newFilename} updateFilename={updateFilename} errorMessage={errorMessage} extension={extension} />
              }
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            {
              modalFor === 'rename'?
              <button className={`btn-bottom btn-save ${classes.btnenabled}`} onClick={saveNewFilename}>
                Save
              </button>
              :
              <button className={`btn-bottom btn-save ${ isSaveDisabled() ? classes.btndisabled : classes.btnenabled }`} disabled={isSaveDisabled()} onClick={handleSave}>
                {uploadFor === "email" ? "Save Changes" : "Continue"}
              </button>
            }
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
}

const ModalForRename = ({modalFor, newFilename, updateFilename, errorMessage, extension}) => {

  return(
  modalFor === 'rename'?
                <div className="row">
                  <div className="col-sm-1"></div>
                  <div className="col-sm-9">
                    <TextField
                    id="renameAttachment"                        
                    label="Rename Attachment"
                    inputProps={{ "aria-labelledby": "renameAttachment-label"}}
                    InputLabelProps={{ shrink: true, }}
                    variant="outlined"
                    fullWidth
                    value={newFilename}
                    onChange={updateFilename}
                    error={(errorMessage !== undefined && errorMessage !== "")}
                    helperText={errorMessage}
                    />
                  </div>
                  <div className="col-sm-1 extension-name">
                    .{extension}
                  </div>
                  <div className="col-sm-1"></div>
                </div>                 
                : null
  )
}
