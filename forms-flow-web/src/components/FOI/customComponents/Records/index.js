import React, { useEffect, useState } from 'react'
import '../Attachments/attachments.scss'
import './records.scss'
import { useDispatch, useSelector } from "react-redux";
import AttachmentModal from '../Attachments/AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3, postFOIS3DocumentPreSignedUrl, getFOIS3DocumentPreSignedUrl } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRecords, saveFOIRecords, deleteFOIRecords } from "../../../../apiManager/services/FOI/foiRecordServices";
import { StateTransitionCategories, AttachmentCategories } from '../../../../constants/FOI/statusEnum'
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
import AttachmentFilter from '../Attachments/AttachmentFilter';
import Accordion from '@material-ui/core/Accordion';
import {  ClickableChip  } from "../../Dashboard/utils";
import Stack from "@mui/material/Stack";
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import Paper from "@mui/material/Paper";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faTimesCircle  } from '@fortawesome/free-regular-svg-icons';
import {faSpinner } from '@fortawesome/free-solid-svg-icons';


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
  },
  chipPrimary: {
    color: "#fff",
    height: "18px",
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
  recordLog: {
    marginTop: "1em"
  },
  heading: {
    color: '#FFF',
    fontSize: '16px !important',
    fontWeight: 'bold !important',
    flexDirection: 'row-reverse',
  },
  actions: {
    textAlign:'right'
  },
  createDate: {
    fontStyle: "italic",
    fontSize: "14px"
  },
  createBy: {
    fontStyle: "italic",
    fontSize: "14px",
    display: "flex"
  },
  filename: {
    fontWeight: "bold"
  },
  divider: {
    marginTop: "-2px",
    marginBottom: "-5px"
  },
  topDivider: {
    paddingTop: '0px !important',
  },
  recordStatus:{
    fontSize:"12px",
    color:"#a7a1a1",
    display:"flex"
  },
  statusIcons: {
    height: "20px",
    paddingRight:"10px"
  },
  recordReports:{
    marginTop: "1em",
    fontSize: "14px",
    marginBottom: "0px",
    marginLeft: "15px",
    fontWeight:'bold'
  },
  // reportText:{
  //   fontWeight:'bold'
  // },
  fileSize: {
    paddingLeft:'20px'
  }
}));

