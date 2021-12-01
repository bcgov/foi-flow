import React, { useEffect, useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import TextField from '@material-ui/core/TextField';
import '../confirmationmodal.scss';
import './attachmentmodal.scss';
import FileUpload from '../FileUpload';
import { makeStyles } from '@material-ui/core/styles';
import { MimeTypeList, MaxFileSizeInMB } from "../../../../constants/FOI/enum";
import { StateTransitionCategories } from '../../../../constants/FOI/statusEnum';

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

export default function AttachmentModal({ modalFor, openModal, handleModal, multipleFiles, requestNumber, requestId, attachment, attachmentsArray, handleRename }) {

    const mimeTypes = multipleFiles ? MimeTypeList.attachmentLog : MimeTypeList.stateTransition;
    const maxFileSize = multipleFiles ? MaxFileSizeInMB.attachmentLog : MaxFileSizeInMB.stateTransition;
    const totalFileSize = multipleFiles ? MaxFileSizeInMB.totalFileSize : MaxFileSizeInMB.stateTransition;
    const classes = useStyles();
    const [files, setFiles] = useState([]);
    const [newFilename, setNewFilename] = useState("");
    const [extension, setExtension] = useState("");
    const [errorMessage, setErrorMessage] = useState();
    const attchmentFileNameList = attachmentsArray.map(_file => _file.filename.toLowerCase());

    useEffect(() => {
      parseFileName(attachment);
    }, [attachment])

    const parseFileName = (_attachment) => {
      setNewFilename("");
      setExtension("");
      setErrorMessage("");
      if(_attachment && _attachment.filename) {
        var lastIndex = _attachment.filename.lastIndexOf(".");
        setNewFilename(lastIndex>0?_attachment.filename.substr(0, lastIndex):_attachment.filename);
        setExtension(lastIndex>0?_attachment.filename.substr(lastIndex+1):"");
      }
    }

    const checkInvalidCharacters = (fname) => {
      var rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
      return !fname || rg1.test(fname);
    };

    const validateFilename = (fname) => {
      var rg1 = /^[^\/:*?"<>|]+$/; // forbidden characters  / : * ? " < > |
      var rg2 = /^\./; // cannot start with dot (.)
      var rg3 = /^(nul|prn|con|lpt[0-9]|com[0-9])(.|$)/i; // forbidden file names

      return fname && rg1.test(fname) && !rg2.test(fname) && !rg3.test(fname);
    };

    const containDuplicate = (fname) => {
      if(attachment.filename !== (fname+"."+extension)) {
        // return attachmentFileNameListByCategory.includes(fname+"."+extension);
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
        if (files.length > 0 || (modalFor === 'rename' && attachment.filename !== (newFilename+"."+extension))) {
            if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
                handleModal(false);
                parseFileName(attachment);
            }
        }
        else {
            handleModal(false);
            parseFileName(attachment);
        }
    };

    const handleSave = () => {
      if (modalFor.toLowerCase() === "delete") {
        handleModal(true, null, null);
      }
      else {
        let fileInfoList = [];
        if (files.length > 0) {
          let fileStatusTransition = "";
          if (modalFor === 'replace') {
            fileStatusTransition = attachment && attachment.category;
          }
          else {
            fileStatusTransition = "general";
          }
            fileInfoList = files.map(file => {
            return {
                ministrycode: "Misc",
                requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
                filestatustransition: fileStatusTransition,
                filename: file.filename? file.filename : file.name,
            }
            });
        }
        handleModal(true, fileInfoList, files);
      }
    }  
    const getMessage = () => {
      switch(modalFor.toLowerCase()) { 
        case "add":
          return {title: "Add Attachment", body: ""};
        case "replace":
          let _message = {};
            if (attachment) {              
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
          <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">{message.title}</h2>
              <IconButton onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-description" component={'span'}>
              <div className="modal-message">
                <span className="confirmation-message">
                  {message.body}                               
                </span>                
              </div>
              {
                (['replace','add'].includes(modalFor)) ?
                <FileUpload attachment={attachment}  attchmentFileNameList={attchmentFileNameList}  multipleFiles={multipleFiles} mimeTypes={mimeTypes} maxFileSize={maxFileSize} totalFileSize={totalFileSize} updateFilesCb={updateFilesCb} /> 
                :
                (modalFor === 'rename'?
                <div class="row">
                  <div class="col-sm-1"></div>
                  <div class="col-sm-9">
                    <TextField                            
                    label="Rename Attachment"
                    InputLabelProps={{ shrink: true, }}
                    variant="outlined"
                    fullWidth
                    value={newFilename}
                    onChange={updateFilename}
                    error={(errorMessage !== undefined && errorMessage !== "")}
                    helperText={errorMessage}
                    />
                  </div>
                  <div class="col-sm-1 extension-name">
                    .{extension}
                  </div>
                  <div class="col-sm-1"></div>
                </div>                 
                : null)
              }
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            {
              modalFor === 'rename'?
              <button className="btn-bottom btn-save" onClick={saveNewFilename}>
                Save
              </button>
              :
              <button className={`btn-bottom btn-save ${ (files.length === 0 && modalFor !== 'delete') ? classes.btndisabled : classes.btnenabled }`} disabled={files.length === 0 && modalFor !== 'delete'} onClick={handleSave}>
                Continue
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
