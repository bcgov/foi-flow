import React, { useEffect, useState } from 'react'
import '../Attachments/attachments.scss'
import './records.scss'
import { useDispatch, useSelector } from "react-redux";
import AttachmentModal from '../Attachments/AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3, postFOIS3DocumentPreSignedUrl, getFOIS3DocumentPreSignedUrl } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRecords, saveFOIRecords, deleteFOIRecords, retryFOIRecordProcessing, deleteReviewerRecords, triggerDownloadFOIRecordsForHarms, fetchPDFStitchedRecordForHarms } from "../../../../apiManager/services/FOI/foiRecordServices";
import { StateTransitionCategories, AttachmentCategories } from '../../../../constants/FOI/statusEnum'
import { RecordsDownloadList, RecordDownloadCategory } from '../../../../constants/FOI/enum';
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
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
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
import { faCheckCircle, faClone } from '@fortawesome/free-regular-svg-icons';
import {faSpinner, faExclamationCircle, faBan, faArrowTurnUp } from '@fortawesome/free-solid-svg-icons';import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import _ from 'lodash';
import { DOC_REVIEWER_WEB_URL } from "../../../../constants/constants";


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
  attachmentIcon: {
    height: "20px",
    margin:"0 15px",
    rotate:"90deg"
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

 let pdfStitchStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForHarms
  );

  let pdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForHarms
  );  
  const classes = useStyles();
  const [records, setRecords] = useState(recordsObj?.records);

  useEffect(() => {
    setRecords(recordsObj?.records)
  }, [recordsObj])


  const divisionFilters = [...new Map(recordsObj?.records?.reduce((acc, file) => [...acc, ...new Map(file?.attributes?.divisions?.map(division => [division?.divisionid, division]))], [])).values()]
  if (divisionFilters?.length > 0) divisionFilters?.push(
    {divisionid: -1, divisionname: "All"},
    {divisionid: -2, divisionname: "Errors"},
    {divisionid: -3, divisionname: "Incompatible"}
  )


  const [openModal, setModal] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const dispatch = useDispatch();
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [searchValue, setSearchValue] = useState("");
  const [filterValue, setFilterValue] = useState(-1);
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const [currentDownload, setCurrentDownload] = useState(0) 
  const [isDownloadInProgress, setIsDownloadInProgress] = useState(false)
  const [isDownloadReady, setIsDownloadReady] = useState(false)
  const [isDownloadFailed, setIsDownloadFailed] = useState(false)
  
  useEffect(() => {
    switch(pdfStitchStatus) {      
      case "started":
      case "pushedtostream":
        setIsDownloadInProgress(true);
        setIsDownloadReady(false);
        setIsDownloadFailed(false);
        break;
      case "completed":
        dispatch(fetchPDFStitchedRecordForHarms(requestId, ministryId));
        setIsDownloadInProgress(false);
        setIsDownloadReady(true);
        setIsDownloadFailed(false);
        break;
      case "error":
        setIsDownloadInProgress(false);
        setIsDownloadReady(false);
        setIsDownloadFailed(true);
        break;
      default:
        setIsDownloadInProgress(false);
        setIsDownloadReady(false);
        setIsDownloadFailed(false);
        break;
    }
  }, [pdfStitchStatus, requestId, ministryId])

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
      if (updateAttachment.isattachment) {
        dispatch(deleteReviewerRecords({filepaths: [updateAttachment], ministryrequestid: ministryId },(err, _res) => {
          dispatchRequestAttachment(err);
        }));
      } else {
        const recordId = updateAttachment.recordid;
        dispatch(deleteFOIRecords(requestId, ministryId, recordId, (err, _res) => {
          dispatchRequestAttachment(err);
        }));
      }
    }
    else if (files) {
      saveDocument(value, fileInfoList, files);
    }
  }

  const saveDocument = (value, fileInfoList, files) => {
    if (value) {
      if (files.length !== 0) {
        setRecordsUploading(true)
        if (modalFor === 'replace') {
          fileInfoList[0].filepath = updateAttachment.s3uripath.substr(0, updateAttachment.s3uripath.lastIndexOf(".")) + ".pdf";
        }
        postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList, 'records', bcgovcode, dispatch, async (err, res) => {
          let _documents = [];
          if (!err) {
            var completed = 0;
            let failed = [];
            const toastID = toast.loading("Uploading files (" + completed + "/" + fileInfoList.length + ")")
            for (let header of res) {
              const _file = files.find(file => file.filename === header.filename);
              const _fileInfo = fileInfoList.find(fileInfo => fileInfo.filename === header.filename);
              const documentDetails = modalFor === 'replace' ?
                {
                  ...updateAttachment,
                  s3uripath: header.filepathdb,
                  trigger: 'recordreplace',
                  service: 'deduplication'
                }:
                {
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
            if (modalFor === 'replace') {
              dispatch(retryFOIRecordProcessing(requestId, ministryId, {records: _documents},(err, _res) => {
                  dispatchRequestAttachment(err);
              }));
            } else {
              dispatch(saveFOIRecords(requestId, ministryId, {records: _documents},(err, _res) => {
                  dispatchRequestAttachment(err);
              }));
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
            setRecordsUploading(false)
          }
        })
      }
    }
  }

  const downloadDocument = (file, isPDF = false) => {
    var s3filepath = file.s3uripath;
    var filename = file.filename
    if (isPDF) {
      s3filepath = s3filepath.substr(0, s3filepath.lastIndexOf(".")) + ".pdf";
      filename = filename + ".pdf";
    }
    getFOIS3DocumentPreSignedUrl(s3filepath.split('/').slice(4).join('/'), ministryId, dispatch, (err, res) => {
      if (!err) {
        getFileFromS3({filepath: res}, (_err, response) => {
          let blob = new Blob([response.data], {type: "application/octet-stream"});
          saveAs(blob, filename)
        });
      }
    }, 'records', bcgovcode);
  }  

  const handleDownloadChange = (e) => {
    if (e.target.value === 1 && ["not started", "error"].includes(pdfStitchStatus)) {
      toast.info("In progress. You will be notified when the records are ready for download.", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "colored",
        backgroundColor: "#FFA500"
      });
      setIsDownloadInProgress(true);      
      setIsDownloadReady(false);
      setIsDownloadFailed(false);           
      downloadLinearHarmsDocuments()      
    }
    else if (e.target.value === 1 && pdfStitchStatus === "completed") {
      const s3filepath = pdfStitchedRecord?.finalpackagepath
      const filename = requestNumber + ".zip"
      getFOIS3DocumentPreSignedUrl(s3filepath?.split('/').slice(4).join('/'), ministryId, dispatch, (err, res) => {
        if (!err) {
          getFileFromS3({filepath: res}, (_err, response) => {
            let blob = new Blob([response.data], {type: "application/octet-stream"});
            saveAs(blob, filename)
          });
        }
      }, 'records', bcgovcode);
    }
    setCurrentDownload(e.target.value); 
  }

  const downloadLinearHarmsDocuments = () => {
    let exporting = recordsObj?.records.filter(record => !record.isduplicate)
    for (let record of exporting) {
      if (record.attachments) for (let attachment of record.attachments) {
        if (!attachment.isduplicate) exporting.push(attachment);
      }
    }
    try {
      let message = {       
        attributes: []
      }
      let attributes = [];      
      for (let record of exporting) {
        const fileObj = {}
        const attributeObj = {files: []}
        let filepath = record.s3uripath
        let filename = record.filename
        if (record.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(record.attributes?.extension)) {
          filepath = filepath.substr(0, filepath.lastIndexOf(".")) + ".pdf";
          filename += ".pdf";
        }
        fileObj.recordid = record.recordid;
        fileObj.filename = filename;
        fileObj.s3uripath = filepath;
        fileObj.lastmodified = record.attributes.lastmodified;
        for (let division of record.attributes.divisions) {
          attributeObj.divisionid = division.divisionid
          attributeObj.divisionname = division.divisionname?.replace("'", "")
          attributeObj.files.push(fileObj)
        }
        //attributes will have unique files array and division combination
        attributes.push(attributeObj)        
      }

      //This will return the result by merging the files with same division id (order by lastmodified asc)
      let result = attributes.reduce((acc, val) => {
        let found = acc.find((findval) => val.divisionid === findval.divisionid);
        if (!found) acc.push(val)
        else found.files = found.files.concat(
          val.files.filter((f) => !found.files.find((findval) => f.filename === findval.filename))).sort((a,b) => {
                return new Date(Date.parse(a.lastmodified)) - new Date(Date.parse(b.lastmodified))
              });
        return acc;
      }, []);

      message.requestnumber = requestNumber
      message.bcgovcode = bcgovcode
      message.attributes = result
      message.category = RecordDownloadCategory.harms

      dispatch(triggerDownloadFOIRecordsForHarms(requestId, ministryId, message,(err, _res) => {
        dispatchRequestAttachment(err);
    }));

    } catch (error) {
      console.log(error)
      toast.error(
        "Temporarily unable to process your request. Please try again in a few minutes.",
        {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        }
      );
    }

  }

  const downloadAllDocuments = async () => {
    let blobs = [];
    var completed = 0;
    let failed = 0;
    var exporting = records.filter(record => !record.isduplicate)
    for (let record of exporting) {
      if (record.attachments) for (let attachment of record.attachments) {
        if (!attachment.isduplicate) exporting.push(attachment);
      }
    }
    const toastID = toast.loading("Exporting files (" + completed + "/" + exporting.length + ")")
    try {
      for (let record of exporting) {
        var filepath = record.s3uripath
        var filename = record.filename
        if (record.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(record.attributes?.extension)) {
          filepath = filepath.substr(0, filepath.lastIndexOf(".")) + ".pdf";
          filename += ".pdf";
        }
        const response = await getFOIS3DocumentPreSignedUrl(filepath.split('/').slice(4).join('/'), ministryId, dispatch, null, 'records', bcgovcode)
        await getFileFromS3({filepath: response.data}, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          blobs.push({name: filename, lastModified: res.headers['last-modified'], input: blob})
          completed++;
          toast.update(toastID, {
            render: "Exporting files (" + completed + "/" + exporting.length + ")",
            isLoading: true,
          })
        });
      }
    } catch (error) {
      console.log(error)
    }
    var toastOptions = {
      render: failed > 0 ? failed.length + " file(s) failed to download" : exporting.length + ' Files exported',
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
    var currentFilter = divisionFilters.find(division => division.divisionid === filterValue).divisionname;
    saveAs(zipfile, requestNumber + " Records - " + currentFilter + ".zip");
  }

  const retryDocument = (record) => {
    record.trigger = 'recordretry';
    record.service = record.failed;
    if (record.isattachment) {
      var parentRecord = recordsObj.records.find(r => r.recordid = record.rootparentid);
      record.attributes.divisions = parentRecord.attributes.divisions;
      record.attributes.batch = parentRecord.attributes.batch;
      record.attributes.extension = record['s3uripath'].substr(record['s3uripath'].lastIndexOf("."), record['s3uripath'].length);
      record.attributes.incompatible = false;
      record.attributes.isattachment = true;
    }
    if (record.service === 'deduplication') {
      record['s3uripath'] = record['s3uripath'].substr(0, record['s3uripath'].lastIndexOf(".")) + ".pdf";
    }
    dispatch(retryFOIRecordProcessing(requestId, ministryId, {records: [record]},(err, _res) => {
        dispatchRequestAttachment(err);
    }));
  }

  const removeAttachments = () => {
    setDeleteModalOpen(false);
    var attachments = records.reduce((acc, record) => {return record.attachments ? acc.concat(record.attachments.map(a => a.filepath)) : acc}, []);
    dispatch(deleteReviewerRecords({filepaths: attachments, ministryrequestid :ministryId},(err, _res) => {
      dispatchRequestAttachment(err);
    }));
  }

  const hasDocumentsToExport = records.filter(record => !(isMinistryCoordinator && record.category == 'personal')).length > 0;
  const hasDocumentsToDownload = records.filter(record => record.category !== 'personal').length > 0;

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
      case "downloadPDF":
        downloadDocument(_record, true);
        setModalFor("download");
        setModal(false);
        break;
      case "delete":
        setModalFor("delete")
        setModal(true)
        break;
      case "retry":
        retryDocument(_record);
        setModal(false)
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

  const getCurrentDownload = () => {
    if (currentDownload === 1 && isDownloadInProgress)
      return 0;
    return currentDownload;
  }

  // const onFilterChange = (filterValue) => {
    // let _filteredRecords = filterValue === "" ?
    // records.records :
    // records.records.filter(r =>
    //   r.filename.toLowerCase().includes(filterValue?.toLowerCase()) ||
    //   r.createdby.toLowerCase().includes(filterValue?.toLowerCase()) ||
    //   r.attributes?.findIndex(a => a.divisionname.toLowerCase() === filterValue?.toLowerCase().trim()) > -1
    // );
    // setRecords(_filteredRecords)
  // }


  React.useEffect(() => {
    setRecords(searchAttachments(_.cloneDeep(recordsObj.records), filterValue, searchValue));
  },[filterValue, searchValue, recordsObj])

  const searchAttachments = (_recordsArray, _filterValue, _keywordValue) =>  {
    var filterFunction = (r) => {
      if (r.attachments?.length > 0) {
        r.attachments = r.attachments.filter(filterFunction)
        return r.attachments.length > 0;
      } else {
        return (r.filename.toLowerCase().includes(_keywordValue?.toLowerCase()) ||
        r.createdby.toLowerCase().includes(_keywordValue?.toLowerCase())) &&
        (
          _filterValue === -3 ? r.attributes?.incompatible :
          _filterValue === -2 ? r.failed && !r.isredactionready:
          _filterValue > -1 ? r.attributes?.divisions?.findIndex(a => a.divisionid === _filterValue) > -1 :
          true
        )
      }
    }
    return _recordsArray.filter(filterFunction)
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
          </Grid>
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            spacing={1}
          >
            <Grid item xs={2}>
              <ConditionalComponent condition={records.filter(record => record.attachments?.length > 0).length > 0}>
                <button
                  className="btn addAttachment foi-export-button"
                  variant="contained"
                  onClick={() => setDeleteModalOpen(true)}
                  color="primary"
                >
                  Remove Attachments
                </button>
              </ConditionalComponent>
            </Grid>
            <Grid item xs={3}>
              <ConditionalComponent condition={hasDocumentsToDownload}>
              <TextField
              className="download-dropdown custom-select-wrapper foi-download-button"
              id="download"
              label={currentDownload === 0 ? "Download" : ""}
              inputProps={{ "aria-labelledby": "download-label" }}
            //   InputProps={{
            //     startAdornment: isDownloadInProgress && <InputAdornment position="start">
            //       {/* <CircularProgress class="download-progress-adornment"/> */}
            //       {/* <CircularProgress/> */}
            //       record.isredactionready ?
            //       <FontAwesomeIcon icon={faCheckCircle} size='2x' color='#1B8103' className={classes.statusIcons}/>:
            // record.failed ?
            // <FontAwesomeIcon icon={faExclamationCircle} size='2x' color='#A0192F' className={classes.statusIcons}/>:
            // <FontAwesomeIcon icon={faSpinner} size='2x' color='#FAA915' className={classes.statusIcons}/>
            //       </InputAdornment>
            //   }}
              InputLabelProps={{ shrink: false }}
              select
              name="download"
              value={currentDownload}
              onChange={handleDownloadChange}
              placeholder="Download"
              variant="outlined"
              size="small"
              fullWidth
            >
              {RecordsDownloadList.map((item, index) => {

                if (item.id !=0) {
                  return (
                      <MenuItem
                        className="download-menu-item"
                        key={item.id}
                        value={index}
                        disabled={item.disabled}
                        sx={{ display: 'flex' }}
                      >
                        {
                          !item.disabled && (isDownloadReady && !item.disabled ?
                          <FontAwesomeIcon icon={faCheckCircle} size='2x' color='#1B8103' className={classes.statusIcons}/>:
                          isDownloadFailed && !item.disabled ?
                          <FontAwesomeIcon icon={faExclamationCircle} size='2x' color='#A0192F' className={classes.statusIcons}/>:
                          isDownloadInProgress && !item.disabled ? <FontAwesomeIcon icon={faSpinner} size='2x' color='#FAA915' className={classes.statusIcons}/>:null) 
                        }
                        {item.label}
                      </MenuItem>
                    // </>
                  )
                }

              } )}
            </TextField>
              </ConditionalComponent>
            </Grid>
            {/* <Grid item xs={2}>
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
            </Grid> */}
            <Grid item xs={2}>
              {isMinistryCoordinator ?
                <button
                  className={clsx("btn", "addAttachment", classes.createButton)}
                  variant="contained"
                  onClick={addAttachments}
                  color="primary"
                >
                  + Upload Records
                </button> :
                <a href={DOC_REVIEWER_WEB_URL + "/foi/" + ministryId}>
                  <button
                    className={clsx("btn", "addAttachment", classes.createButton)}
                    variant="contained"
                    // onClick={}
                    color="primary"
                  >
                    Redact Records
                  </button>
                </a>
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
                  <span>Files Uploaded:</span>
                  <span className='number-spacing'>{recordsObj.dedupedfiles}</span>
                </Grid>
                <Grid item xs={3}>
                  <span>Deduplicated Files:</span>
                  <span className='number-spacing'>{recordsObj.removedfiles}</span>
                </Grid>
                <Grid item xs={3}>
                  <span>Files Converted to PDF:</span>
                  <span className='number-spacing'>{recordsObj.convertedfiles}</span>

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
                    color={division.divisionid === -2 ? '#A0192F' : division.divisionid === -3 ? '#B57808' : 'primary'}
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
            uploadFor={"record"}
            bcgovcode={bcgovcode}
            divisions={divisions.filter(d => d.divisionname.toLowerCase() !== 'communications')}
          />
          <div className="state-change-dialog">
            <Dialog
              open={deleteModalOpen}
              onClose={() => setDeleteModalOpen(false)}
              aria-labelledby="state-change-dialog-title"
              aria-describedby="state-change-dialog-description"
              maxWidth={'md'}
              fullWidth={true}
              // id="state-change-dialog"
            >
              <DialogTitle disableTypography id="state-change-dialog-title">
                  <h2 className="state-change-header">Remove Attachments</h2>
                  <IconButton className="title-col3" onClick={() => setDeleteModalOpen(false)}>
                    <i className="dialog-close-button">Close</i>
                    <CloseIcon />
                  </IconButton>
                </DialogTitle>
              <DialogContent className={'dialog-content-nomargin'}>
                <DialogContentText id="state-change-dialog-description" component={'span'} style={{textAlign: "center"}}>
                  <span className="confirmation-message">
                    Are you sure you want to delete the attachments from this request? <br></br>
                    <i>This will remove all attachments from the redaction app.</i>
                  </span>
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <button
                  className={`btn-bottom btn-save btn`}
                  onClick={removeAttachments}
                >
                  Continue
                </button>
                <button className="btn-bottom btn-cancel" onClick={() => setDeleteModalOpen(false)}>
                  Cancel
                </button>
              </DialogActions>
            </Dialog>
          </div>
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
          {record.isattachment && <FontAwesomeIcon icon={faArrowTurnUp} size='2x' className={classes.attachmentIcon}/>}
          {
            record.isduplicate && record.attributes?.incompatible ?
            <FontAwesomeIcon icon={faClone} size='2x' color='#FF873D' className={classes.statusIcons}/>:
            record.attributes?.incompatible ?
            <FontAwesomeIcon icon={faBan} size='2x' color='#FAA915' className={classes.statusIcons}/>:
            record.isduplicate ?
            <FontAwesomeIcon icon={faClone} size='2x' color='#FF873D' className={classes.statusIcons}/>:
            record.isredactionready ?
            <FontAwesomeIcon icon={faCheckCircle} size='2x' color='#1B8103' className={classes.statusIcons}/>:
            record.failed ?
            <FontAwesomeIcon icon={faExclamationCircle} size='2x' color='#A0192F' className={classes.statusIcons}/>:
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
              record.isduplicate && record.attributes?.incompatible ?
              <span>Duplicate of {record.duplicateof}</span>:
              record.attributes?.incompatible ?
              <span>Incompatible File Type</span>:
              record.trigger === 'recordreplace' ?
              <span>Record Manually Replaced Due to Error</span>:
              record.isduplicate ?
              <span>Duplicate of {record.duplicateof}</span>:
              record.isredactionready ?
              <span>Ready for Redaction</span>:
              record.failed ?
              <span>Error during {record.failed}</span>:
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
              style={{backgroundColor: "#003366", margin: record.isattachment && i === 0 ? "4px 4px 4px 60px" : "4px"}}
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
      {record?.attachments?.map((attachment, i) =>
        <Attachment
          key={"attachment" + i}
          indexValue={i}
          record={attachment}
          handlePopupButtonClick={handlePopupButtonClick}
          getFullname={getFullname}
          isMinistryCoordinator={isMinistryCoordinator}
          ministryId={ministryId}
          classes={classes}
        />
      )}
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

  const handleDownloadPDF = () =>{
    closeTooltip();
    handlePopupButtonClick("downloadPDF", record);
  }

  const handleView =()=>{
    closeTooltip();
    opendocumentintab(record,ministryId);
  }

  const handleDelete = () => {
    closeTooltip();
    handlePopupButtonClick("delete", record);
  };

  const handleRetry = () => {
    closeTooltip();
    handlePopupButtonClick("retry", record);
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

  const ActionsPopover = ({RestrictViewInBrowser, record}) => {

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
          {!record.isredactionready && record.failed && <MenuItem
            onClick={() => {
                handleReplace();
                setPopoverOpen(false);
            }}
          >
            Replace Manually
          </MenuItem>}
          {record.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(record.attributes?.extension) && <MenuItem
            onClick={() => {
                handleDownloadPDF();
                setPopoverOpen(false);
            }}
          >
            Download Converted
          </MenuItem>}
          <MenuItem
            onClick={() => {
                handleDownload();
                setPopoverOpen(false);
            }}
          >
            Download Original
          </MenuItem>
          <DeleteMenu />
          {!record.isredactionready && record.failed && <MenuItem
            onClick={() => {
                handleRetry();
                setPopoverOpen(false);
            }}
          >
            Re-Try
          </MenuItem>}

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
    <ActionsPopover RestrictViewInBrowser={true} record={record}/>
  </>
  );
})

export default RecordsLog