export const RecordsLog = ({
  divisions,
  requestNumber,
  requestId,
  ministryId,
  bcgovcode,
  iaoassignedToList,
  ministryAssignedToList,
  isMinistryCoordinator,
  setRecordsUploading
}) => {

  let recordsObj = useSelector(
    (state) => state.foiRequests.foiRequestRecords
  );

  const classes = useStyles();
  const [records, setRecords] = useState(recordsObj?.records);


  useEffect(() => {
    setRecords(recordsObj?.records)
  }, [recordsObj])

 
  const divisionFilters = [...new Map(recordsObj?.records?.reduce((acc, file) => [...acc, ...new Map(file?.attributes?.divisions?.map(division => [division?.divisionid, division]))], [])).values()]
  if (divisionFilters?.length > 0) divisionFilters?.push({divisionid: -1, divisionname: "ALL"})


  const [openModal, setModal] = useState(false);
  const dispatch = useDispatch();
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [searchValue, setSearchValue] = useState("");
  const [filterValue, setFilterValue] = useState(-1);
  const [fullnameList, setFullnameList] = useState(getFullnameList);

  const addAttachments = () => {
    setModalFor('add');
    setMultipleFiles(true);
    setUpdateAttachment({});
    setModal(true);
  }

  const dispatchRequestAttachment = (err) => {
    if (!err) {
      setAttachmentLoading(false);
      dispatch(fetchFOIRecords(requestId, ministryId))
    }
  }

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (modalFor === 'delete' && value) {
      //const documentId = ministryId ? updateAttachment.foiministrydocumentid : updateAttachment.foidocumentid;
      const recordId = updateAttachment.recordid;
      dispatch(deleteFOIRecords(requestId, ministryId, recordId, (err, _res) => {
        dispatchRequestAttachment(err);
      }));
    }
    else if (files) {
      saveDocument(value, fileInfoList, files);
    }
  }

  const saveDocument = (value, fileInfoList, files) => {
    if (value) {
      if (files.length !== 0) {
        setRecordsUploading(true)
        postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList, 'records', bcgovcode, dispatch, async (err, res) => {
          let _documents = [];
          if (!err) {
            var completed = 0;
            let failed = [];
            const toastID = toast.loading("Uploading files (" + completed + "/" + fileInfoList.length + ")")
            for (let header of res) {
              const _file = files.find(file => file.filename === header.filename);
              const _fileInfo = fileInfoList.find(fileInfo => fileInfo.filename === header.filename);
              const documentDetails = {
                s3uripath: header.filepathdb,
                filename: header.filename,
                attributes:{
                  divisions:[{divisionid: _fileInfo.divisionid}],
                  lastmodified: _file.lastModifiedDate,
                  filesize: _file.size
                }
              };
              await saveFilesinS3(header, _file, dispatch, (_err, _res) => {
                if (!_err && _res === 200) {
                  completed++;
                  toast.update(toastID, {
                    render: "Uploading files (" + completed + "/" + fileInfoList.length + ")",
                    isLoading: true,
                  })
                  _documents.push(documentDetails);
                }
                else {
                  failed.push(header.filename);
                }
              })
            }
            dispatch(saveFOIRecords(requestId, ministryId, {records: _documents},(err, _res) => {
                dispatchRequestAttachment(err);
            }));
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
            setRecordsUploading(false)
          }
        })
      }
    }
  }

  const downloadDocument = (file) => {
    getFOIS3DocumentPreSignedUrl(file.s3uripath.split('/').slice(4).join('/'), ministryId, dispatch, (err, res) => {
      if (!err) {
        getFileFromS3({filepath: res}, (_err, response) => {
          let blob = new Blob([response.data], {type: "application/octet-stream"});
          saveAs(blob, file.filename)
        });
      }
    }, 'records', bcgovcode);
  }

  const downloadAllDocuments = async () => {
    let blobs = [];
    var completed = 0;
    let failed = 0;
    const toastID = toast.loading("Exporting files (" + completed + "/" + records.length + ")")
    try {
      for (let record of records) {
        const response = await getFOIS3DocumentPreSignedUrl(record.s3uripath.split('/').slice(4).join('/'), ministryId, dispatch, null, 'records', bcgovcode)
        await getFileFromS3({filepath: response.data}, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: record.filename, lastModified: res.headers['last-modified'], input: blob})
          completed++;
          toast.update(toastID, {
            render: "Exporting files (" + completed + "/" + records.length + ")",
            isLoading: true,
          })
        });
      }
    } catch (error) {
      console.log(error)
    }
    var toastOptions = {
      render: failed > 0 ? failed.length + " file(s) failed to download" : records.length + ' Files exported',
      type: failed > 0 ? "error" : "success",
    }
    toast.update(toastID, {
      ...toastOptions,
      isLoading: false,
      autoClose: 3000,
      hideProgressBar: true,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      closeButton: true
    });
    const zipfile = await downloadZip(blobs).blob()
    saveAs(zipfile, requestNumber + ".zip");
  }

  const hasDocumentsToExport = records.filter(record => !(isMinistryCoordinator && record.category == 'personal')).length > 0;

  const handlePopupButtonClick = (action, _record) => {
    setUpdateAttachment(_record);
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
        downloadDocument(_record);
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

  const handleRename = (_record, newFilename) => {
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

  // const onFilterChange = (filterValue) => {
    // let _filteredRecords = filterValue === "" ?
    // records.records :
    // records.records.filter(r =>
    //   r.filename.toLowerCase().includes(filterValue?.toLowerCase()) ||
    //   r.createdby.toLowerCase().includes(filterValue?.toLowerCase()) ||
    //   r.attributes.findIndex(a => a.divisionname.toLowerCase() === filterValue?.toLowerCase().trim()) > -1
    // );
    // setRecords(_filteredRecords)
  // }


  React.useEffect(() => {
    setRecords(searchAttachments(recordsObj.records, filterValue, searchValue));
  },[filterValue, searchValue, recordsObj])

  const searchAttachments = (_recordsArray, _filterValue, _keywordValue) =>  {
    return _recordsArray.filter(r =>
      (r.filename.toLowerCase().includes(_keywordValue?.toLowerCase()) ||
      r.createdby.toLowerCase().includes(_keywordValue?.toLowerCase())) &&
      (_filterValue > -1 ? r.attributes?.divisions?.findIndex(a => a.divisionid === _filterValue) > -1 : true))
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
                  Export Shown
                </button>
              </ConditionalComponent>
            </Grid>
            <Grid item xs={3}>
              {isMinistryCoordinator ?
                <button
                  className={clsx("btn", "addAttachment", classes.createButton)}
                  variant="contained"
                  onClick={addAttachments}
                  color="primary"
                >
                  + Upload Records
                </button> :
                <button
                  className={clsx("btn", "addAttachment", classes.createButton)}
                  variant="contained"
                  // onClick={}
                  color="primary"
                >
                  Redact Records
                </button>
              }
            </Grid>
            <Grid
              container
              item
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              xs={12}
              className={classes.recordReports}
            >
             <Grid container spacing={2} className={classes.reportText}>
                <Grid item xs={3}>
                  <span>Deduplicated Files:</span>
                  <span className='number-spacing'>{recordsObj.dedupedfiles}</span>
                </Grid>
                <Grid item xs={3}>
                  <span>Files Removed:</span>
                  <span className='number-spacing'>{recordsObj.removedfiles}</span>
                </Grid>
                <Grid item xs={3}>
                  <span>Files Converted to PDF:</span>
                  <span className='number-spacing'>0</span>

                </Grid>
                <Grid item xs={3} direction="row-reverse">
                  <span style={{float:"right"}}>
                    <span >Batches Uploaded:</span>
                    <span className='number-spacing'>{recordsObj.batchcount ? recordsObj.batchcount : 0}</span>
                  </span>
                </Grid>
                {/* <Grid item xs={3}>
                  <span>Batches Uploaded:</span>
                  <span className='number-spacing'>{recordsObj.batchcount ? recordsObj.batchcount : 0}</span>
                </Grid> */}
              </Grid> 
            </Grid>
            <Grid
              container
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              spacing={3}
              className={classes.divider}
            >
              <Grid item xs={12} className={classes.topDivider}>
                <Divider className={"record-divider"} style={{backgroundColor: '#979797'}}/>
              </Grid>
            </Grid>
            <Grid
              container
              item
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              xs={12}
              className={classes.recordLog}
            >
              <Paper
                component={Grid}
                sx={{
                  border: "1px solid #38598A",
                  color: "#38598A",
                  maxWidth:"100%",
                  backgroundColor: "rgba(56,89,138,0.1)",
                  borderBottomLeftRadius: 0,
                  borderBottomRightRadius: 0
                }}
                alignItems="center"
                justifyContent="center"
                direction="row"
                container
                item
                xs={12}
                elevation={0}
              >
                <Grid
                  item
                  container
                  alignItems="center"
                  direction="row"
                  xs={true}
                  className="search-grid"
                >
                  <label className="hideContent">Filter Records</label>
                  <InputBase
                    id="foicommentfilter"
                    placeholder="Filter Records ..."
                    defaultValue={""}
                    onChange={(e)=>{setSearchValue(e.target.value.trim())}}
                    sx={{
                      color: "#38598A",
                    }}
                    startAdornment={
                      <InputAdornment position="start">
                        <IconButton
                          className="search-icon"
                        >
                          <span className="hideContent">Filter Records ...</span>
                          <SearchIcon />
                        </IconButton>
                      </InputAdornment>
                    }
                    fullWidth
                  />
                </Grid>
              </Paper>
              <Paper
                component={Grid}
                sx={{
                  border: "1px solid #38598A",
                  color: "#38598A",
                  maxWidth:"100%",
                  paddingTop: "8px",
                  borderTopLeftRadius: 0,
                  borderTopRightRadius: 0,
                  borderTop: "none"
                }}
                alignItems="center"
                justifyContent="flex-start"
                direction="row"
                container
                item
                xs={12}
                elevation={0}
              >
                {divisionFilters.map(division =>
                  <ClickableChip
                    item
                    id={`${division.divisionid}Tag`}
                    key={`${division.divisionid}-tag`}
                    label={division.divisionname.toUpperCase()}
                    sx={{width: "fit-content", marginLeft: "8px", marginBottom: "8px" }}
                    color="primary"
                    size="small"
                    onClick={(e)=>{setFilterValue(division.divisionid === filterValue ? -1 : division.divisionid)}}
                    clicked={filterValue == division.divisionid}
                  />
                  )}
              </Paper>
            </Grid>
            <Grid
              container
              item
              xs={12}
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
              className={classes.recordLog}
            >
              {records.map((record, i) =>
                <Attachment
                  key={i}
                  indexValue={i}
                  record={record}
                  handlePopupButtonClick={handlePopupButtonClick}
                  getFullname={getFullname}
                  isMinistryCoordinator={isMinistryCoordinator}
                  ministryId={ministryId}
                  classes={classes}
                />
              )}
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
            attachmentsArray={[]}
            handleRename={handleRename}
            isMinistryCoordinator={isMinistryCoordinator}
            uploadFor={"records"}
            bcgovcode={bcgovcode}
            divisions={divisions}
          />
        </>
      )}
    </div>
  );
}


