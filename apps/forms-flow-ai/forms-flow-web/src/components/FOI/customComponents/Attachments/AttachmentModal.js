import React, { useState } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import '../confirmationmodal.scss';
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

export default function AttachmentModal({ modalFor, openModal, handleModal, multipleFiles, requestNumber, requestId, attachment }) {

  //mimetype, maxfilesize, totalfilesize;
    const classes = useStyles();

    const [files, setFiles] = useState([]);
    const updateFilesCb = (_files, _errorMessage) => {
      setFiles(_files);
    }
    const handleClose = () => {
        //handleModal(false);
        if (files.length > 0) {
            if (window.confirm("Are you sure you want to leave? Your changes will be lost.")) {
                // window.location.reload();
                handleModal(false);
            }
        }
        else {
            // window.location.reload();
            handleModal(false);
        }
    };

    const handleSave = () => {
        let fileInfoList = [];
        if (files.length > 0) {
            let fileStatusTransition = "attachmentlog";    
            fileInfoList = files.map(file => {
            return {
                ministrycode: "Misc",
                requestnumber: requestNumber ? requestNumber : `U-00${requestId}`,
                filestatustransition: fileStatusTransition,
                filename: file.name,
            }
            });
        }
        handleModal(true, fileInfoList, files);
    }
    const getMessage = () => {
      console.log(`modalFor.toLowerCase() === ${modalFor.toLowerCase()}`)
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
                  _message = {title: "", body: ""}                  
                  break;
              }
              console.log(`message = ${_message}`);
            }
            console.log(`message out = ${_message}`);
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
    console.log(message);
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
              <FileUpload  multipleFiles={multipleFiles} mimeTypes={MimeTypeList.attachmentLog} maxFileSize={MaxFileSizeInMB.attachmentLog} totalFileSize={MaxFileSizeInMB.totalFileSize} updateFilesCb={updateFilesCb} />                                
            </DialogContentText>
          </DialogContent>
          <DialogActions>            
            <button className={`btn-bottom btn-save ${ files.length === 0 ? classes.btndisabled : classes.btnenabled }`} disabled={files.length === 0} onClick={handleSave}>
              Continue
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
}
