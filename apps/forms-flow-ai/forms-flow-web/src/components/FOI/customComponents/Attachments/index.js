import React, { useEffect, useState } from 'react'
import './attachments.scss'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { StateTransitionCategories } from '../../../../constants/FOI/statusEnum'
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
  },
  chipPrimary: {
    color: "#fff",
    backgroundColor: "#003366",
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
  const [successCount, setSuccessCount] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  const dispatch = useDispatch();
  const [documents, setDocuments] = useState([]);
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [fullnameList, setFullnameList] = useState(getFullnameList);

  const addAttachments = () => {
    setModalFor('add');
    setMultipleFiles(true);
    setUpdateAttachment({});
    setModal(true);
  }

  React.useEffect(() => {    
    if (successCount === fileCount && successCount !== 0) {
        setModal(false);
        const documentsObject = {documents: documents};
        if (modalFor === 'replace' && updateAttachment) {
          replaceAttachment();
        }
        else {
          dispatch(saveFOIRequestAttachmentsList(requestId, ministryId, documentsObject,(err, _res) => {
            dispatchRequestAttachment(err);
        }));
      }
    }
  },[successCount])

  const replaceAttachment = () => {
    const replaceDocumentObject = {filename: documents[0].filename, documentpath: documents[0].documentpath};
    const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;      
    dispatch(replaceFOIRequestAttachment(requestId, ministryId, documentId, replaceDocumentObject,(err, _res) => {
      dispatchRequestAttachment(err);
    }));
  }

  const dispatchRequestAttachment = (err) => {
    if (!err) {
      setAttachmentLoading(false);
      setSuccessCount(0);
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
        setAttachmentLoading(true);
        getOSSHeaderDetails(fileInfoList, dispatch, (err, res) => {
          let _documents = [];
          if (!err) {
            res.map((header, index) => {
              const _file = files.find(file => file.filename === header.filename);
              const documentDetails = {documentpath: header.filepath, filename: header.filename, category: 'general'};
              _documents.push(documentDetails);
              setDocuments(_documents);
              saveFilesinS3(header, _file, dispatch, (_err, _res) => {
                if (_res === 200) {
                  setSuccessCount(index+1);
                }
                else {
                  setSuccessCount(0);
                }
              })
            });
          }
        })
      }             
    }
  }

  const downloadDocument = (file) => {
    const fileInfoList = [
      {
        ministrycode: "Misc",
        requestnumber: `U-00${requestId}`,
        filestatustransition: file.category,
        filename: file.filename,
        s3sourceuri: file.documentpath
      },
    ];
    getOSSHeaderDetails(fileInfoList, dispatch, (err, res) => {
      if (!err) {
        res.map(async (header, _index) => {
          getFileFromS3(header, (_err, response) => {
            let blob = new Blob([response.data], {type: "application/octet-stream"});
            saveAs(blob, file.filename)
          });
        });
      }
    });
  }

  const downloadAllDocuments = async () => {
    let fileInfoList = []
    attachments.forEach(attachment => {
      if (!(isMinistryCoordinator && attachment.category == 'personal')) {
        fileInfoList.push({
            ministrycode: "Misc",
            requestnumber: `U-00${requestId}`,
            filestatustransition: attachment.category,
            filename: attachment.filename,
            s3sourceuri: attachment.documentpath
        });
      }
    })
    let blobs = [];
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (let header of response.data) {
        await getFileFromS3(header, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: header.filename, lastModified: res.headers['last-modified'], input: blob})
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
  for(let i=0; i<attachments.length; i++) {
    attachmentsList.push(
    <Attachment 
      key={i}
      indexValue={i} 
      attachment={attachments[i]} 
      handlePopupButtonClick={handlePopupButtonClick} 
      getFullname={getFullname} 
      isMinistryCoordinator={isMinistryCoordinator}
      ministryId={ministryId}
      classes={classes} 
    />);
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
          />
        </>
      )}
    </div>
  );
}


const Attachment = React.memo(({indexValue, attachment, handlePopupButtonClick, getFullname, isMinistryCoordinator,ministryId}) => {
  
  const classes = useStyles();
  const [disabled, setDisabled] = useState(isMinistryCoordinator && attachment.category == 'personal');
  useEffect(() => {
    if(attachment && attachment.filename) {
      setDisabled(isMinistryCoordinator && attachment.category == 'personal')
    }
  }, [attachment])

  
  const getCategory = (category) => {
    switch(category) {
      case "cfr-review":
        return "cfr - review";
      case "cfr-feeassessed":
        return "cfr - fee estimate";
      case "signoff-response":
        return "signoff - response";
      case "harms-review":
        return "harms assessment - review";
      default:
        return category || "general";
    }
  }

  const attachmenttitle = ()=>{

    if(attachment.documentpath.toLowerCase().indexOf('.eml') > 0  || attachment.documentpath.toLowerCase().indexOf('.msg') > 0 || disabled)
    {
      return (
        <div 
          className="attachment-name attachment-disabled"
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
        <Chip
          label={getCategory(attachment.category).toUpperCase()}
          size="small"
          className={clsx(classes.chip, {
            [classes.chipPrimary]: !disabled,
          })}
        />
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

      <Grid item xs={12}>
        <div
          className={`attachment-time ${disabled ? "attachment-disabled" : ""}`}
        >
          {attachment.created_at}
        </div>
      </Grid>

      <Grid item xs={12}>
        <div
          className={`attachment-owner ${
            disabled ? "attachment-disabled" : ""
          }`}
        >
          {getFullname(attachment.createdby)}
        </div>
      </Grid>

      <Grid item xs={12}>
        <Divider />
      </Grid>
    </Grid>
  );
})

const opendocumentintab =(attachment,ministryId)=>
{
  let relativedocpath = attachment.documentpath.split('/').slice(4).join('/')
  let url =`/foidocument?id=${ministryId}&filepath=${relativedocpath}`;
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
    StateTransitionCategories.harmsreview.name
  ];

  const showReplace = (category) => {
    return transitionStates.includes(category.toLowerCase());
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