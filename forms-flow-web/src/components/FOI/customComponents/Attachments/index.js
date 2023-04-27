import React, { useEffect, useState } from 'react'
import './attachments.scss'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { saveFilesinS3, getFileFromS3, postFOIS3DocumentPreSignedUrl, getFOIS3DocumentPreSignedUrl, completeMultiPartUpload } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { StateTransitionCategories, AttachmentCategories, AttachmentLetterCategories } from '../../../../constants/FOI/statusEnum'
import { addToFullnameList, getFullnameList, ConditionalComponent } from '../../../../helper/FOI/helper';
import Grid from "@material-ui/core/Grid";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx"
import Chip from "@material-ui/core/Chip";
import Divider from "@material-ui/core/Divider";
import Popover from "@material-ui/core/Popover";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import IconButton from "@material-ui/core/IconButton";
import MenuList from "@material-ui/core/MenuList";
import MenuItem from "@material-ui/core/MenuItem";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import AttachmentFilter from './AttachmentFilter';
import { getCategory } from './util';
import { readUploadedFileAsBytes } from '../../../../helper/FOI/helper';
import { OSS_S3_CHUNK_SIZE } from "../../../../constants/constants";
import { toast } from "react-toastify";

const useStyles = makeStyles((_theme) => ({
  createButton: {
    margin: 0,
    width: "100%",
    backgroundColor: "#38598A",
    color: "#FFFFFF",
    fontFamily: " BCSans-Bold, sans-serif !important",
  },
  chip: {
    fontWeight: "bold",
    height: "18px",
    marginBottom: "15px",
  },
  chipPrimary: {
    color: "#fff",
    height: "18px",
    marginBottom: "15px",
  },
  ellipses: {
    color: "#38598A",
  },
  container: {
    marginTop: "60px",
    marginLeft: "1em",
    marginRight: "1em",
  },
  headerSection: {
    marginBottom: "2em",
  },
  attachmentLog: {
    marginTop: "1em",
    marginLeft: "1em",
  },
}));

