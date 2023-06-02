import React, { useEffect, useState } from 'react'
import '../Attachments/attachments.scss'
import './records.scss'
import { useDispatch, useSelector } from "react-redux";
import AttachmentModal from '../Attachments/AttachmentModal';
import Loading from "../../../../containers/Loading";
import { getOSSHeaderDetails, saveFilesinS3, getFileFromS3, postFOIS3DocumentPreSignedUrl, getFOIS3DocumentPreSignedUrl, completeMultiPartUpload } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveFOIRequestAttachmentsList, replaceFOIRequestAttachment, saveNewFilename, deleteFOIRequestAttachment } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRecords, saveFOIRecords, deleteFOIRecords, retryFOIRecordProcessing,replaceFOIRecordProcessing, deleteReviewerRecords, getRecordFormats, triggerDownloadFOIRecordsForHarms, fetchPDFStitchedRecordForHarms, checkForRecordsChange } from "../../../../apiManager/services/FOI/foiRecordServices";
import { StateTransitionCategories, AttachmentCategories } from '../../../../constants/FOI/statusEnum'
import { RecordsDownloadList, RecordDownloadCategory,MimeTypeList } from '../../../../constants/FOI/enum';
import { addToFullnameList, getFullnameList, ConditionalComponent, isrecordtimeout } from '../../../../helper/FOI/helper';
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
import {faSpinner, faExclamationCircle, faBan, faArrowTurnUp, faHistory } from '@fortawesome/free-solid-svg-icons';import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import _ from 'lodash';
import { DOC_REVIEWER_WEB_URL, RECORD_PROCESSING_HRS, OSS_S3_CHUNK_SIZE, DISABLE_REDACT_WEBLINK } from "../../../../constants/constants";
import {removeDuplicateFiles, addDeduplicatedAttachmentsToRecords, getPDFFilePath, sortDivisionalFiles, calculateTotalFileSize,calculateTotalUploadedFileSizeInKB,getReadableFileSize} from "./util"
import { readUploadedFileAsBytes } from '../../../../helper/FOI/helper';
import { TOTAL_RECORDS_UPLOAD_LIMIT } from "../../../../constants/constants";
//import {convertBytesToMB} from "../../../../components/FOI/customComponents/FileUpload/util";


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
  const [totalUploadedRecordSize, setTotalUploadedRecordSize] = useState(0);
  useEffect(() => {
    setRecords(recordsObj?.records)
    let nonDuplicateRecords = recordsObj?.records.filter(record => !record.isduplicate)
    let totalUploadedSize= (calculateTotalUploadedFileSizeInKB(nonDuplicateRecords)/ (1024 * 1024))
    setTotalUploadedRecordSize(parseFloat(totalUploadedSize.toFixed(4)));
    dispatch(checkForRecordsChange(requestId, ministryId))
  }, [recordsObj])

  useEffect(() => {
    dispatch(getRecordFormats());
  }, [])


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
  const [replaceRecord, setreplaceRecord] = useState({});
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [searchValue, setSearchValue] = useState("");
  const [filterValue, setFilterValue] = useState(-1);
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const [recordsDownloadList, setRecordsDownloadList] = useState(RecordsDownloadList);
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
          dispatch(deleteReviewerRecords({filepaths: [updateAttachment.filepath], ministryrequestid: ministryId},(err, _res) => {
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
        if (modalFor === 'replaceattachment') {
          fileInfoList[0].filepath = updateAttachment.s3uripath.substr(0, updateAttachment.s3uripath.lastIndexOf(".")) + ".pdf";
        }
        postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList.map(file => ({...file, multipart: true})), 'records', bcgovcode, dispatch, async (err, res) => {
          let _documents = [];
          if (!err) {
            var completed = 0;
            let failed = [];
            const toastID = toast.loading("Uploading files (" + completed + "/" + fileInfoList.length + ")")
            for (let header of res) {
              const _file = files.find(file => file.filename === header.filename);
              const _fileInfo = fileInfoList.find(fileInfo => fileInfo.filename === header.filename);
              var documentDetails;
              if (modalFor === 'replace') {
                documentDetails = {
                  filename: header.filename,
                  attributes:{
                    divisions:replaceRecord['attributes']['divisions'],
                    lastmodified: _file.lastModifiedDate,
                    filesize: _file.size
                  },
                  replacementof:replaceRecord['replacementof'] == null || replaceRecord['replacementof']==''? replaceRecord['recordid'] : replaceRecord['replacementof'] ,
                  s3uripath: header.filepathdb,
                  trigger: 'recordreplace',
                  service: 'deduplication'
                }
              } else if (modalFor === 'replaceattachment') {
                documentDetails = {
                  ...updateAttachment,
                  s3uripath: header.filepathdb,
                  trigger: 'recordreplace',
                  service: 'deduplication'
                }
              } else {
                documentDetails = {
                  s3uripath: header.filepathdb,
                  filename: header.filename,
                  attributes:{
                    divisions:[{divisionid: _fileInfo.divisionid}],
                    lastmodified: _file.lastModifiedDate,
                    filesize: _file.size
                  }
                }
              }
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
              await completeMultiPartUpload({uploadid: header.uploadid, filepath: header.filepathdb, parts: parts}, ministryId, 'records', bcgovcode, dispatch, (_err, _res) => {
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
              if (modalFor === 'replace' || modalFor == 'replaceattachment') {
                
                 if (modalFor === 'replaceattachment'){
                dispatch(retryFOIRecordProcessing(requestId, ministryId, {records: _documents},(err, _res) => {
                    dispatchRequestAttachment(err);
                })); }

                 if (modalFor === 'replace'){
                dispatch(replaceFOIRecordProcessing(requestId, ministryId,replaceRecord.recordid, {records: _documents},(err, _res) => {
                  dispatchRequestAttachment(err);
              })); }

              }                             
              else {
                dispatch(saveFOIRecords(requestId, ministryId, {records: _documents},(err, _res) => {
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
            setRecordsUploading(false)
          }
        })
      }
    }
  }

  const downloadDocument = (file, isPDF = false,originalfile = false) => {
    var s3filepath = !originalfile ? file.s3uripath: (!file.isattachment ? file.originalfile:file.s3uripath);
    var filename = !originalfile ? file.filename:(!file.isattachment ?file.originalfilename: file.filename);
    if (isPDF) {
      s3filepath = s3filepath.substr(0, s3filepath.lastIndexOf(".")) + ".pdf";
      filename = filename + ".pdf";
    }
    const toastID = toast.loading("Downloading file (0%)")
    getFOIS3DocumentPreSignedUrl(s3filepath.split('/').slice(4).join('/'), ministryId, dispatch, (err, res) => {
      if (!err) {
        getFileFromS3({filepath: res}, (_err, response) => {
          let blob = new Blob([response.data], {type: "application/octet-stream"});
          saveAs(blob, filename)
          toast.update(toastID, {
            render: _err ? "File download failed" : "Download complete",
            type: _err ? "error" : "success",
            className: "file-upload-toast",
            isLoading: false,
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            closeButton: true
          });
        }, (progressEvent) => {
          toast.update(toastID, {
            render: "Downloading file (" + Math.floor(progressEvent.loaded / progressEvent.total * 100) + "%)",
            isLoading: true,
          })
        });
      }
    }, 'records', bcgovcode);
  }  

  const handleDownloadChange = (e) => {
    //if clicked on harms
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
      downloadLinearHarmsDocuments()
    }
    //if clicked on harms and stitching is complete
    else if (e.target.value === 1 && pdfStitchStatus === "completed") {
      const s3filepath = pdfStitchedRecord?.finalpackagepath
      const filename = requestNumber + ".zip"
      try {
        downloadZipFile(s3filepath, filename);
      }
      catch (error) {
        console.log(error)
        toastError()
      }
    }
    setCurrentDownload(e.target.value); 
  }

  const downloadZipFile = async (s3filepath, filename) => {
      const toastID = toast.loading("Downloading file (0%)")
      const response = await getFOIS3DocumentPreSignedUrl(s3filepath.split('/').slice(4).join('/'), ministryId, dispatch, null, 'records', bcgovcode)
      await getFileFromS3({filepath: response.data}, (_err, res) => {
          let blob = new Blob([res.data], {type: "application/octet-stream"});
          saveAs(blob, filename)
          toast.update(toastID, {
            render: _err ? "File download failed" : "Download complete",
            type: _err ? "error" : "success",
            className: "file-upload-toast",
            isLoading: false,
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            closeButton: true
          });
        }, (progressEvent) => {
          toast.update(toastID, {
            render: "Downloading file (" + Math.floor(progressEvent.loaded / progressEvent.total * 100) + "%)",
            isLoading: true,
          })
        });
  }

  const downloadLinearHarmsDocuments = () => {
    try{
    
      const message = createMessageForHarms(recordsObj?.records);
      dispatch(triggerDownloadFOIRecordsForHarms(requestId, ministryId, message,(err, _res) => {
        if (err) {
          toastError()
        }
        else {
          setIsDownloadInProgress(true);      
          setIsDownloadReady(false);
          setIsDownloadFailed(false); 
        }
        dispatchRequestAttachment(err);
    }));

    } catch (error) {
      console.log(error)
      toastError()
    }

  }

  const createMessageForHarms = (recordList) => {
    
    const message = {
      "category":RecordDownloadCategory.harms,
      "requestnumber":requestNumber,
      "bcgovcode":bcgovcode,
      "attributes":[]
    };

    let exporting = removeDuplicateFiles(recordList);
    exporting = addDeduplicatedAttachmentsToRecords(exporting);

    // Create a map to group files by division
    const divisionMap = new Map();
 
    // Loop through each item in the input array
    for (const item of exporting) {
      // Get the division information from the item
      const divisions = item.attributes ? item.attributes.divisions : null;
      
      const [filepath, filename] = getPDFFilePath(item);
    
      // If the item has no division information, skip it
      if (!divisions) {
        continue;
      }
      // Loop through each division in the item
      for (const division of divisions) {
        // Get the division ID and name
        const divisionId = division.divisionid;
        const divisionName = division.divisionname.replace("'", "");
    
        // If the division is not already in the division map, add it
        if (!divisionMap.has(divisionId)) {
          divisionMap.set(divisionId, {
            divisionid: divisionId,
            divisionname: divisionName,
            files: [],
            divisionfilesize: 0
          });
        }
    
        // Add the item to the files array for this division
        const files = divisionMap.get(divisionId).files;
        const convertedFileSize = parseFloat(item.attributes?.convertedfilesize) || 0
        const fileSize = parseFloat(item.attributes?.filesize) || 0
        const fileAttrs = {
          lastmodified: item.attributes?.lastmodified,
          recordid: item.recordid,
          s3uripath: filepath,
          filename,
          filesize: convertedFileSize || fileSize
        };
        files.push(fileAttrs);
        divisionMap.get(divisionId).divisionfilesize += fileAttrs.filesize; // add file size to division total
      }
    }
 
    // Sort the divisions by lastmodified date and add them to the output object
    const sortedDivisions = sortDivisionalFiles(divisionMap);

    message.attributes = sortedDivisions;
    message.totalfilesize = calculateTotalFileSize(sortedDivisions); // calculate total size for whole message

    //keeping this for testing purpose.
    console.log(`message = ${JSON.stringify(message)}`);

    return message;

  } 


  const toastError = (error) => {
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
    setIsDownloadInProgress(false);      
    setIsDownloadReady(false);
    setIsDownloadFailed(true);

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
        if (record.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(record.attributes?.extension?.toLowerCase())) {
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
    record.service = record.failed ? record.failed : 'all';
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
        setreplaceRecord(_record)
        setModalFor("replace");
        setModal(true);
        break;
      case "replaceattachment":
        setreplaceRecord(_record)
        setModalFor("replaceattachment");
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
      case "downloadoriginal":
        downloadDocument(_record, false, true);
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

  const getreplacementfiletypes = () => {

    var replacefileextensions = [...MimeTypeList.recordsLog]

    let _filename = replaceRecord?.originalfilename === '' ? replaceRecord.filename : replaceRecord.originalfilename ;
    let fileextension =  _filename?.split('.').pop();
    
    switch(fileextension)
    {
      case "docx" || "doc":
        replacefileextensions = ["application/pdf" ,'application/vnd.openxmlformats-officedocument.wordprocessingml.document', "application/msword",'.doc', '.docx'];
        break;
      case "xlsx" || "xls":
        replacefileextensions = ["application/pdf" ,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel','.xls', '.xlsx'];
        break;
      case "msg" || "eml" :
        replacefileextensions = ["application/pdf" ,'.msg','.eml'];
          break;
      case "pdf" :
            replacefileextensions = ["application/pdf"];
              break;      
      default:
        replacefileextensions = [...MimeTypeList.recordsLog]
        break;
    }

    return replacefileextensions;
  }


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
          _filterValue === -2 ? !r.isredactionready && !r.attributes?.incompatible && (r.failed || isrecordtimeout(r.created_at, RECORD_PROCESSING_HRS) == true):
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
            <Grid item xs={5}>
              <h1 className="foi-review-request-text foi-ministry-requestheadertext foi-records-request-text">
                {getRequestNumber()}
              </h1>
            </Grid>
            <Grid item xs={7}>
              <span style={{float:'right', fontWeight:'bold'}}>
              <div style={{paddingBottom: '5px'}}>Total Uploaded Size : {getReadableFileSize(totalUploadedRecordSize)}</div>
              <div>Total Upload Limit : {getReadableFileSize(TOTAL_RECORDS_UPLOAD_LIMIT)}</div>
              </span>
            </Grid>
          </Grid>
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            spacing={1}
          >
            <ConditionalComponent condition={records.filter(record => record.attachments?.length > 0).length > 0}>
            <Grid item xs={3}>              
                <button
                  className="btn addAttachment foi-export-button"
                  variant="contained"
                  onClick={() => setDeleteModalOpen(true)}
                  color="primary"
                >
                  Remove Attachments
                </button>
              
            </Grid>
            </ConditionalComponent>
            <ConditionalComponent condition={hasDocumentsToDownload}>
            <Grid item xs={3}>
              
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
              {recordsDownloadList.map((item, index) => {

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
                          !item.disabled && (isDownloadReady ?
                          <FontAwesomeIcon icon={faCheckCircle} size='2x' color='#1B8103' className={classes.statusIcons}/>:
                          isDownloadFailed ?
                          <FontAwesomeIcon icon={faExclamationCircle} size='2x' color='#A0192F' className={classes.statusIcons}/>:
                          isDownloadInProgress ? <FontAwesomeIcon icon={faSpinner} size='2x' color='#FAA915' className={classes.statusIcons}/>:null) 
                        }
                        {item.label}
                      </MenuItem>
                    // </>
                  )
                }

              } )}
            </TextField>
             
            </Grid>
            </ConditionalComponent>
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
                (records.length > 0 && DISABLE_REDACT_WEBLINK?.toLowerCase() =='false' && <a href={DOC_REVIEWER_WEB_URL + "/foi/" + ministryId}>
                  <button
                    className={clsx("btn", "addAttachment", classes.createButton)}
                    variant="contained"
                    // onClick={}
                    color="primary"
                  >
                    Redact Records
                  </button>
                </a>)
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
                  <span>Duplicates Removed:</span>
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
                    id="foirecordsfilter"
                    placeholder="Filter Records ..."
                    defaultValue={""}
                    onChange={(e)=>{setSearchValue(e.target.value.trim())}}
                    sx={{
                      color: "#38598A",
                    }}
                    startAdornment={
                      <InputAdornment position="start">
                        <IconButton
                          aria-label="Search Icon"
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
            totalUploadedRecordSize={totalUploadedRecordSize}
            replacementfiletypes={getreplacementfiletypes()}
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
  const [isRetry, setRetry] = useState(false); 
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
            isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) == true && isRetry == false ?
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
              record.failed && record.isredactionready ?
              <span>Record Manually Replaced Due to Error</span>:
              record.isduplicate ?
              <span>Duplicate of {record.duplicateof}</span>:
              record.isredactionready ?
              <span>Ready for Redaction</span>:
              record.failed ?
              <span>Error during {record.failed}</span>:
              isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) == true && isRetry == false ?
              <span>Error due to timeout</span>:
              <span>Deduplication & file conversion in progress</span>
            }
            <AttachmentPopup
            indexValue={indexValue}
            record={record}
            handlePopupButtonClick={handlePopupButtonClick}
            disabled={disabled}
            ministryId={ministryId}
            setRetry={setRetry}
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

const AttachmentPopup = React.memo(({indexValue, record, handlePopupButtonClick, disabled,ministryId, setRetry}) => {
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

  const handleReplaceAttachment = () => {
    closeTooltip();
    handlePopupButtonClick("replaceattachment", record);
  }

  const handleDownload = () =>{
    closeTooltip();
    handlePopupButtonClick("download", record);
  }

  const handleDownloadPDF = () =>{
    closeTooltip();
    handlePopupButtonClick("downloadPDF", record);
  }

  const handleDownloadoriginal = () =>{
    closeTooltip();
    handlePopupButtonClick("downloadoriginal", record);
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
    setRetry(true)
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
          { (!record.attributes?.isattachment || record.attributes?.isattachment  === undefined) && <MenuItem
            onClick={() => {
                handleReplace();
                setPopoverOpen(false);
            }}
          >
            Replace Manually
          </MenuItem>}
          { record.attributes?.isattachment && <MenuItem
            onClick={() => {
                 handleReplaceAttachment() 
                setPopoverOpen(false);
            }}
          >
            Replace Attachment
          </MenuItem>}
          {record.originalfile!=''  && record.originalfile!=undefined  && <MenuItem
            onClick={() => {
                handleDownloadoriginal();
                setPopoverOpen(false);
            }}
          >
            Download Original
          </MenuItem>
          }
          {record.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(record.attributes?.extension?.toLowerCase()) && <MenuItem
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
           {record.originalfile!='' && record.originalfile!=undefined ? "Download Replaced" : record.attributes?.isattachment ? "Download Original" : "Download" }
          </MenuItem>
          {!record.isattachment && <DeleteMenu />}
          {!record.isredactionready && (record.failed || isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) == true) && <MenuItem
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