const Attachment = React.memo(({indexValue, record, handlePopupButtonClick, getFullname, isMinistryCoordinator,ministryId}) => {

  const classes = useStyles();
  const [disabled, setDisabled] = useState(false);
  // useEffect(() => {
  //   if(record && record.filename) {
  //     setDisabled(isMinistryCoordinator && record.category == 'personal')
  //   }
  // }, [record])


  const getCategory = (category) => {
    return AttachmentCategories.categorys.find(element => element.name === category);
  }

  const recordtitle = ()=>{

    if (disabled)
    {
      return (
        <div
          className="record-name record-disabled"
        >
          {record.filename}
        </div>
      )
    }

    if(record.filename.toLowerCase().indexOf('.eml') > 0  || record.filename.toLowerCase().indexOf('.msg') > 0 || record.filename.toLowerCase().indexOf('.txt') > 0)
    {
      return (
        <div
          className="record-name viewrecord" onClick={()=>handlePopupButtonClick("download", record)}
        >
          {record.filename}
        </div>
      )

    }
    else{
      return (
        <div onClick={()=>{
          opendocumentintab(record,ministryId);
        }}
          className="record-name viewrecord"
        >
          {record.filename}
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
      >
        <Grid item xs={6}>
            { record.isduplicate ?
              <FontAwesomeIcon icon={faTimesCircle} size='2x' color='#A0192F' className={classes.statusIcons}/>:
              record.isdeduplicated ?
              <FontAwesomeIcon icon={faCheckCircle} size='2x' color='#1B8103' className={classes.statusIcons}/>: 
              <FontAwesomeIcon icon={faSpinner} size='2x' color='#FAA915' className={classes.statusIcons}/>
            }
          <span className={classes.filename}>{record.filename} </span>
          <span className={classes.fileSize}>{record?.attributes?.filesize > 0 ? (record?.attributes?.filesize / 1024).toFixed(2) : 0} KB</span>
        </Grid>
        <Grid item xs={6} direction="row" 
            justifyContent="flex-end"
            alignItems="flex-end"
            className={classes.recordStatus}>
            { 
              record.isduplicate ?
              <span>Duplicate of {record.duplicateof}</span>:
              record.isdeduplicated ?
              <span>Ready for Redaction</span>:
              <span>Deduplication & file conversion in progress</span>
            }
            <AttachmentPopup
            indexValue={indexValue}
            record={record}
            handlePopupButtonClick={handlePopupButtonClick}
            disabled={disabled}
            ministryId={ministryId}
          />
        </Grid>
      </Grid>
      <Grid
        container
        item
        xs="auto"
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
      >
      <Grid item xs={6}>
        {record.attributes?.divisions?.map((division, i) =>
          <Chip
            item
            key={i}
            label={division.divisionname}
            size="small"
            className={clsx(classes.chip, classes.chipPrimary)}
            style={{backgroundColor: "#003366", margin: "4px"}}
          />
        )}
      </Grid>
      <Grid item xs={2} 
        direction="row"
        justifyContent="flex-end"
        alignItems="flex-end" 
        className={classes.createBy}>
          <div
            className={`record-owner ${
              disabled ? "record-disabled" : ""
            }`}
          >
            {getFullname(record.createdby)}
          </div>
        </Grid>
        <Grid item xs={4} 
         direction="row"
         justifyContent="flex-end"
         alignItems="flex-end" 
         className={classes.createDate}>
          <div
            className='record-time'
          >
            {record.created_at}
          </div>
        </Grid>
      </Grid>
      <Grid
        container
        direction="row"
        justify="flex-start"
        alignItems="flex-start"
        spacing={3}
        className={classes.divider}
      >
        <Grid item xs={12}>
          <Divider className={"record-divider"} />
        </Grid>
      </Grid>
    </>
  );
})

const opendocumentintab =(record,ministryId)=>
{
  let relativedocpath = record.documentpath.split('/').slice(4).join('/')
  let url =`/foidocument?id=${ministryId}&filepath=${relativedocpath}`;
  window.open(url, '_blank').focus();
}

const AttachmentPopup = React.memo(({indexValue, record, handlePopupButtonClick, disabled,ministryId}) => {
  const ref = React.useRef();
  const closeTooltip = () => ref.current && ref ? ref.current.close():{};

  const handleRename = () => {
    closeTooltip();
    handlePopupButtonClick("rename", record);
  }

  const handleReplace = () => {
    closeTooltip();
    handlePopupButtonClick("replace", record);
  }

  const handleDownload = () =>{
    closeTooltip();
    handlePopupButtonClick("download", record);
  }

  const handleView =()=>{
    closeTooltip();
    opendocumentintab(record,ministryId);
  }

  const handleDelete = () => {
    closeTooltip();
    handlePopupButtonClick("delete", record);
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

  // const AddMenuItems = () => {
  //   if (showReplace(record.category))
  //     return (<ReplaceMenu />)
  //   return (<DeleteMenu />)
  // }

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
          <DeleteMenu />

          {/* {record.category === "personal" ? (
          ""
        ) : <DeleteMenu />} */}
        </MenuList>
      </Popover>
    );
  };

  return (
    <>
      <IconButton
        className="records-actions-btn"
        aria-label= "actions"
        id={`ellipse-icon-${indexValue}`}
        key={`ellipse-icon-${indexValue}`}
        color="primary"
        disabled={disabled}
        onClick={(e) => {
          setPopoverOpen(true);
          setAnchorPosition(
            e?.currentTarget?.getBoundingClientRect()
          );
        }}
      >
      <MoreHorizIcon />
    </IconButton>
    <ActionsPopover RestrictViewInBrowser={true}/>
  </>
  );
})

export default RecordsLog