export const AttachmentSection = ({
  requestNumber,
  attachmentsArray,
  requestId,
  ministryId,
  bcgovcode,
  iaoassignedToList,
  ministryAssignedToList,
  isMinistryCoordinator
}) => {
  const classes = useStyles();
  const [attachments, setAttachments] = useState(attachmentsArray)
  
  useEffect(() => {
    setAttachments(attachmentsArray);
  }, [attachmentsArray])
  

  const [openModal, setModal] = useState(false);
  const [fileCount, setFileCount] = useState(0);
  const dispatch = useDispatch();
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const [attachmentsForDisplay, setAttachmentsForDisplay] = useState(attachments)
  const [filterValue, setFilterValue] = useState('ALL');
  const [keywordValue, setKeywordValue] = useState('');

  const addAttachments = () => {
    setModalFor('add');
    setMultipleFiles(true);
    setUpdateAttachment({});
    setModal(true);
  }

  React.useEffect(() => {
    setAttachmentsForDisplay(searchAttachments(attachments, filterValue, keywordValue));
  },[filterValue, keywordValue, attachments])

  const searchAttachments = (_attachments, _filterValue, _keywordValue) =>  {
    return _attachments.filter( attachment => {
              let onecategory = getCategory(attachment.category.toLowerCase());
              return (
                (_filterValue==="ALL"?true:onecategory.tags.includes(_filterValue?.toLowerCase()))
                && ( onecategory.tags.join('-').includes(_keywordValue?.toLowerCase())
                      || attachment.category.toLowerCase().includes(_keywordValue?.toLowerCase()) 
                      || attachment.filename.toLowerCase().includes(_keywordValue?.toLowerCase()) 
                      || attachment.createdby.toLowerCase().includes(_keywordValue?.toLowerCase()) )
              )
    });
  }

  const dispatchRequestAttachment = (err) => {
    if (!err) {
      setAttachmentLoading(false);
    }
  }

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (modalFor === 'delete' && value) { 
      const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      dispatch(deleteFOIRequestAttachment(requestId, ministryId, documentId, {}));
    }
    else if (files) {
      setFileCount(files.length);
      saveDocument(value, fileInfoList, files);
    }
  }
  
  const saveDocument = (value, fileInfoList, files) => {
    if (value) {
      if (files.length !== 0) {
        // setAttachmentLoading(true);
        postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList.map(file => ({...file, multipart: true})), 'attachments', bcgovcode, dispatch, async (err, res) => {
          let _documents = [];
          if (!err) {
            let completed = 0;
            let failed = [];
            const toastID = toast.loading("Uploading files (" + completed + "/" + fileInfoList.length + ")")
            for (let header of res) {
              const _file = files.find(file => file.filename === header.filename);
              const _fileInfo = fileInfoList.find(fileInfo => fileInfo.filename === header.filename);
              const documentDetails = {documentpath: header.filepathdb, filename: header.filename, category: _fileInfo.filestatustransition};
              let bytes = await readUploadedFileAsBytes(_file)              
              const CHUNK_SIZE = OSS_S3_CHUNK_SIZE;
              const totalChunks = Math.ceil(bytes.byteLength / CHUNK_SIZE);
              let parts = [];
              for (let chunk = 0; chunk < totalChunks; chunk++) {
                let CHUNK = bytes.slice(chunk * CHUNK_SIZE, (chunk + 1) * CHUNK_SIZE);
                let response = await saveFilesinS3({filepath: header.filepaths[chunk]}, CHUNK, dispatch, (_err, _res) => {
                  if (_err) {
                    failed.push(header.filename);
                  }
                })
                if (response.status === 200) {
                  parts.push({PartNumber: chunk + 1, ETag: response.headers.etag})
                } else {
                  failed.push(header.filename);
                }
              }
              await completeMultiPartUpload({uploadid: header.uploadid, filepath: header.filepathdb, parts: parts}, ministryId, 'attachments', bcgovcode, dispatch, (_err, _res) => {                
                if (!_err && _res.ResponseMetadata.HTTPStatusCode === 200) {
                  completed++;
                  toast.update(toastID, {
                    render: "Uploading files (" + completed + "/" + fileInfoList.length + ")",
                    isLoading: true,
                  })
                  _documents.push(documentDetails);
                } else {
                  failed.push(header.filename);
                }
              })
            }
            if (_documents.length > 0) {
              if (modalFor === 'replace' && updateAttachment) {
                const replaceDocumentObject = {filename: _documents[0].filename, documentpath: _documents[0].documentpath};
                const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;      
                dispatch(replaceFOIRequestAttachment(requestId, ministryId, documentId, replaceDocumentObject,(err, _res) => {
                  dispatchRequestAttachment(err);
                }));
              }
              else {
                dispatch(saveFOIRequestAttachmentsList(requestId, ministryId, {documents: _documents}, (err, _res) => {
                  dispatchRequestAttachment(err);
                }));
              }
            }
            var toastOptions = {
              render: failed.length > 0 ?
                "The following " + failed.length + " file uploads failed\n- " + failed.join("\n- ")  :
                fileInfoList.length + ' Files successfully saved',
              type: failed.length > 0 ? "error" : "success",
            }
            toast.update(toastID, {
              ...toastOptions,
              className: "file-upload-toast",
              isLoading: false,
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              closeButton: true
            });
            setAttachmentLoading(false)
          }
        })
      }             
    }
  }

  const downloadDocument = (file) => {
    getFOIS3DocumentPreSignedUrl(file.documentpath.split('/').slice(4).join('/'), ministryId, dispatch, (err, res) => {
      if (!err) {
        getFileFromS3({filepath: res}, (_err, response) => {
          let blob = new Blob([response.data], {type: "application/octet-stream"});
          saveAs(blob, file.filename)
        });
      }
    }, 'attachments', bcgovcode);
  }

  const downloadAllDocuments = async () => {
    let blobs = [];
    try {
      for (let attachment of attachmentsForDisplay) {
        const response = await getFOIS3DocumentPreSignedUrl(attachment.documentpath.split('/').slice(4).join('/'), ministryId, dispatch, null, 'attachments', bcgovcode)
        await getFileFromS3({filepath: response.data}, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: attachment.filename, lastModified: res.headers['last-modified'], input: blob})
        });
      }
    } catch (error) {
      console.log(error)
    }
    const zipfile = await downloadZip(blobs).blob()
    saveAs(zipfile, requestNumber + ".zip");
  }

  const hasDocumentsToExport = attachments.filter(attachment => !(isMinistryCoordinator && attachment.category == 'personal')).length > 0;

  const handlePopupButtonClick = (action, _attachment) => {
    setUpdateAttachment(_attachment);
    setMultipleFiles(false);
    switch (action) {
      case "replace":
        setModalFor("replace");
        setModal(true);
        break;
      case "rename":
        setModalFor("rename");
        setModal(true);
        break;
      case "download":
        downloadDocument(_attachment);
        setModalFor("download");
        setModal(false);
        break;
      case "delete":
        setModalFor("delete")
        setModal(true)
        break;
      default:
        setModal(false);
        break;
    }
  }

  const handleRename = (_attachment, newFilename) => {
    setModal(false);

    if (updateAttachment.filename !== newFilename) {
      const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      dispatch(saveNewFilename(newFilename, documentId, requestId, ministryId, (err, _res) => {
        if (!err) {
          setAttachmentLoading(false);
        }
      }));
    }
  }

  const getFullname = (userId) => {
    let user;

    if(fullnameList) {
      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    } else {

      if(iaoassignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, "iao");
        setFullnameList(getFullnameList());
      }
  
      if(ministryAssignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, bcgovcode);
        setFullnameList(getFullnameList());
      }
  
      user = fullnameList.find(u => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    }
  };

  const getRequestNumber = ()=> {
    if (requestNumber)
      return `Request #${requestNumber}`;
    return `Request #U-00${requestId}`;
  }

  let attachmentsList = [];
  for(let i=0; i<attachmentsForDisplay.length; i++) {
    attachmentsList.push(
    <Attachment 
      key={i}
      indexValue={i} 
      attachment={attachmentsForDisplay[i]} 
      handlePopupButtonClick={handlePopupButtonClick} 
      getFullname={getFullname} 
      isMinistryCoordinator={isMinistryCoordinator}
      ministryId={ministryId}
      classes={classes} 
    />);
  }

  const handleFilterChange = (_newFilterValue) => {
    setFilterValue(_newFilterValue);
  }

  const handleKeywordChange = (_newKeywordValue) => {
    setKeywordValue(_newKeywordValue);
  }

  return (
    <div className={classes.container}>
      {isAttachmentLoading ? (
        <Grid container alignItems="center">
          <Loading costumStyle={{ position: "relative" }} />
        </Grid>
      ) : (
        <>
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            spacing={1}
          >
            <Grid item xs={6}>
              <h1 className="foi-review-request-text foi-ministry-requestheadertext">
                {getRequestNumber()}
              </h1>
            </Grid>
            <Grid item xs={3}>
              <ConditionalComponent condition={hasDocumentsToExport}>
                <button
                  className="btn addAttachment foi-export-button"
                  variant="contained"
                  onClick={downloadAllDocuments}
                  color="primary"
                >
                  Export All
                </button>
              </ConditionalComponent>
            </Grid>
            <Grid item xs={3}>
              <button
                className={clsx("btn", "addAttachment", classes.createButton)}
                variant="contained"
                onClick={addAttachments}
                color="primary"
              >
                + Add Attachment
              </button>
            </Grid>
            <Grid
              container
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              spacing={1}
              className={classes.attachmentLog}
            >
              <AttachmentFilter handleFilterChange={handleFilterChange} filterValue={filterValue} handleKeywordChange={handleKeywordChange} keyWordValue={keywordValue} isMinistryCoordinator={isMinistryCoordinator} />
            </Grid>
            <Grid
              container
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              spacing={1}
              className={classes.attachmentLog}
            >
              {attachmentsList}
            </Grid>
          </Grid>

          <AttachmentModal
            modalFor={modalFor}
            openModal={openModal}
            handleModal={handleContinueModal}
            multipleFiles={multipleFiles}
            requestNumber={requestNumber}
            requestId={requestId}
            attachment={updateAttachment}
            attachmentsArray={attachmentsArray}
            handleRename={handleRename}
            maxNoFiles={10}
            isMinistryCoordinator={isMinistryCoordinator}
          />
        </>
      )}
    </div>
  );
}


