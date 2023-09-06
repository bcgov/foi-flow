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
import FileUploadForScanning from '../FileUpload/FileUploadForScanning';
import FileUploadForMSDPersonal from '../FileUpload/FileUploadForMSDPersonal';
import { makeStyles } from '@material-ui/core/styles';
import { MimeTypeList, MaxFileSizeInMB } from "../../../../constants/FOI/enum";
import { StateTransitionCategories, AttachmentCategories } from '../../../../constants/FOI/statusEnum';
import { TOTAL_RECORDS_UPLOAD_LIMIT } from "../../../../constants/constants";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";

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
  divisions=[],
  replacementfiletypes=[],
  totalUploadedRecordSize=0,
  requestType=FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_GENERAL
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

    const recordFormats = useSelector((state) => state.foiRequests.recordFormats)
    useEffect(() => {
      setMimeTypes(multipleFiles ?
        (uploadFor === 'attachment' ? [...recordFormats, ...MimeTypeList.additional] : (uploadFor === 'record' && (modalFor==="replace" || modalFor === "replaceattachment") ? replacementfiletypes: recordFormats))
        : MimeTypeList.stateTransition);
    }, [recordFormats])
    const [mimeTypes, setMimeTypes] = useState(multipleFiles ?
      (uploadFor === 'attachment' ? [...recordFormats, ...MimeTypeList.additional] : (uploadFor === 'record' && (modalFor==="replace" || modalFor === "replaceattachment") ? replacementfiletypes: recordFormats))
      : MimeTypeList.stateTransition);
    const maxFileSize = uploadFor === 'record' ? MaxFileSizeInMB.totalFileSize : multipleFiles ? MaxFileSizeInMB.attachmentLog : MaxFileSizeInMB.stateTransition;
    const totalFileSize = multipleFiles ? MaxFileSizeInMB.totalFileSize : MaxFileSizeInMB.stateTransition;
    const classes = useStyles();
    const [files, setFiles] = useState([]);
    const [newFilename, setNewFilename] = useState("");
    const [extension, setExtension] = useState("");
    const [errorMessage, setErrorMessage] = useState();
    const [tagValue, setTagValue] = useState(uploadFor === 'record' ? "" : "general");
    const [parentTagValue, setParentTagValue] = useState(10);
    const attchmentFileNameList = attachmentsArray.map(_file => _file.filename.toLowerCase());
    const totalRecordUploadLimit= TOTAL_RECORDS_UPLOAD_LIMIT ;

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
      //let rg3 = /^(nul|prn|con|lpt\d|com\d)(.|$)/i; // forbidden file names

      return fname && rg1.test(fname) && !rg2.test(fname);
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
        if (modalFor === 'replace' || modalFor === "replaceattachment") {
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
              filesize: file.size,
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

        case "replaceattachment":
          if (uploadFor === 'record') {
            _message = {title: "Replace Records", body:<>Replace the existing record with a reformatted or updated version of the same record.<br></br>The original file that was uploaded will still be available for download.</> }
          }
          return _message;
        case "replace":
          let _message = {};
            if (uploadFor === 'record') {
              _message = {title: "Replace Records", body:<>Replace the existing record with a reformatted or updated version of the same record.<br></br>The original file that was uploaded will still be available for download.</> }
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
                case StateTransitionCategories.responsereview.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b>{StateTransitionCategories.responsereview.fromState}</b> to <b>{StateTransitionCategories.responsereview.toState}</b>.</>};
                  break;
                case StateTransitionCategories.signoffreview.name: 
                  _message = {title: "Replace Attachment", body: <>This attachment must be replaced as it was uploaded during the state change. Please replace attachment with document from Request #{requestNumber} changing from <b>{StateTransitionCategories.signoffreview.fromState}</b> to <b>{StateTransitionCategories.signoffreview.toState}</b>.</>};
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
          if (uploadFor === 'record') {
            return {title: "Delete Record", body: <>Are you sure you want to delete this record?<br></br><i>If you delete this record, the record will not appear in the redaction app for review by IAO.</i></>};
          } else {
            return {title: "Delete Attachment", body: "Are you sure you want to delete the attachment?"};
          }          
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
      } else if (modalFor === 'replace' || modalFor === 'replaceattachment') {
        return false;
      }
    }
  


    const tagL = [
      {"name": 1, "display": "111"},
      {"name": 2, "display": "222"},
      {"name": 3, "display": "333"},
      {"name": 4, "display": "444"},
      {"name": 5, "display": "555"},
      {"name": 6, "display": "666"},
      {"name": 7, "display": "777"},
      {"name": 8, "display": "888"},
      {"name": 9, "display": "999"},
      {"name": 10, "display": "101010"},
      {"name": 11, "display": "111111"},
      {"name": 12, "display": "121212"},
      {"name": 13, "display": "131313"},
      {"name": 14, "display": "141414"},
      {"name": 15, "display": "151515"},
      {"name": 16, "display": "161616"},
      {"name": 17, "display": "171717"},
      {"name": 18, "display": "181818"},
      {"name": 19, "display": "191919"},
      {"name": 20, "display": "202020"},
      {"name": 21, "display": "212121"},
      {"name": 22, "display": "222222"},
      {"name": 23, "display": "232323"},
      {"name": 24, "display": "242424"},
      {"name": 25, "display": "252525"},
      {"name": 26, "display": "262626"},
      {"name": 27, "display": "272727"},
      {"name": 28, "display": "282828"},
      {"name": 29, "display": "292929"},
      {"name": 30, "display": "303030"},
      {"name": 31, "display": "313131"},
      {"name": 32, "display": "323232"},
      {"name": 33, "display": "333333"},
      {"name": 34, "display": "343434"},
      {"name": 35, "display": "353535"},
      {"name": 36, "display": "363636"},
      {"name": 37, "display": "373737"},
      {"name": 38, "display": "383838"},
      {"name": 39, "display": "393939"},
      {"name": 40, "display": "404040"},
    ];

    const otherTagL = [
      {"name": 41, "display": "414141"},
      {"name": 42, "display": "424242"},
      {"name": 43, "display": "434343"},
      {"name": 44, "display": "444444"},
      {"name": 45, "display": "454545"},
      {"name": 46, "display": "464646"},
      {"name": 47, "display": "474747"},
      {"name": 48, "display": "484848"},
      {"name": 49, "display": "494949"},
      {"name": 50, "display": "505050"},
      {"name": 51, "display": "515151"},
      {"name": 52, "display": "525252"},
      {"name": 53, "display": "535353"},
      {"name": 54, "display": "545454"},
      {"name": 55, "display": "555555"},
      {"name": 56, "display": "565656"},
      {"name": 57, "display": "575757"},
      {"name": 58, "display": "585858"},
      {"name": 59, "display": "595959"},
      {"name": 60, "display": "606060"},
      {"name": 61, "display": "616161"},
      {"name": 62, "display": "626262"},
      {"name": 63, "display": "636363"},
      {"name": 64, "display": "646464"},
      {"name": 65, "display": "656565"},
      {"name": 66, "display": "666666"},
      {"name": 67, "display": "676767"},
      {"name": 68, "display": "686868"},
      {"name": 69, "display": "696969"},
      {"name": 70, "display": "707070"},
      {"name": 71, "display": "717171"},
      {"name": 72, "display": "727272"},
      {"name": 73, "display": "737373"},
      {"name": 74, "display": "747474"},
      {"name": 75, "display": "757575"},
      {"name": 76, "display": "767676"},
      {"name": 77, "display": "777777"},
      {"name": 78, "display": "787878"},
      {"name": 79, "display": "797979"},
      {"name": 80, "display": "808080"},
      {"name": 81, "display": "818181"},
      {"name": 82, "display": "828282"},
      {"name": 83, "display": "838383"},
      {"name": 84, "display": "848484"},
      {"name": 85, "display": "858585"},
      {"name": 86, "display": "868686"},
      {"name": 87, "display": "878787"},
      {"name": 88, "display": "888888"},
      {"name": 89, "display": "898989"},
      {"name": 90, "display": "909090"},
      {"name": 91, "display": "919191"},
      {"name": 92, "display": "929292"},
      {"name": 93, "display": "939393"},
      {"name": 94, "display": "949494"},
      {"name": 95, "display": "959595"},
      {"name": 96, "display": "969696"},
      {"name": 97, "display": "979797"},
      {"name": 98, "display": "989898"},
      {"name": 99, "display": "999999"},
      {"name": 100, "display": "100100100"},
    ];

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
              <div className="attachment-modal-message">
                <span className="confirmation-message">
                  {message.body}                               
                </span>                
              </div>
              {
                (['replaceattachment','replace','add'].includes(modalFor)) ?
                // <FileUpload 
                //   attachment={attachment}  
                //   attchmentFileNameList={attchmentFileNameList}  
                //   multipleFiles={multipleFiles} 
                //   mimeTypes={modalFor === "replaceattachment"? ['application/pdf','.pdf']: mimeTypes} 
                //   maxFileSize={maxFileSize} 
                //   totalFileSize={totalFileSize} 
                //   updateFilesCb={updateFilesCb}
                //   modalFor={modalFor}
                //   uploadFor={uploadFor}
                //   tagList={tagList}
                //   handleTagChange={handleTagChange}
                //   tagValue={tagValue}
                //   maxNumberOfFiles={maxNoFiles}
                //   isMinistryCoordinator={isMinistryCoordinator}
                //   existingDocuments={existingDocuments}
                //   totalUploadedRecordSize={totalUploadedRecordSize}
                //   totalRecordUploadLimit={totalRecordUploadLimit}
                // /> 
                // <FileUploadForScanning 
                //   attachment={attachment}  
                //   attchmentFileNameList={attchmentFileNameList}  
                //   multipleFiles={multipleFiles} 
                //   mimeTypes={modalFor === "replaceattachment"? ['application/pdf','.pdf']: mimeTypes} 
                //   maxFileSize={maxFileSize} 
                //   totalFileSize={totalFileSize} 
                //   updateFilesCb={updateFilesCb}
                //   modalFor={modalFor}
                //   uploadFor={uploadFor}
                //   tagList={tagL}
                //   otherTagList={otherTagL}
                //   handleTagChange={handleTagChange}
                //   tagValue={tagValue}
                //   maxNumberOfFiles={maxNoFiles}
                //   isMinistryCoordinator={isMinistryCoordinator}
                //   existingDocuments={existingDocuments}
                //   totalUploadedRecordSize={totalUploadedRecordSize}
                //   totalRecordUploadLimit={totalRecordUploadLimit}
                // /> 
                <FileUploadForMSDPersonal 
                  attachment={attachment}  
                  attchmentFileNameList={attchmentFileNameList}  
                  multipleFiles={multipleFiles} 
                  mimeTypes={modalFor === "replaceattachment"? ['application/pdf','.pdf']: mimeTypes} 
                  maxFileSize={maxFileSize} 
                  totalFileSize={totalFileSize} 
                  updateFilesCb={updateFilesCb}
                  modalFor={modalFor}
                  uploadFor={uploadFor}
                  tagList={tagL}
                  subTagList={otherTagL}
                  handleTagChange={handleTagChange}
                  tagValue={tagValue}
                  parentTagValue={parentTagValue}
                  maxNumberOfFiles={maxNoFiles}
                  isMinistryCoordinator={isMinistryCoordinator}
                  existingDocuments={existingDocuments}
                  totalUploadedRecordSize={totalUploadedRecordSize}
                  totalRecordUploadLimit={totalRecordUploadLimit}
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
