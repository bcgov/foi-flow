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
import { MimeTypeList, MaxFileSize } from "../../../../constants/FOI/enum";

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

export default function AttachmentModal({ openModal, handleModal, multipleFiles, requestNumber }) {

    const classes = useStyles();

    const [files, setFiles] = useState([]);
    const updateFilesCb = (_files) => {
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
                requestnumber: requestNumber,
                filestatustransition: fileStatusTransition,
                filename: file.name,
            }
            });
        }
        //console.log(fileInfoList);
        handleModal(true, fileInfoList, files);
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
          <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Add Attachment</h2>
              <IconButton onClick={handleClose}>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
          <DialogContent>
            <DialogContentText id="state-change-description" component={'span'}>
                <FileUpload  multipleFiles={multipleFiles} mimeTypes={MimeTypeList.attachmentLog} maxFileSize={MaxFileSize.attachmentLog} updateFilesCb={updateFilesCb} />                                
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