const Attachment = React.memo(({indexValue, attachment, handlePopupButtonClick, getFullname, isMinistryCoordinator,ministryId}) => {
  
  const classes = useStyles();

  const disableCategory = () => {
    if (['personal', AttachmentLetterCategories.feeestimatefailed.name, AttachmentLetterCategories.feeestimatesuccessful.name, AttachmentLetterCategories.feeestimateletter.name, AttachmentLetterCategories.feeestimatepaymentreceipt.name, AttachmentLetterCategories.feeestimatepaymentcorrespondencesuccessful.name, AttachmentLetterCategories.feeestimatepaymentcorrespondencefailed.name].includes(attachment.category?.toLowerCase()) )
      return true;      
  }
  const [disabled, setDisabled] = useState(isMinistryCoordinator && disableCategory());
  useEffect(() => {
    if(attachment && attachment.filename) {
      setDisabled(isMinistryCoordinator && disableCategory())
    }
  }, [attachment])

  const attachmenttitle = ()=>{

    if (disabled)
    {
      return (
        <div 
          className="attachment-name attachment-disabled"
        >
          {attachment.filename}
        </div>
      )
    }

    if(attachment.documentpath.toLowerCase().indexOf('.eml') > 0  || attachment.documentpath.toLowerCase().indexOf('.msg') > 0 || attachment.documentpath.toLowerCase().indexOf('.txt') > 0)
    {
      return (
        <div 
          className="attachment-name viewattachment" onClick={()=>handlePopupButtonClick("download", attachment)}
        >
          {attachment.filename}
        </div>
      )
     
    }   
    else{
      return (
        <div onClick={()=>{
          opendocumentintab(attachment,ministryId);
        }}
          className="attachment-name viewattachment"
        >
          {attachment.filename}
        </div>
      )
    }

    
  }

  return (
    <>
      <Grid
        container
        item
        xs={12}
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={1}
      >
        <Grid item xs={11}>
          {attachmenttitle()}
        </Grid>
        <Grid 
          item 
          xs={1}
          container
          direction="row-reverse"
          justifyContent="flex-start"
          alignItems="flex-start"
        >
          <AttachmentPopup
            indexValue={indexValue}
            attachment={attachment}
            handlePopupButtonClick={handlePopupButtonClick}
            disabled={disabled}
            ministryId={ministryId}
          />
        </Grid>
      </Grid>
      <Grid 
        container
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={1}
      >
        <Grid item xs={2} style={{ minWidth: "150px" }} >
          <Chip
            label={getCategory(attachment.category)?.display}
            size="small"
            className={clsx(classes.chip, {
              [classes.chipPrimary]: !disabled,
            })}
            style={{backgroundColor: disabled?"#e0e0e0":getCategory(attachment.category).bgcolor, width: "130px"}}
          />
        </Grid>
        <Grid item xs={2}>
          <div
            className={`attachment-owner ${
              disabled ? "attachment-disabled" : ""
            }`}
          >
            {getFullname(attachment.createdby)}
          </div>
        </Grid>
        <Grid item xs={4}>
          <div
            className={`attachment-time ${disabled ? "attachment-disabled" : ""}`}
          >
            {attachment.created_at}
          </div>
        </Grid>
      </Grid>
      <Grid 
        container
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={3}
      >
        <Grid item xs={12}>
          <Divider className={"attachment-divider"} />
        </Grid>
      </Grid>
    </>
  );
})

