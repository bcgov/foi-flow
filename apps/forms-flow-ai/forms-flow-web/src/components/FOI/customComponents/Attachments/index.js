import React, { useEffect, useState } from 'react'
import './attachments.scss'
import { useDispatch } from "react-redux";
import AttachmentModal from './AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { StateTransitionCategories } from '../../../../constants/FOI/statusEnum'
import { addToFullnameList, getFullnameList } from '../../../../helper/FOI/helper'
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

const useStyles = makeStyles((theme) => ({
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
  const [iaoList, setIaoList] = useState(iaoassignedToList)
  const [ministryList, setMinistryList] = useState(ministryAssignedToList)
  
  useEffect(() => {
    setAttachments(attachmentsArray);
    setIaoList(iaoassignedToList);
    setMinistryList(ministryAssignedToList);
  }, [attachmentsArray, iaoassignedToList, ministryAssignedToList])
  

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
          const replaceDocumentObject = {filename: documents[0].filename, documentpath: documents[0].documentpath};
          const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;      
          dispatch(replaceFOIRequestAttachment(requestId, ministryId, documentId, replaceDocumentObject,(err, res) => {
            if (!err) {
              setAttachmentLoading(false);
              setSuccessCount(0);
            }
          }));
        }
        else {
          dispatch(saveFOIRequestAttachmentsList(requestId, ministryId, documentsObject,(err, res) => {
          if (!err) {
            setAttachmentLoading(false);
            setSuccessCount(0);
          }
        }));
      }
    }
  },[successCount])

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (modalFor === 'delete' && value) { 
      const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      dispatch(deleteFOIRequestAttachment(requestId, ministryId, documentId, {}));
    }
    else if (files) {
    setFileCount(files.length);
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
              saveFilesinS3(header, _file, dispatch, (err, res) => {
              if (res === 200) {
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
        res.map(async (header, index) => {
          getFileFromS3(header, (err, res) => {
            var blob = new Blob([res.data], {type: "application/octet-stream"});
            saveAs(blob, file.filename)
          });
        });
      }
    });
  }

  const downloadAllDocuments = async () => {
    var fileInfoList = []
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
    var blobs = [];
    try {
      const response = await getOSSHeaderDetails(fileInfoList, dispatch);
      for (var i = 0; i < response.data.length; i++) {
        await getFileFromS3(response.data[i], (err, res) => {
          var blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: response.data[i].filename, lastModified: res.headers['last-modified'], input: blob})
        });
      }
    } catch (error) {
      console.log(error)
    }
    const zipfile = await downloadZip(blobs).blob()
    saveAs(zipfile, requestNumber + ".zip");
  }

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
      dispatch(saveNewFilename(newFilename, documentId, requestId, ministryId, (err, res) => {
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

  var attachmentsList = [];
  for(var i=0; i<attachments.length; i++) {
    attachmentsList.push(
    <Attachment 
      key={i}
      indexValue={i} 
      attachment={attachments[i]} 
      handlePopupButtonClick={handlePopupButtonClick} 
      getFullname={getFullname} 
      isMinistryCoordinator={isMinistryCoordinator}
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
                {`Request #${
                  requestNumber ? requestNumber : `U-00${requestId}`
                }`}
              </h1>
            </Grid>
            <Grid item xs={3}>
              <button
                className="btn addAttachment foi-export-button"
                variant="contained"
                onClick={downloadAllDocuments}
                color="primary"
              >
                Export All
              </button>
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


const Attachment = React.memo(({indexValue, attachment, handlePopupButtonClick, getFullname, isMinistryCoordinator}) => {
  
  const classes = useStyles();
  const [filename, setFilename] = useState("");
  const [disabled, setDisabled] = useState(isMinistryCoordinator && attachment.category == 'personal');
  let lastIndex = 0;
  useEffect(() => {
    if(attachment && attachment.filename) {
      lastIndex = attachment.filename.lastIndexOf(".");
      setFilename(lastIndex>0?attachment.filename.substr(0, lastIndex):attachment.filename);
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
        <div
          className={`attachment-name ${disabled ? "attachment-disabled" : ""}`}
        >
          {attachment.filename}
        </div>
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

const AttachmentPopup = React.memo(({indexValue, attachment, handlePopupButtonClick, disabled}) => {
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



  const ActionsPopover = () => {
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
        ) : showReplace(attachment.category) ? (
            <MenuItem
                onClick={() => {
                    handleReplace();
                    setPopoverOpen(false);
                }}
            >
                Replace
            </MenuItem>
        ) : (
            <MenuItem
                onClick={() => {
                    handleDelete();
                    setPopoverOpen(false);
                }}
            >
                Delete
            </MenuItem>
          )}
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
    <ActionsPopover />
  </>
  );
})

export default AttachmentSection