const opendocumentintab =(attachment,ministryId)=>
{
  let relativedocpath = attachment.documentpath.split('/').slice(4).join('/')
  let url =`/foidocument?id=${ministryId || -1}&filepath=${relativedocpath}`;
  window.open(url, '_blank').focus();
}

const AttachmentPopup = React.memo(({indexValue, attachment, handlePopupButtonClick, disabled,ministryId}) => {
  const ref = React.useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close():{};

  const handleRename = () => {
    closeTooltip(); 
    handlePopupButtonClick("rename", attachment);
  }

  const handleReplace = () => {
    closeTooltip(); 
    handlePopupButtonClick("replace", attachment);
  }

  const handleDownload = () =>{
    closeTooltip();   
    handlePopupButtonClick("download", attachment);
  }

  const handleView =()=>{
    closeTooltip();    
    opendocumentintab(attachment,ministryId);
  }

  const handleDelete = () => {
    closeTooltip(); 
    handlePopupButtonClick("delete", attachment);
  };

  const transitionStates = [
    "statetransition",
    StateTransitionCategories.cfrreview.name,
    StateTransitionCategories.cfrfeeassessed.name,
    StateTransitionCategories.signoffresponse.name,
    StateTransitionCategories.harmsreview.name,
    StateTransitionCategories.feeonhold.name,
    StateTransitionCategories.responseonhold.name,
    StateTransitionCategories.responsereview.name,
    StateTransitionCategories.signoffreview.name
  ];

  const emailCategories = [
    AttachmentLetterCategories.feeestimatefailed.name,
    AttachmentLetterCategories.feeestimatesuccessful.name,    
    AttachmentLetterCategories.feeestimateletter.name,
    AttachmentLetterCategories.feeestimatepaymentreceipt.name,
    AttachmentLetterCategories.feeestimatepaymentcorrespondencesuccessful.name,
    AttachmentLetterCategories.feeestimatepaymentcorrespondencefailed.name,
    AttachmentLetterCategories.feeestimateoutstandingletter.name
  ]

  const showReplace = (category) => {
    return transitionStates.includes(category.toLowerCase());
  }

  const showDelete = (category) => {
    return !emailCategories.includes(category.toLowerCase());
  }

  const [popoverOpen, setPopoverOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);

  const ReplaceMenu = () => {
    return (
      <MenuItem
        onClick={() => {
          handleReplace();
          setPopoverOpen(false);
         }}
      >
        Replace
      </MenuItem>
    )
  }

  const DeleteMenu = () => {

    return (
      <MenuItem
        onClick={() => {
          handleDelete();
          setPopoverOpen(false);
         }}
      >
        Delete
      </MenuItem>
    )

  }

  const AddMenuItems = () => {
    if (showReplace(attachment.category))
      return (<ReplaceMenu />)
    else if (!showDelete(attachment.category))
      return null;
    return (<DeleteMenu />)
  }

  const ActionsPopover = ({RestrictViewInBrowser}) => {

    return (
      <Popover
        anchorReference="anchorPosition"
        anchorPosition={
          anchorPosition && {
            top: anchorPosition.top,
            left: anchorPosition.left,
          }
        }
        open={popoverOpen}
        anchorOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={() => setPopoverOpen(false)}
      >
        <MenuList>
{!RestrictViewInBrowser ?
        <MenuItem
            onClick={() => {
                handleView();
                setPopoverOpen(false);
            }}
          >
            View
          </MenuItem>
          :""}
          <MenuItem
            onClick={() => {
                handleDownload();
                setPopoverOpen(false);
            }}
          >
            Download
          </MenuItem>
          <MenuItem
            onClick={() => {
                handleRename();
                setPopoverOpen(false);
            }}
          >
            Rename
          </MenuItem>
          {attachment.category === "personal" ? (
          ""
        ) : <AddMenuItems />}
        </MenuList>
      </Popover>
    );
  };

  return (
    <>
      <IconButton
        aria-label= "actions"
        id={`ellipse-icon-${indexValue}`}
        key={`ellipse-icon-${indexValue}`}
        color="primary"
        disabled={disabled}
        onClick={(e) => {
          setPopoverOpen(true);
          setAnchorPosition(
            e.currentTarget.getBoundingClientRect()
          );
        }}                      
      >
      <MoreHorizIcon />
    </IconButton>
    <ActionsPopover RestrictViewInBrowser={attachment.documentpath.toLowerCase().indexOf('.eml') > 0 || attachment.documentpath.toLowerCase().indexOf('.msg') > 0 ? true:false }/>
  </>
  );
})

export default AttachmentSection