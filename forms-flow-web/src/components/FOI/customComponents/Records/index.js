import React, { useEffect, useState } from "react";
import "../Attachments/attachments.scss";
import "./records.scss";
import { useDispatch, useSelector } from "react-redux";
import AttachmentModal from "../Attachments/AttachmentModal";
import Loading from "../../../../containers/Loading";
import {
  getOSSHeaderDetails,
  saveFilesinS3,
  getFileFromS3,
  postFOIS3DocumentPreSignedUrl,
  getFOIS3DocumentPreSignedUrl,
  completeMultiPartUpload,
} from "../../../../apiManager/services/FOI/foiOSSServices";
import {
  saveFOIRequestAttachmentsList,
  replaceFOIRequestAttachment,
  saveNewFilename,
  deleteFOIRequestAttachment,
} from "../../../../apiManager/services/FOI/foiAttachmentServices";
import {
  fetchFOIRecords,
  saveFOIRecords,
  updateFOIRecords,
  retryFOIRecordProcessing,
  replaceFOIRecordProcessing,
  deleteReviewerRecords,
  getRecordFormats,
  triggerDownloadFOIRecordsForHarms,
  fetchPDFStitchedRecordForHarms,
  fetchPDFStitchedRecordForRedlines,
  fetchPDFStitchedRecordForResponsePackage,
  fetchPDFStitchedRecordForOIPCRedline,
  fetchPDFStitchedRecordForOIPCRedlineReview,
  checkForRecordsChange,
  fetchPDFStitchedRecordForConsults,
  editPersonalAttributes,
  updateUserLockedRecords,
  fetchPDFStitchedRecordsForPhasedRedlines,
  fetchPDFStitchedRecordsForPhasedResponsePackages,
  retrieveSelectedRecordVersion
} from "../../../../apiManager/services/FOI/foiRecordServices";
import {
  saveRequestDetails,
  openRequestDetails,
  updateSpecificRequestSection,
} from "../../../../apiManager/services/FOI/foiRequestServices";
import {
  StateTransitionCategories,
  AttachmentCategories,
} from "../../../../constants/FOI/statusEnum";
import {
  RecordsDownloadList,
  RecordDownloadCategory,
  MimeTypeList,
  RecordDownloadStatus,
} from "../../../../constants/FOI/enum";
import {
  addToFullnameList,
  getFullnameList,
  ConditionalComponent,
  isrecordtimeout,
  isMinistryCoordinator,
} from "../../../../helper/FOI/helper";
import Grid from "@material-ui/core/Grid";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";
import Chip from "@material-ui/core/Chip";
import Divider from "@material-ui/core/Divider";
import Popover from "@material-ui/core/Popover";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import IconButton from "@material-ui/core/IconButton";
import MenuList from "@material-ui/core/MenuList";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@mui/material/TextField";
import { saveAs } from "file-saver";
import { downloadZip } from "client-zip";
import { ClickableChip } from "../../Dashboard/utils";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import Paper from "@mui/material/Paper";
import Tooltip from "@mui/material/Tooltip";
import { toast } from "react-toastify";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCheckCircle,
  faClone,
} from "@fortawesome/free-regular-svg-icons";
import {
  faSpinner,
  faExclamationCircle,
  faBan,
  faArrowTurnUp,
  faTrash,
  faPenToSquare,
  faLinkSlash,
  faDownload,
  faMinimize,
  faMaximize,
  faMagnifyingGlass,
  faRotate,
} from "@fortawesome/free-solid-svg-icons";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import CloseIcon from "@material-ui/icons/Close";
import _ from "lodash";
import {
  DOC_REVIEWER_WEB_URL,
  RECORD_PROCESSING_HRS,
  OSS_S3_CHUNK_SIZE,
  DISABLE_REDACT_WEBLINK,
  RECORD_DOWNLOAD_LIMIT,
  RECORD_DOWNLOAD_SIZE_LIMIT
} from "../../../../constants/constants";
import {
  removeDuplicateFiles,
  getUpdatedRecords,
  sortByLastModified,
  getFiles,
  calculateDivisionFileSize,
  calculateTotalFileSize,
  calculateTotalUploadedFileSizeInKB,
  getReadableFileSize,
} from "./util";
import { readUploadedFileAsBytes } from "../../../../helper/FOI/helper";
import { TOTAL_RECORDS_UPLOAD_LIMIT } from "../../../../constants/constants";
import { isScanningTeam } from "../../../../helper/FOI/helper";
import { MinistryNeedsScanning } from "../../../../constants/FOI/enum";
//import {convertBytesToMB} from "../../../../components/FOI/customComponents/FileUpload/util";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import MCFPersonal from "./MCFPersonal";
import MSDPersonal from "./MSDPersonal";
import PhaseMenu from "./PhaseMenu";

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
    marginTop: "1em",
  },
  heading: {
    color: "#FFF",
    fontSize: "16px !important",
    fontWeight: "bold !important",
    flexDirection: "row-reverse",
  },
  actions: {
    textAlign: "right",
  },
  createDate: {
    fontStyle: "italic",
    fontSize: "14px",
  },
  createBy: {
    fontStyle: "italic",
    fontSize: "14px",
    display: "flex",
  },
  filename: {
    fontWeight: "bold",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    maxWidth: "79%",
  },
  divider: {
    marginTop: "-2px",
    marginBottom: "-5px",
  },
  topDivider: {
    paddingTop: "0px !important",
  },
  recordStatus: {
    fontSize: "12px",
    color: "#a7a1a1",
    display: "flex",
  },
  statusIcons: {
    height: "20px",
    paddingRight: "10px",
  },
  attachmentIcon: {
    height: "20px",
    margin: "0 15px",
    rotate: "90deg",
  },
  recordReports: {
    marginTop: "1em",
    fontSize: "14px",
    marginBottom: "0px",
    marginLeft: "15px",
    fontWeight: "bold",
  },
  fileSize: {
    paddingLeft: "20px",
  },
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
  setRecordsUploading,
  recordsTabSelect,
  requestType,
  handleSaveRequest,
  isHistoricalRequest,
  lockRecords,
  setLockRecordsTab,
  validLockRecordsState,
  setSaveRequestObject,
  isPhasedRelease
}) => {
  const user = useSelector((state) => state.user.userDetail);
  const userGroups = user?.groups?.map((group) => group.slice(1));

  let recordsObj = useSelector((state) => state.foiRequests.foiRequestRecords);

  let pdfStitchStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForHarms
  );
  let redlinePdfStitchStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForRedlines
  );
  let oipcRedlineReviewPdfStitchedStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForOipcRedlineReview
  );
  let oipcRedlinePdfStitchedStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForOipcRedline
  );
  let responsePackagePdfStitchStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForResponsePackage
  );
  let consultPDFStitchedStatus = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusForConsults
  );
  let phasedRedlinesStitchedStatuses = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusesForPhasedRedlines
  );
  let phasedResponsePackageStitchedStatuses = useSelector(
    (state) => state.foiRequests.foiPDFStitchStatusesForPhasedResponsePackages
  );

  let pdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForHarms
  );
  let redlinePdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForRedlines
  );
  let oipcRedlineReviewPdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForOipcRedlineReview
  );
  let oipcRedlinePdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForOipcRedline
  );
  let responsePackagePdfStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForResponsePackage
  );
  let consultPDFStitchedRecord = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordForConsultPackage
  );
  let phasedRedlinesStitchedRecords = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordsForPhasedRedlines
  );
  let phasedResponsePackageStitchedRecords = useSelector(
    (state) => state.foiRequests.foiPDFStitchedRecordsForPhasedResponsePackages
  );

  let isRecordsfetching = useSelector(
    (state) => state.foiRequests.isRecordsLoading
  );

  let requestDetails = useSelector(
    (state) => state.foiRequests.foiRequestDetail
  );

  const tagList = divisions?.filter((d) => d.divisionname.toLowerCase() !== "communications")
    .map((division) => {
      return {
        name: division.divisionid,
        display: division.divisionname,
      };
    });

  const classes = useStyles();
  const [records, setRecords] = useState(recordsObj?.records);
  const [estimatedPageCount, setEstimatedPageCount] = useState(0);
  const [estimatedTaggedPageCount, setEstimatedTaggedPageCount] = useState(0);
  const [totalUploadedRecordSize, setTotalUploadedRecordSize] = useState(0);
  const [isScanningTeamMember, setIsScanningTeamMember] = useState(
    isScanningTeam(userGroups)
  );
  const [ministryCode, setMinistryCode] = useState(
    bcgovcode.replaceAll('"', "").toUpperCase()
  );
  const [isMCFPersonal, setIsMCFPersonal] = useState(
    ministryCode == "MCF" &&
      requestType === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL
  );
  useEffect(() => {
    setRecords(recordsObj?.records);
    let nonDuplicateRecords = recordsObj?.records?.filter(
      (record) => !record.isduplicate
    );
    let totalUploadedSize =
      calculateTotalUploadedFileSizeInKB(nonDuplicateRecords) / (1024 * 1024);
    setTotalUploadedRecordSize(parseFloat(totalUploadedSize.toFixed(4)));
    dispatch(checkForRecordsChange(requestId, ministryId));
    //To manage enabling and disabling of download for harms package
    recordsDownloadList[1].disabled = enableHarmsDonwnload();
    // isDisableRedactRecords(recordsObj?.records)
  }, [recordsObj]);

  useEffect(() => {
    dispatch(getRecordFormats());

    
    //Filter out download consults option from RecordsDownloadList if ministry user
    if (isMinistryCoordinator) {
      setRecordsDownloadList(recordsDownloadList.filter((record) => record.id !== 6));
    }
  }, []);

  const isDisableRedactRecords = (allRecords) => {
    return allRecords.some(record =>
      !record.isredactionready && !record.attributes.incompatible && 
        !record.selectedfileprocessversion && !record.ocrfilepath
      // || (!record.attributes.incompatible && !record.iscompressed &&
      //   (record.selectedfileprocessversion !== 1 || !record.selectedfileprocessversion))
        
    );
  };
  

  const [currentEditRecord, setCurrentEditRecord] = useState();
  const [editTagModalOpen, setEditTagModalOpen] = useState(false);
  const [curPersonalAttributes, setCurPersonalAttributes] = useState({
    person: "",
    filetype: "",
    volume: "",
    trackingid: "",
    personaltag: "TBD"
  });
  const [newPersonalAttributes, setNewPersonalAttributes] = useState();

  useEffect(() => {
    if(currentEditRecord?.attributes?.personalattributes)
      setCurPersonalAttributes(currentEditRecord.attributes.personalattributes);
  },[currentEditRecord])
  
  const MCFPeople = useSelector(
    (state) => state.foiRequests.foiPersonalPeople
  );
  const MCFFiletypes = useSelector(
    (state) => state.foiRequests.foiPersonalFiletypes
  );
  const MCFVolumes = useSelector(
    (state) => state.foiRequests.foiPersonalVolumes
  );
  const MCFSections = useSelector(
    (state) => state.foiRequests.foiPersonalSections
  );
  const [personFilters, setPersonFilters] = useState([]);
  const [fileTypeFilters, setFileTypeFilters] = useState([]);
  const [volumeFilters, setVolumeFilters] = useState([]);
  const [personalTagFilters, setPersonalTagFilters] = useState([]);
  useEffect(() => {
    let _personFilters = [];
    let _fileTypeFilters = [];
    let _volumeFilters = [];
    let _personalTagFilters = []
    if(recordsObj?.records?.length > 0) {
      recordsObj.records.forEach((record) => {
        if(record.attributes?.personalattributes?.person && MCFPeople?.people) {
          if(_personFilters.filter((p)=>{return p.name === record.attributes.personalattributes.person}).length === 0) {
            _personFilters = _personFilters.concat(MCFPeople.people.filter((p)=>{return p.name === record.attributes.personalattributes.person}));
          }
        }
        if(record.attributes?.personalattributes?.filetype && MCFFiletypes?.filetypes) {
          if(_fileTypeFilters.filter((ft)=>{return ft.name === record.attributes.personalattributes.filetype}).length === 0) {
            _fileTypeFilters = _fileTypeFilters.concat(MCFFiletypes.filetypes.filter((ft)=>{return ft.name === record.attributes.personalattributes.filetype}));
          }
        }
        if(record.attributes?.personalattributes?.volume && MCFVolumes?.volumes) {
          if(_volumeFilters.filter((v)=>{return v.name === record.attributes.personalattributes.volume}).length === 0) {
            _volumeFilters = _volumeFilters.concat(MCFVolumes.volumes.filter((v)=>{return v.name === record.attributes.personalattributes.volume}));
          }
        }
        if(record.attributes?.personalattributes?.personaltag && MCFSections?.sections) {
          if(_personalTagFilters.filter((pt)=>{return pt.name === record.attributes.personalattributes.personaltag}).length === 0) {
            _personalTagFilters = _personalTagFilters.concat(MCFSections.sections.filter((d)=>{return d.name === record.attributes.personalattributes.personaltag}));
          }
        }
      });
    }
    setPersonFilters(_personFilters.sort((a, b)=>a.sortorder-b.sortorder));
    setFileTypeFilters(_fileTypeFilters.sort((a, b)=>a.sortorder-b.sortorder));
    setVolumeFilters(_volumeFilters.sort((a, b)=>a.sortorder-b.sortorder));
    setPersonalTagFilters(_personalTagFilters.sort((a, b)=>a.sortorder-b.sortorder));
  }, [recordsObj, MCFPeople, MCFFiletypes, MCFVolumes, MCFSections]);
  
  useEffect(() => {
    setEstimatedPageCount(requestDetails.estimatedpagecount)
    setEstimatedTaggedPageCount(requestDetails.estimatedtaggedpagecount)
  }, [requestDetails]);

  const conversionFormats = useSelector(
    (state) => state.foiRequests.conversionFormats
  );

  useEffect(() => {
    if (recordsTabSelect && conversionFormats?.length < 1) {
      toast.error(
        "Temporarily unable to save your request. Please try again in a few minutes.",
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
  }, [recordsTabSelect, conversionFormats]);

  const divisionFilters = [
    ...personFilters.map((p)=>{p.divisionname=p.name; p.type='person'; return p;}),
    ...fileTypeFilters.map((ft)=>{ft.divisionname=ft.name; ft.type='filetype'; return ft;}),
    ...volumeFilters.map((v)=>{v.divisionname=v.name; v.type='volume'; return v;}),
    ...personalTagFilters.map((pt)=>{pt.divisionname=pt.name; pt.type='personaltag'; return pt;}),
    ...new Map(
      recordsObj?.records?.reduce(
        (acc, file) => [
          ...acc,
          ...new Map(
            file?.attributes?.divisions?.filter(
              (division) => division.divisionname != "TBD"
            ).map((division) => [
              division?.divisionid,
              division,
            ])
          ),
        ],
        []
      )
    ).values(),
  ];
  
  if (divisionFilters?.length > 0)
    divisionFilters?.push(
      { divisionid: -1, divisionname: "All" },
      { divisionid: -2, divisionname: "Errors" },
      { divisionid: -3, divisionname: "Incompatible" }
    );

  const [openModal, setModal] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [divisionsModalOpen, setDivisionsModalOpen] = useState(false);
  const [divisionModalTagValue, setDivisionModalTagValue] = useState(-1);
  const dispatch = useDispatch();
  const [isAttachmentLoading, setAttachmentLoading] = useState(false);
  const [isRecordsLoading, setRecordsLoading] = useState(false);
  const [multipleFiles, setMultipleFiles] = useState(true);
  const [modalFor, setModalFor] = useState("add");
  const [replaceRecord, setreplaceRecord] = useState({});
  const [updateAttachment, setUpdateAttachment] = useState({});
  const [searchValue, setSearchValue] = useState("");
  const [filterValue, setFilterValue] = useState(-1);
  const [filterText, setFilterText] = useState("");
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const [recordsDownloadList, setRecordsDownloadList] =
    useState(RecordsDownloadList);
  const [currentDownload, setCurrentDownload] = useState(0);
  const [isDownloadInProgress, setIsDownloadInProgress] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [isDownloadFailed, setIsDownloadFailed] = useState(false);
  const [isRedlineDownloadInProgress, setIsRedlineDownloadInProgress] =
    useState(false);
  const [isRedlineDownloadReady, setIsRedlineDownloadReady] = useState(false);
  const [isRedlineDownloadFailed, setIsRedlineDownloadFailed] = useState(false);
  const [
    isResponsePackageDownloadInProgress,
    setIsResponsePackageDownloadInProgress,
  ] = useState(false);
  const [isResponsePackageDownloadReady, setIsResponsePackageDownloadReady] =
    useState(false);
  const [isResponsePackageDownloadFailed, setIsResponsePackageDownloadFailed] =
    useState(false);
  const [isOIPCRedlineReviewReady, setIsOIPCRedlineReviewReady] =
    useState(false);
  const [isOIPCRedlineReviewFailed, setIsOIPCRedlineReviewFailed] =
    useState(false);
  const [isOIPCRedlineReviewInProgress, setIsOIPCRedlineReviewInProgress] =
    useState(false);
  const [isOIPCRedlineReady, setIsOIPCRedlineReady] =
    useState(false);
  const [isOIPCRedlineFailed, setIsOIPCRedlineFailed] =
    useState(false);
  const [isOIPCRedlineInProgress, setIsOIPCRedlineInProgress] =
    useState(false);

  const [isConsultDownloadInProgress, setIsConsultDownloadInProgress] = useState(false);
  const [isConsultDownloadReady, setIsConsultDownloadReady] = useState(false);
  const [isConsultDownloadFailed, setIsConsultDownloadFailed] = useState(false);

  const [phasedRedlineDownloadStatuses, setPhasedRedlineDownloadStatuses] = useState([]);
  const [phasedResponsePackageDownloadStatuses, setPhasedResponsePackageDownloadStatuses] = useState([]);

  const [isAllSelected, setIsAllSelected] = useState(false);

  useEffect(() => {
    const updateStatus = (
      status,
      setIsInProgress,
      setIsReady,
      setIsFailed,
      dispatchAction
    ) => {
      switch (status) {
        case RecordDownloadStatus.started:
        case RecordDownloadStatus.pushedtostream:
        case RecordDownloadStatus.redactionsummarystarted:
        case RecordDownloadStatus.redactionsummaryuploaded:
        case RecordDownloadStatus.zippingstarted:
        case RecordDownloadStatus.zippingcompleted:
          setIsInProgress(true);
          setIsReady(false);
          setIsFailed(false);
          break;
        case RecordDownloadStatus.completed:
          dispatch(dispatchAction(requestId, ministryId));
          setIsInProgress(false);
          setIsReady(true);
          setIsFailed(false);
          break;
        case RecordDownloadStatus.error:
          setIsInProgress(false);
          setIsReady(false);
          setIsFailed(true);
          break;
        default:
          setIsInProgress(false);
          setIsReady(false);
          setIsFailed(false);
          break;
      }
    };

    const updatePhasePackageStatus = (statuses, setStatuses, dispatchAction) => {
      if (statuses?.length > 0) {
        let newArr = [...statuses];
        for (let phaseObj of newArr) {
          switch (phaseObj.status) {
            case RecordDownloadStatus.started:
            case RecordDownloadStatus.pushedtostream:
            case RecordDownloadStatus.redactionsummarystarted:
            case RecordDownloadStatus.redactionsummaryuploaded:
            case RecordDownloadStatus.zippingstarted:
            case RecordDownloadStatus.zippingcompleted:
              phaseObj.downloadReady = false;
              phaseObj.downloadWIP = true;
              phaseObj.downloadFailed = false;
              break;
            case RecordDownloadStatus.completed:
              dispatch(dispatchAction(requestId, ministryId));
              phaseObj.downloadReady = true;
              phaseObj.downloadWIP = false;
              phaseObj.downloadFailed = false;
              break;
            case RecordDownloadStatus.error:
              phaseObj.downloadReady = false;
              phaseObj.downloadWIP = false;
              phaseObj.downloadFailed = true;
              break;
            default:
              phaseObj.downloadReady = false;
              phaseObj.downloadWIP = false;
              phaseObj.downloadFailed = false;
              break;
          }
        }
        setStatuses(newArr)
      }
    }

    // Update PDF Stitch Status
    updateStatus(
      pdfStitchStatus,
      setIsDownloadInProgress,
      setIsDownloadReady,
      setIsDownloadFailed,
      fetchPDFStitchedRecordForHarms
    );
    // Update Redline PDF Stitch Status
    updateStatus(
      redlinePdfStitchStatus,
      setIsRedlineDownloadInProgress,
      setIsRedlineDownloadReady,
      setIsRedlineDownloadFailed,
      fetchPDFStitchedRecordForRedlines
    );

    // Update Response Package PDF Stitch Status
    updateStatus(
      responsePackagePdfStitchStatus,
      setIsResponsePackageDownloadInProgress,
      setIsResponsePackageDownloadReady,
      setIsResponsePackageDownloadFailed,
      fetchPDFStitchedRecordForResponsePackage
    );

    // Update OIPC Review Package PDF Stitch Status
    updateStatus(
      oipcRedlineReviewPdfStitchedStatus,
      setIsOIPCRedlineReviewInProgress,
      setIsOIPCRedlineReviewReady,
      setIsOIPCRedlineReviewFailed,
      fetchPDFStitchedRecordForOIPCRedlineReview
    );
    // Update Redline OIPC PDF Stitch Status
    updateStatus(
      oipcRedlinePdfStitchedStatus,
      setIsOIPCRedlineInProgress,
      setIsOIPCRedlineReady,
      setIsOIPCRedlineFailed,
      fetchPDFStitchedRecordForOIPCRedline
    );
    // Update Consult Stitch Status
    updateStatus(
      consultPDFStitchedStatus,
      setIsConsultDownloadInProgress,
      setIsConsultDownloadReady,
      setIsConsultDownloadFailed,
      fetchPDFStitchedRecordForConsults
    );
    updatePhasePackageStatus(
      phasedRedlinesStitchedStatuses,
      setPhasedRedlineDownloadStatuses,
      fetchPDFStitchedRecordsForPhasedRedlines,
    )
    updatePhasePackageStatus(
      phasedResponsePackageStitchedStatuses,
      setPhasedResponsePackageDownloadStatuses,
      fetchPDFStitchedRecordsForPhasedResponsePackages
    )
  }, [
    pdfStitchStatus,
    redlinePdfStitchStatus,
    responsePackagePdfStitchStatus,
    oipcRedlinePdfStitchedStatus,
    oipcRedlineReviewPdfStitchedStatus,
    consultPDFStitchedStatus,
    requestId,
    ministryId,
    phasedRedlinesStitchedStatuses,
    phasedResponsePackageStitchedStatuses,
  ]);

  useEffect(() => {
    recordsDownloadList.map((item) => {
      if (item.id === 2 && isRedlineDownloadReady) {
        item.disabled = false;
      }
      if (item.id === 3 && isResponsePackageDownloadReady) {
        item.disabled = false;
      }
      if (item.id === 4 && isOIPCRedlineReady) {
        item.disabled = false;
      }
      if (item.id === 5 && isOIPCRedlineReviewReady) {
        item.disabled = false;
      }
      if (item.id === 6 && isConsultDownloadReady) {
        item.disabled = false;
      }
    });
  }, [isRedlineDownloadReady, isResponsePackageDownloadReady, isOIPCRedlineReady, isOIPCRedlineReviewReady, isConsultDownloadReady]);

  const addAttachments = () => {
    setModalFor("add");
    setMultipleFiles(true);
    setUpdateAttachment({});
    setModal(true);
  };

  const dispatchRequestAttachment = (err) => {
    if (!err) {
      setAttachmentLoading(false);
      dispatch(fetchFOIRecords(requestId, ministryId));
    }
  };

  const handleContinueModal = (value, fileInfoList, files) => {
    setModal(false);
    if (modalFor === "delete" && value) {
      var deleteRecords = [];
      var deleteAttachemnts = [];
      if (updateAttachment) {
        deleteRecords.push(
          (({ recordid, documentmasterid, s3uripath }) => ({
            recordid,
            documentmasterid,
            filepath: s3uripath,
          }))(updateAttachment)
        );
      } else {
        for (let record of records) {
          if (record.isselected) {
            deleteRecords.push(
              (({ recordid, documentmasterid, s3uripath }) => ({
                recordid,
                documentmasterid,
                filepath: s3uripath,
              }))(record)
            );
          } else {
            if (record?.attachments) {
              for (let attachment of record.attachments) {
                if (attachment.isselected) {
                  deleteAttachemnts.push(attachment.filepath);
                }
              }
            }
          }
        }
      }
      if (deleteRecords.length > 0) {
        dispatch(
          updateFOIRecords(
            requestId,
            ministryId,
            { records: deleteRecords, isdelete: true },
            (err, _res) => {
              dispatchRequestAttachment(err);
            }
          )
        );
      }
      if (deleteAttachemnts.length > 0) {
        dispatch(
          deleteReviewerRecords(
            { filepaths: deleteAttachemnts, ministryrequestid: ministryId },
            (err, _res) => {
              dispatchRequestAttachment(err);
            }
          )
        );
      }
    } else if (files) {
      saveDocument(value, fileInfoList, files);
    }
  };

  const saveDocument = (value, fileInfoList, files) => {
    if (value) {
      if (files.length !== 0) {
        setRecordsUploading(true);
        if (modalFor === "replaceattachment") {
          fileInfoList[0].filepath =
            updateAttachment.s3uripath.substr(
              0,
              updateAttachment.s3uripath.lastIndexOf(".")
            ) + ".pdf";
        }
        postFOIS3DocumentPreSignedUrl(
          ministryId,
          fileInfoList.map((file) => ({ ...file, multipart: true })),
          "records",
          bcgovcode,
          dispatch,
          async (err, res) => {
            let _documents = [];
            if (!err) {
              var completed = 0;
              let failed = [];
              const toastID = toast.loading(
                "Uploading files (" +
                  completed +
                  "/" +
                  fileInfoList.length +
                  ")"
              );
              for (let header of res) {
                const _file = files.find(
                  (file) => file.filename === header.filename
                );
                const _fileInfo = fileInfoList.find(
                  (fileInfo) => fileInfo.filename === header.filename
                );
                var documentDetails;
                if (modalFor === "replace") {
                  documentDetails = {
                    filename: header.filename,
                    attributes: {
                      divisions: replaceRecord["attributes"]["divisions"],
                      lastmodified: _file.lastModifiedDate
                        ? _file.lastModifiedDate
                        : new Date(_file.lastModified),
                      filesize: _file.size,
                      personalattributes: _fileInfo.personalattributes,
                    },
                    replacementof:
                      replaceRecord["replacementof"] == null ||
                      replaceRecord["replacementof"] == ""
                        ? replaceRecord["recordid"]
                        : replaceRecord["replacementof"],
                    s3uripath: header.filepathdb,
                    trigger: "recordreplace",
                    service: "deduplication",
                  };
                } else if (modalFor === "replaceattachment") {
                  documentDetails = {
                    ...updateAttachment,
                    s3uripath: header.filepathdb,
                    trigger: "recordreplace",
                    service: "deduplication",
                  };
                  documentDetails.attributes.convertedfilesize = _file.size;
                  documentDetails.attributes.trigger = "recordreplace";
                  delete documentDetails.outputdocumentmasterid;
                } else {
                  documentDetails = {
                    s3uripath: header.filepathdb,
                    filename: header.filename,
                    attributes: {
                      divisions: [{ divisionid: _fileInfo.divisionid }],
                      lastmodified: _file.lastModifiedDate
                        ? _file.lastModifiedDate
                        : new Date(_file.lastModified),
                      filesize: _file.size,
                      personalattributes: _fileInfo.personalattributes,
                    },
                  };
                }
                let bytes = await readUploadedFileAsBytes(_file);
                const CHUNK_SIZE = OSS_S3_CHUNK_SIZE;
                const totalChunks = Math.ceil(bytes.byteLength / CHUNK_SIZE);
                let parts = [];
                for (let chunk = 0; chunk < totalChunks; chunk++) {
                  let CHUNK = bytes.slice(
                    chunk * CHUNK_SIZE,
                    (chunk + 1) * CHUNK_SIZE
                  );
                  let response = await saveFilesinS3(
                    { filepath: header.filepaths[chunk] },
                    CHUNK,
                    dispatch,
                    (_err, _res) => {
                      if (_err) {
                        failed.push(header.filename);
                      }
                    }
                  );
                  if (response.status === 200) {
                    parts.push({
                      PartNumber: chunk + 1,
                      ETag: response.headers.etag,
                    });
                  } else {
                    failed.push(header.filename);
                  }
                }
                await completeMultiPartUpload(
                  {
                    uploadid: header.uploadid,
                    filepath: header.filepathdb,
                    parts: parts,
                  },
                  ministryId,
                  "records",
                  bcgovcode,
                  dispatch,
                  (_err, _res) => {
                    if (!_err && _res.ResponseMetadata.HTTPStatusCode === 200) {
                      completed++;
                      toast.update(toastID, {
                        render:
                          "Uploading files (" +
                          completed +
                          "/" +
                          fileInfoList.length +
                          ")",
                        isLoading: true,
                      });
                      _documents.push(documentDetails);
                    } else {
                      failed.push(header.filename);
                    }
                  }
                );
              }
              if (_documents.length > 0) {
                if (modalFor === "replace" || modalFor == "replaceattachment") {
                  if (modalFor === "replaceattachment") {
                    dispatch(
                      retryFOIRecordProcessing(
                        requestId,
                        ministryId,
                        { records: _documents },
                        (err, _res) => {
                          dispatchRequestAttachment(err);
                        }
                      )
                    );
                  }

                  if (modalFor === "replace") {
                    dispatch(
                      replaceFOIRecordProcessing(
                        requestId,
                        ministryId,
                        replaceRecord.recordid,
                        { records: _documents },
                        (err, _res) => {
                          dispatchRequestAttachment(err);
                        }
                      )
                    );
                  }
                } else {
                  dispatch(
                    saveFOIRecords(
                      requestId,
                      ministryId,
                      { records: _documents },
                      (err, _res) => {
                        dispatchRequestAttachment(err);
                      }
                    )
                  );
                }
              }
              var toastOptions = {
                render:
                  failed.length > 0
                    ? "The following " +
                      failed.length +
                      " file uploads failed\n- " +
                      failed.join("\n- ")
                    : fileInfoList.length + " Files successfully saved",
                type: failed.length > 0 ? "error" : "success",
              };
              toast.update(toastID, {
                ...toastOptions,
                className: "file-upload-toast",
                isLoading: false,
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                closeButton: true,
              });
              setRecordsUploading(false);
            }
          }
        );
      }
    }
  };

  const downloadDocument = (file, isPDF = false, originalfile = false) => {
    var filePath = ('ocrfilepath' in file && file.ocrfilepath != null)? file.ocrfilepath : ('compresseds3uripath' in file && file.compresseds3uripath != null)? 
          file.compresseds3uripath : file.s3uripath
    var s3filepath = !originalfile
      ? filePath
      : !file.isattachment
      ? file.originalfile
      : filePath;
    var filename = !originalfile
      ? file.filename
      : !file.isattachment
      ? file.originalfilename
      : file.filename;
    if (isPDF) {
      s3filepath = s3filepath.substr(0, s3filepath.lastIndexOf(".")) + ".pdf";
      filename = filename + ".pdf";
    }
    const toastID = toast.loading("Downloading file (0%)");
    getFOIS3DocumentPreSignedUrl(
      s3filepath.split("/").slice(4).join("/"),
      ministryId,
      dispatch,
      (err, res) => {
        if (!err) {
          getFileFromS3(
            { filepath: res },
            (_err, response) => {
              let blob = new Blob([response.data], {
                type: "application/octet-stream",
              });
              saveAs(blob, filename);
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
                closeButton: true,
              });
            },
            (progressEvent) => {
              toast.update(toastID, {
                render:
                  "Downloading file (" +
                  Math.floor(
                    (progressEvent.loaded / progressEvent.total) * 100
                  ) +
                  "%)",
                isLoading: true,
              });
            }
          );
        }
      },
      isHistoricalRequest ? "historical" : "records",      
      isHistoricalRequest ? undefined : bcgovcode
    );
  };

    const handlePhasePackageDownload = (packageObj, itemid) => {
      const phasedDownloadStatuses = itemid === 2 ? phasedRedlineDownloadStatuses : phasedResponsePackageDownloadStatuses;
      const phasedStichedRecords = itemid === 2 ? phasedRedlinesStitchedRecords : phasedResponsePackageStitchedRecords;
      const packageName = `${packageObj.category}phase${packageObj.phase}`;
      const isDownloadReady = phasedDownloadStatuses?.find(phasedPackage => phasedPackage.phase === packageObj.phase).downloadReady;
      if (isDownloadReady) {
        const s3filepath = phasedStichedRecords?.find(phasedPackage => packageName === phasedPackage.category).finalpackagepath;
        handleDownloadZipFile(s3filepath, packageObj);
      }
    }
    const handleDownloadChange = (e) => {
    //if clicked on harms
    if (
      e.target.value === 1 &&
      [RecordDownloadStatus.notstarted, RecordDownloadStatus.error].includes(
        pdfStitchStatus
      )
    ) {
      toast.info(
        "In progress. You will be notified when the records are ready for download.",
        {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: "colored",
          backgroundColor: "#FFA500",
        }
      );
      downloadLinearHarmsDocuments();
    } else if (e.target.value === 1 && isDownloadReady) {
      //if clicked on harms and stitching is complete
      const s3filepath = pdfStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    } else if (e.target.value === 2 && isRedlineDownloadReady) {
      const s3filepath = redlinePdfStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    } else if (e.target.value === 3 && isResponsePackageDownloadReady) {
      const s3filepath = responsePackagePdfStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    } else if (e.target.value === 4 && isOIPCRedlineReady) {
      const s3filepath = oipcRedlinePdfStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    } else if (e.target.value === 5 && isOIPCRedlineReviewReady) {
      const s3filepath = oipcRedlineReviewPdfStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    } else if (e.target.value === 6 && isConsultDownloadReady) {
      const s3filepath = consultPDFStitchedRecord?.finalpackagepath;
      handleDownloadZipFile(s3filepath, e.target.value);
    }

    setCurrentDownload(e.target.value);
  };

  const handleDownloadZipFile = (s3filepath, packageid) => {
    const filename = requestNumber + ".zip";
    try {
      downloadZipFile(s3filepath, filename);
    } catch (error) {
      console.log(error);
      if (isPhasedRelease) {
        phasedReleaseToastError(packageid)
      }
      else {
        toastError(packageid);
      }
    }
  };

  const downloadZipFile = (s3filepath, filename) => {
    const toastID = toast.loading("Downloading file (0%)");
    getFOIS3DocumentPreSignedUrl(
      s3filepath.split("/").slice(4).join("/"),
      ministryId,
      dispatch,
      (err, res) => {
        if (!err) {
          getFileFromS3(
            { filepath: res },
            (_err, response) => {
              let blob = new Blob([response.data], {
                type: "application/octet-stream",
              });
              saveAs(blob, filename);
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
                closeButton: true,
              });
            },
            (progressEvent) => {
              toast.update(toastID, {
                render:
                  "Downloading file (" +
                  Math.floor(
                    (progressEvent.loaded / progressEvent.total) * 100
                  ) +
                  "%)",
                isLoading: true,
              });
            }
          );
        } else {
          toast.update(toastID, {
            render: "File download failed",
            type: "error",
            className: "file-upload-toast",
            isLoading: false,
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            closeButton: true,
          });
        }
      },
      isHistoricalRequest ? "historical" : "records",      
      isHistoricalRequest ? undefined : bcgovcode
    );
  };

  const downloadLinearHarmsDocuments = () => {
    try {
      const message = createMessageForHarms(recordsObj?.records);
      dispatch(
        triggerDownloadFOIRecordsForHarms(
          requestId,
          ministryId,
          message,
          (err, _res) => {
            if (err) {
              toastError(1);
            } else {
              setIsDownloadInProgress(true);
              setIsDownloadReady(false);
              setIsDownloadFailed(false);
            }
            dispatchRequestAttachment(err);
          }
        )
      );
    } catch (error) {
      console.log(error);
      toastError(1);
    }
  };

  const createMessageForHarms = (recordList) => {
    const message = {
      category: RecordDownloadCategory.harms,
      requestnumber: requestNumber,
      bcgovcode: bcgovcode,
      attributes: [],
    };
    //remove duplicate records(except duplicate attachments)
    const deduplicatedRecords = removeDuplicateFiles(recordList);
    //get only relevent fields
    const updatedrecords = getUpdatedRecords(deduplicatedRecords);
    //sort records and attachments based on lastmodified asc
    let sortedRecords = sortByLastModified(updatedrecords);
    //get all the divisions in the records
    const divisionObj = {};
    for (const _record of sortedRecords) {
      for (const _division of _record.divisions) {
        divisionObj[_division.divisionid] = _division.divisionname;
      }
    }
    // arrange the records and its attachments.
    const recordsArray = [];
    for (const _record of sortedRecords) {
      recordsArray.push(_record);
      if (_record.attachments) {
        const _filteredAttachments = _record.attachments.filter(
          (r) => !r.isduplicate
        );
        recordsArray.push(..._filteredAttachments);
      }
    }
    //form the final attributes for the message
    const attributes = [];
    for (const _key in divisionObj) {
      const files = getFiles(recordsArray, +_key);
      const attribute = {
        divisionid: +_key,
        divisionname: divisionObj[_key],
        files: files,
        divisionfilesize: calculateDivisionFileSize(files),
      };
      attributes.push(attribute);
    }
    message.attributes = attributes;
    message.totalfilesize = calculateTotalFileSize(attributes);
    return message;
  };

  const toastError = (itemid) => {
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
    if (itemid === 1) {
      setIsDownloadInProgress(false);
      setIsDownloadReady(false);
      setIsDownloadFailed(true);
    } else if (itemid === 2) {
      setIsRedlineDownloadInProgress(false);
      setIsRedlineDownloadReady(false);
      setIsRedlineDownloadFailed(true);
    } else if (itemid === 3) {
      setIsResponsePackageDownloadInProgress(false);
      setIsResponsePackageDownloadReady(false);
      setIsResponsePackageDownloadFailed(true);
    } else if (itemid === 4) {
      setIsOIPCRedlineInProgress(false);
      setIsOIPCRedlineReady(false);
      setIsOIPCRedlineFailed(true);
    } else if (itemid === 5) {
      setIsOIPCRedlineReviewInProgress(false);
      setIsOIPCRedlineReviewReady(false);
      setIsOIPCRedlineReviewFailed(true);
    } else if (itemid === 6) {
      setIsConsultDownloadInProgress(false);
      setIsConsultDownloadReady(false);
      setIsConsultDownloadFailed(true);
    }
  };
  const phasedReleaseToastError = (packageObj) => {
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
    if (packageObj.category === "redline") {
      setPhasedRedlineDownloadStatuses((prev) => {
        prev.map(item => item.phase === packageObj.phase ? {...item, downloadReady: false, downloadWIP: false, downloadFailed: true} : item)
      });
    } else if (packageObj.category === "responsepackage") {
      setPhasedResponsePackageDownloadStatuses((prev) => {
        prev.map(item => item.phase === packageObj.phase ? {...item, downloadReady: false, downloadWIP: false, downloadFailed: true} : item)
      })
    }
  }

  const isReady = (itemid) => {
    return (
      (itemid === 1 && isDownloadReady) ||
      (itemid === 2 && isRedlineDownloadReady) ||
      (itemid === 3 && isResponsePackageDownloadReady) ||
      (itemid === 4 && isOIPCRedlineReady) ||
      (itemid === 5 && isOIPCRedlineReviewReady) ||
      (itemid === 6 && isConsultDownloadReady)
    );
  };

  const isFailed = (itemid) => {
    return (
      (itemid === 1 && isDownloadFailed) ||
      (itemid === 2 && isRedlineDownloadFailed) ||
      (itemid === 3 && isResponsePackageDownloadFailed) ||
      (itemid === 4 && isOIPCRedlineFailed) ||
      (itemid === 5 && isOIPCRedlineReviewFailed) ||
      (itemid === 6 && isConsultDownloadFailed)
    );
  };

  const isInprogress = (itemid) => {
    return (
      (itemid === 1 && isDownloadInProgress) ||
      (itemid === 2 && isRedlineDownloadInProgress) ||
      (itemid === 3 && isResponsePackageDownloadInProgress) ||
      (itemid === 4 && isOIPCRedlineInProgress) ||
      (itemid === 5 && isOIPCRedlineReviewInProgress) ||
      (itemid === 6 && isConsultDownloadInProgress)
    );
  };
  
  const getPackageDatetime = (itemid) => {
    return (
      (itemid === 1 && pdfStitchedRecord?.createdat_datetime) ||
      (itemid === 2 && redlinePdfStitchedRecord?.createdat_datetime) ||
      (itemid === 3 && responsePackagePdfStitchedRecord?.createdat_datetime) ||
      (itemid === 4 && oipcRedlinePdfStitchedRecord?.createdat_datetime) ||
      (itemid === 5 && oipcRedlineReviewPdfStitchedRecord?.createdat_datetime) ||
      (itemid === 6 && consultPDFStitchedRecord?.createdat_datetime)
    );
  }
  
  const getPhasePackageDatetime = (phasePackage, itemid) => {
    const packageName = `${phasePackage.category}phase${phasePackage.phase}`;
    if (itemid === 2) return phasedRedlinesStitchedRecords.find(phaseRecord => phaseRecord.category === packageName)?.createdat_datetime;
    if (itemid === 3) return phasedResponsePackageStitchedRecords.find(phaseRecord => phaseRecord.category === packageName)?.createdat_datetime;
   
  }

  const downloadSelectedDocuments = async () => {
    let blobs = [];
    var completed = 0;
    let failed = 0;
    var selected = records.filter((record) => record.isselected);

    for(let record of records) {
      if(record.attachments && !record.isselected) {
        for(let attachment of record.attachments) {
          if(attachment.isselected) {
            selected.push(attachment);
          }
        }
      }
    }

    // rename files with duplicate filename
    for (let record of selected) {
      var filename = record.filename;
      var divisionname = record.attributes.divisions[0].divisionname;

      if(!record.newfilename) {
        let duplicatename = selected.filter((_record) => (_record.filename == filename));
        if(duplicatename.length > 1) {
          record.newfilename = filename.substring(0, filename.lastIndexOf(".")) + "_" + divisionname + filename.substring(filename.lastIndexOf("."));
        }

        let duplicatenamedivision = duplicatename.filter((_record) => (_record.attributes.divisions[0].divisionname == divisionname));
        if(duplicatenamedivision.length > 1) {
          let counter = 0;
          for (let duprecord of duplicatenamedivision) {
            if(counter == 1)
              duprecord.newfilename = filename.substring(0, filename.lastIndexOf(".")) + "_" + divisionname + "_Duplicate" + filename.substring(filename.lastIndexOf("."));
            if(counter > 1)
              duprecord.newfilename = filename.substring(0, filename.lastIndexOf(".")) + "_" + divisionname + "_Duplicate (" + counter + ")" + filename.substring(filename.lastIndexOf("."));
            counter++;
          }
        }
      }
    }

    const toastID = toast.loading(
      "Downloading files (" + completed + "/" + selected.length + ")"
    );
    try {
      for (let record of selected) {
        var filepath = record.s3uripath;
        var filename = record.filename;

        if(record.newfilename) {
          filename = record.newfilename;
          record.newfilename = null;
        }

        const response = await getFOIS3DocumentPreSignedUrl(
          filepath.split("/").slice(4).join("/"),
          ministryId,
          dispatch,
          null,
          isHistoricalRequest ? "historical" : "records",
          isHistoricalRequest ? undefined : bcgovcode
        );
        await getFileFromS3({ filepath: response.data }, (_err, res) => {
          let blob = new Blob([res.data], { type: "application/octet-stream" });
          blobs.push({
            name: filename,
            lastModified: res.headers["last-modified"],
            input: blob,
          });
          completed++;
          toast.update(toastID, {
            render:
              "Downloading files (" + completed + "/" + selected.length + ")",
            isLoading: true,
          });
        });
      }
    } catch (error) {
      console.log(error);
    }
    var toastOptions = {
      render:
        failed > 0
          ? failed.length + " file(s) failed to download"
          : selected.length + " Files exported",
      type: failed > 0 ? "error" : "success",
    };
    toast.update(toastID, {
      ...toastOptions,
      isLoading: false,
      autoClose: 3000,
      hideProgressBar: true,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      closeButton: true,
    });
    if(blobs.length == 1) {
      saveAs(blobs[0].input, blobs[0].name);
    } else {
      const zipfile = await downloadZip(blobs).blob();
      saveAs(zipfile, requestNumber + " Records" + ".zip");
    }
  };

  const retryDocument = (record) => {
    let selectedRecords =[]
    if (Object.keys(record).length === 0)
      selectedRecords = records.filter((record) => record.isselected);
    else
      selectedRecords = [record]
    for (let record of selectedRecords) {
      record.trigger = "recordretry";
      let retryServiceName = record.failed ? record.failed.split('.')[0] : "all" ;
      if (retryServiceName == 'ocr-queue')
        retryServiceName='ocr'
      console.log(retryServiceName);
      record.service = retryServiceName
      //record.failed ? record.failed : "all";
      if (record.isattachment) {
        var parentRecord = recordsObj?.records?.find(
          (r) => (r.recordid = record.rootparentid)
        );
        record.attributes.divisions = parentRecord.attributes.divisions;
        record.attributes.batch = parentRecord.attributes.batch;
        record.attributes.extension = record["s3uripath"].substr(
          record["s3uripath"].lastIndexOf("."),
          record["s3uripath"].length
        );
        record.attributes.incompatible = false;
        record.attributes.isattachment = true;
      }
      if (record.service === "deduplication") {
        record["s3uripath"] =
          record["s3uripath"].substr(0, record["s3uripath"].lastIndexOf(".")) +
          ".pdf";
      }
    }
    dispatch(
      retryFOIRecordProcessing(
        requestId,
        ministryId,
        { records: selectedRecords },
        (err, _res) => {
          dispatchRequestAttachment(err);
        }
      )
    );
  };

  const removeAttachments = () => {
    setDeleteModalOpen(false);
    var attachments = records?.reduce((acc, record) => {
      return record.attachments
        ? acc.concat(record.attachments.map((a) => a.filepath))
        : acc;
    }, []);
    dispatch(
      deleteReviewerRecords(
        { filepaths: attachments, ministryrequestid: ministryId },
        (err, _res) => {
          dispatchRequestAttachment(err);
        }
      )
    );
  };

  const retrieveRecordVersion = (action, record) => {
    console.log("-->",Object.keys(record).length)
    let selectedRecords=[]
    if(Object.keys(record).length === 0)
      selectedRecords = records.filter((record) => record.isselected);
    else
      selectedRecords = [record]
    const documentMasterIds = selectedRecords?.map(record => record.converteddocmasterid ?? record.documentmasterid);
    dispatch(
      retrieveSelectedRecordVersion(
        requestId,
        ministryId,
        { documentmasterids: documentMasterIds,
          recordretrieveversion: action
         }));
    //     (err, _res) => {
    //     }
    //   )
    // );
  }

  const hasDocumentsToExport =
    records?.filter(
      (record) => !(isMinistryCoordinator && record.category == "personal")
    ).length > 0;
  const hasDocumentsToDownload =
    records?.filter((record) => record.category !== "personal").length > 0;

  const handlePopupButtonClick = (action, _record) => {
    setUpdateAttachment(_record);
    setMultipleFiles(false);
    switch (action) {
      case "retrieve_uncompressed":
        retrieveRecordVersion(action, _record);
        setModal(false);
        break;
      case "replace":
        setreplaceRecord(_record);
        setModalFor("replace");
        setModal(true);
        break;
      case "replaceattachment":
        setreplaceRecord(_record);
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
        setModalFor("delete");
        setModal(true);
        break;
      case "downloadselected":
        downloadSelectedDocuments();
        setModalFor("download");
        setModal(false);
        break;
      case "retry":
        retryDocument(_record);
        setModal(false);
        break;
      default:
        setModal(false);
        break;
    }
  };

  const handleRename = (_record, newFilename) => {
    setModal(false);

    if (updateAttachment.filename !== newFilename) {
      const documentId = ministryId
        ? updateAttachment.foiministrydocumentid
        : updateAttachment.foidocumentid;
      dispatch(
        saveNewFilename(
          newFilename,
          documentId,
          requestId,
          ministryId,
          (err, _res) => {
            if (!err) {
              setAttachmentLoading(false);
            }
          }
        )
      );
    }
  };

  const getFullname = (userId) => {
    let user;

    if (fullnameList) {
      user = fullnameList.find((u) => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    } else {
      if (iaoassignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, "iao");
        setFullnameList(getFullnameList());
      }

      if (ministryAssignedToList.length > 0) {
        addToFullnameList(iaoassignedToList, bcgovcode);
        setFullnameList(getFullnameList());
      }

      user = fullnameList.find((u) => u.username === userId);
      return user && user.fullname ? user.fullname : userId;
    }
  };

  const getRequestNumber = () => {
    if (requestNumber) return `Request #${requestNumber}`;
    return `Request #U-00${requestId}`;
  };

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
    var replacefileextensions = [...MimeTypeList.recordsLog];

    let _filename =
      replaceRecord?.originalfilename === ""
        ? replaceRecord.filename
        : replaceRecord.originalfilename;
    let fileextension = _filename?.split(".").pop();

    switch (fileextension) {
      case "docx" || "doc":
        replacefileextensions = [
          "application/pdf",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/msword",
          ".doc",
          ".docx",
        ];
        break;
      case "xlsx" || "xls":
        replacefileextensions = [
          "application/pdf",
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "application/vnd.ms-excel",
          ".xls",
          ".xlsx",
        ];
        break;
      case "msg" || "eml":
        replacefileextensions = ["application/pdf", ".msg", ".eml"];
        break;
      case "pdf":
        replacefileextensions = ["application/pdf"];
        break;
      default:
        replacefileextensions = [...MimeTypeList.recordsLog];
        break;
    }

    return replacefileextensions;
  };

  React.useEffect(() => {
    if (divisionFilters.findIndex((f) => f.divisionid === filterValue) > -1 || isHistoricalRequest) {
      setRecords(
        searchAttachments(
          _.cloneDeep(recordsObj.records),
          filterValue,
          searchValue,
          filterText
        )
      );
    } else {
      setFilterValue(-1);
      setFilterText("");
    }
  }, [filterValue, searchValue, recordsObj]);

  const searchAttachments = (_recordsArray, _filterValue, _keywordValue, _filterText) => {
    var filterFunction = (r) => {
      var isMatch = (
        (r.filename.toLowerCase().includes(_keywordValue?.toLowerCase()) ||
          r.createdby?.toLowerCase().includes(_keywordValue?.toLowerCase())) &&
        (_filterValue === -3
          ? r.attributes?.incompatible
          : _filterValue === -2
          ? !r.isredactionready &&
            !r.attributes?.incompatible &&
            (r.failed ||
              isrecordtimeout(r.created_at, RECORD_PROCESSING_HRS) == true)
          : _filterValue > -1
          ? r.attributes?.divisions?.findIndex(
              (a) => a.divisionid === _filterValue && a.divisionname !== "TBD"
            ) > -1
            ||
            r.attributes?.personalattributes?.person === _filterText
            ||
            r.attributes?.personalattributes?.filetype === _filterText
            ||
            r.attributes?.personalattributes?.volume === _filterText
            ||
            r.attributes?.personalattributes?.personaltag === _filterText
          : true)
      )
      if (isMatch) {
        return true;
      } else if (r.attachments?.length > 0) {
        r.attachments = r.attachments.filter(filterFunction);
        return r.attachments.length > 0;
      } else {
        return false;
      }
    };
    setIsAllSelected(false);
    return _recordsArray?.filter(filterFunction);
  };

  const handleSelectRecord = (record, e) => {
    const newRecords = records.map((r, i) => {
      if (record.isattachment) {
        if (r.documentmasterid === record.rootdocumentmasterid) {
          var newAttachments = r.attachments.map((a, j) => {
            if (a.documentmasterid === record.documentmasterid) {
              record.isselected = e.target.checked;
              return record;
            } else {
              if (a.parentid === record.documentmasterid) {
                if (e.target.checked) {
                  a.isselected = true;
                }
              }
              if (a.documentmasterid === record.parentid) {
                if (!e.target.checked) {
                  a.isselected = false;
                }
              }
              return a;
            }
          });
          r.attachments = newAttachments;
          if (!e.target.checked) {
            r.isselected = false;
          }
          return r;
        } else {
          return r;
        }
      } else {
        if (r.documentmasterid === record.documentmasterid) {
          record.isselected = e.target.checked;
          if (e.target.checked && record.attachments) {
            for (let attachment of record.attachments) {
              attachment.isselected = e.target.checked;
            }
          }
          return record;
        } else {
          return r;
        }
      }
    });
    setRecords(newRecords);
    setIsAllSelected(checkIsAllSelected());
  };

  const handleSelectAll = (e) => {
    const newRecords = records.map((r, i) => {
      r.isselected = e.target.checked;
      if (r.attachments) {
        var newAttachments = r.attachments.map((a, j) => {
          a.isselected = e.target.checked;
          return a;
        });
        r.attachments = newAttachments;
      }
      return r;
    });
    setRecords(newRecords);
    setIsAllSelected(checkIsAllSelected());
  };

  const checkIsAllSelected = () => {
    for (let record of records) {
      if (!record.isselected) return false;
      if (record.attachments) {
        for (let attachment of record.attachments) {
          if (!attachment.isselected) return false;
        }
      }
    }
    return true;
  };

  const checkIsAnySelected = () => {
    for (let record of records) {
      if (record.isselected) return true;
      if (record.attachments) {
        for (let attachment of record.attachments) {
          if (attachment.isselected) return true;
        }
      }
    }
    return false;
  };

  const disableMultiRetrieve = () => {
      let selectedRecords = records.filter((record) => record.isselected);
      if (selectedRecords?.length <=0)
        return true
      for (let record of selectedRecords) {
        if (record.selectedfileprocessversion || record.attributes?.incompatible) return true;
        if (record.attachments) {
          for (let attachment of record.attachments) {
            if (record.selectedfileprocessversion || record.attributes?.incompatible) return true;
          }
        }
      }
      return false;
  }

  const disableMultiRetry = () => {
      let selectedRecords = records.filter((record) => record.isselected);
      if (selectedRecords?.length <=0)
        return true
      for (let record of selectedRecords) {
        if (record.isredactionready || record.selectedfileprocessversion ||
              (!record.failed && !isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) ==
                  true)) return true;
        if (record.attachments) {
          for (let attachment of record.attachments) {
            if (record.isredactionready || record.selectedfileprocessversion ||
              !record.failed || !isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) ==
                  true) return true;
          }
        }
      }
      return false;
  }

  

  const displaySizeLimit = () => {
    if(RECORD_DOWNLOAD_SIZE_LIMIT >= (1024*1024*1024))
      return (RECORD_DOWNLOAD_SIZE_LIMIT/(1024*1024*1024)).toFixed(1) + "GB";
    if(RECORD_DOWNLOAD_SIZE_LIMIT >= (1024*1024))
      return (RECORD_DOWNLOAD_SIZE_LIMIT/(1024*1024)).toFixed(1) + "MB";
    if(RECORD_DOWNLOAD_SIZE_LIMIT >= 1024 )
      return (RECORD_DOWNLOAD_SIZE_LIMIT/(1024)).toFixed(1) + "KB";
    return RECORD_DOWNLOAD_SIZE_LIMIT + "Bytes";
  }

  const isSelectLimitReached = () => {
    let fileCount = 0;
    let totalFileSize = 0;

    const recordlimit = RECORD_DOWNLOAD_LIMIT == 0 ? 1000000000 : RECORD_DOWNLOAD_LIMIT;
    const sizelimt = RECORD_DOWNLOAD_SIZE_LIMIT == 0 ? 999999999999 : RECORD_DOWNLOAD_SIZE_LIMIT;

    for (let record of records) {
      if (record.isselected) {
        fileCount++;
        totalFileSize += record.attributes.filesize;

        if(fileCount > recordlimit || totalFileSize > sizelimt)
          return true;
      } else {
        if(record.attachments) {
          for(let attachment of record.attachments) {
            if(attachment.isselected) {
              fileCount++;
              totalFileSize += parseInt(attachment.attributes.filesize);


              if(fileCount > recordlimit || totalFileSize > sizelimt)
                return true;
            }
          }
        }
      }
    }

    if(fileCount == 0)
      return true;
    else
      return false;
  };

  function intersection(setA, setB) {
    const _intersection = new Set();
    for (const elem of setB) {
      if (setA.has(elem)) {
        _intersection.add(elem);
      }
    }
    return _intersection;
  }

  const isUpdateDivisionsDisabled = () => {
    if (isHistoricalRequest) {
      return true;
    }
    var count = 0;
    var selectedDivision = new Set();
    for (let record of records) {
      if (record.isselected) {
        if (!record.isredactionready) {
          return true;
        }
        count++;
        if (selectedDivision.size === 0) {
          record.attributes.divisions.forEach((d) =>
            selectedDivision.add(d.divisionid)
          );
        } else {
          let int = intersection(
            selectedDivision,
            new Set(record.attributes.divisions?.map((d) => d.divisionid))
          );
          if (int.size === 0) {
            return true;
          } else {
            selectedDivision = int;
          }
        }
      }
      if (!record.isselected && record.attachments) {
        for (let attachment of record.attachments) {
          if (attachment.isselected) return true;
        }
      }
    }
    // setDivisionToUpdate()

    if (isMCFPersonal && selectedDivision.size > 0) {
      if (divisions?.find((d) => selectedDivision.has(d.divisionid))) {
        return !isMinistryCoordinator;
      } else {
        return isMinistryCoordinator;
      }
    }
    return count === 0;
  };

  const updateDivisions = () => {
    setDivisionModalTagValue(-1);
    setDivisionsModalOpen(false);
    var updateRecords = [];
    for (let record of records) {
      if (record.isselected) {
        if (
          record.attributes.divisions?.length > 1 &&
          record.attributes.divisions[0].divisionid !== filterValue
        ) {
          if (filterValue < 0) {
            throw new Error(
              "invalid filter value - need to select a single division"
            );
          }
          for (var i = 1; i < record.attributes.divisions?.length; i++) {
            if (record.attributes.divisions[i].divisionid === filterValue) {
              let updateRecord = records.find(
                (r) =>
                  r.documentmasterid ===
                  record.attributes.divisions[i].duplicatemasterid
              );
              updateRecords.push(
                (({ recordid, documentmasterid, s3uripath }) => ({
                  recordid,
                  documentmasterid,
                  filepath: s3uripath,
                }))(updateRecord)
              );
              updateRecords = updateRecords.concat(
                updateRecord.attachments?.map((a) =>
                  (({ documentmasterid, s3uripath }) => ({
                    documentmasterid,
                    filepath: s3uripath,
                  }))(a)
                )
              );
            }
          }
        } else {
          updateRecords.push(
            (({ recordid, documentmasterid, s3uripath }) => ({
              recordid,
              documentmasterid,
              filepath: s3uripath,
            }))(record)
          );
          updateRecords = updateRecords.concat(
            record.attachments?.map((a) =>
              (({ documentmasterid, s3uripath }) => ({
                documentmasterid,
                filepath: s3uripath,
              }))(a)
            )
          );
        }
      }
    }
    dispatch(
      updateFOIRecords(
        requestId,
        ministryId,
        {
          records: updateRecords,
          divisions: [{ divisionid: divisionModalTagValue }],
          isdelete: false,
        },
        (err, _res) => {
          dispatchRequestAttachment(err);
        }
      )
    );
  };

  const comparePersonalAttributes = (a, b) => {
    return a?.person === b?.person && a?.volume === b?.volume
              && a?.filetype === b?.filetype
              && a?.personaltag === b?.personaltag
              && a?.trackingid === b?.trackingid;
  };

  const [isBulkEdit, setIsBulkEdit] = React.useState(false);

  useEffect(() => {
    let selectedRecords = records.filter((record) => record.isselected);
    setIsBulkEdit(selectedRecords.length > 1);
  }, [records])

  const isBulkEditDisabled = () => {
    if (isBulkEdit) {
    return false;
    } else {
      return true;
    }
  }

  const updatePersonalAttributes = (_all = false) => {
    const selectedRecords = records.filter((record) => record.isselected);
    setEditTagModalOpen(false);
    var updateRecords = [];
    var updateDivisionForRecords = [];

    if(newPersonalAttributes) {
      if(_all) {
        for (let record of records) {
          if(record.attributes?.personalattributes?.person
             && record.attributes?.personalattributes?.person === currentEditRecord.attributes?.personalattributes?.person
            //  && record.attributes?.personalattributes?.filetype
            //  && record.attributes?.personalattributes?.filetype === currentEditRecord.attributes?.personalattributes?.filetype
          ) {
            updateRecords.push(
              (({ recordid, documentmasterid, s3uripath }) => ({
                recordid,
                documentmasterid,
                filepath: s3uripath,
              }))(record)
            );
          }
  
          if(record.attachments) {
            for (let attachment of record.attachments) {
              if(attachment.attributes?.personalattributes?.person
                && attachment.attributes?.personalattributes?.person === currentEditRecord.attributes?.personalattributes?.person
                // && attachment.attributes?.personalattributes?.filetype
                // && attachment.attributes?.personalattributes?.filetype === currentEditRecord.attributes?.personalattributes?.filetype
              ) {
                updateRecords.push(
                  (({ documentmasterid, s3uripath }) => ({
                    documentmasterid,
                    filepath: s3uripath,
                  }))(attachment)
                );
              }
            }
          }
        }
      } else if (selectedRecords.length > 1 && !currentEditRecord) {
        for (let selectedRecord of selectedRecords) {
          updateRecords.push(
            {
              recordid: selectedRecord.recordid,
              documentmasterid: selectedRecord.documentmasterid,
              filepath: selectedRecord.s3uripath
            }
          );
        }
      } else if (currentEditRecord) {
        updateRecords.push(
          {
            recordid: currentEditRecord.recordid,
            documentmasterid: currentEditRecord.documentmasterid,
            filepath: currentEditRecord.s3uripath
          }
        );
      }
    }

    if(isMinistryCoordinator
      && currentEditRecord
      && currentEditRecord.attributes.divisions[0].divisionname != "TBD"
      && currentEditRecord.attributes.divisions[0].divisionid != divisionModalTagValue) {
      updateDivisionForRecords.push(
        {
          recordid: currentEditRecord.recordid,
          documentmasterid: currentEditRecord.documentmasterid,
          filepath: currentEditRecord.s3uripath
        }
      );
    }

    if(isMinistryCoordinator
      && selectedRecords.length > 1
      && divisionModalTagValue !== -1
    )
      for (let selectedRecord of selectedRecords) {
        updateDivisionForRecords.push(
          {
            recordid: selectedRecord.recordid,
            documentmasterid: selectedRecord.documentmasterid,
            filepath: selectedRecord.s3uripath
          }
        );
      }

    if(currentEditRecord || selectedRecords.length > 1) {
      if(updateRecords.length > 0 && !comparePersonalAttributes(newPersonalAttributes, curPersonalAttributes)) {
        dispatch(
          editPersonalAttributes(
            requestId,
            ministryId,
            {
              records: updateRecords,
              newpersonalattributes: newPersonalAttributes,
            },
            (err, _res) => {
              if(updateDivisionForRecords.length > 0) {
                dispatch(
                  updateFOIRecords(
                    requestId,
                    ministryId,
                    {
                      records: updateDivisionForRecords,
                      divisions: [{ divisionid: divisionModalTagValue }],
                      isdelete: false,
                    },
                    (err, _res) => {
                      dispatchRequestAttachment(err);
                    }
                  )
                );
              } else {
                dispatchRequestAttachment(err);
              }
            }
          )
        );
      } else {
        if(updateDivisionForRecords.length > 0) {
          dispatch(
            updateFOIRecords(
              requestId,
              ministryId,
              {
                records: updateDivisionForRecords,
                divisions: [{ divisionid: divisionModalTagValue }],
                isdelete: false,
              },
              (err, _res) => {
                dispatchRequestAttachment(err);
              }
            )
          );
        }
      }

      setDivisionModalTagValue(-1);
      setCurrentEditRecord();
      setCurPersonalAttributes({
        person: "",
        filetype: "",
        volume: "",
        trackingid: "",
        personaltag: "TBD"
      });
      setNewPersonalAttributes();
    }
  };

  //function to manage download for harms option
  const enableHarmsDonwnload = () => {
    return !recordsObj.records.every(
      (record) =>
        record.isredactionready ||
        record.failed ||
        isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS)
    );
  };

  const handleLockRecords = () => {
    const toastID = toast.loading("Updating records lock status for request...");
    const data = {userrecordslockstatus: !lockRecords};
    dispatch(
      updateSpecificRequestSection(
        data,
        'userrecordslockstatus',
        requestId,
        ministryId, 
        (err, _res) => {
        if(!err) {
          setSaveRequestObject(prev => ({...prev, userrecordslockstatus: !lockRecords}));
          setLockRecordsTab(!lockRecords);
          toast.update(toastID, {
            type: "success",
            render: "Request details have been saved successfully.",
            position: "top-right",
            isLoading: false,
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          });
        } else {
          toast.error(
            "Temporarily unable to update records lock status for request. Please try again in a few minutes.",
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
      })
    )
  }

  const saveEstimates = (e) => {
    requestDetails.estimatedpagecount = estimatedPageCount
    requestDetails.estimatedtaggedpagecount = estimatedTaggedPageCount
    dispatch(
      saveRequestDetails(
        requestDetails,
        -1,
        requestId,
        ministryId,
        (err, res) => {    
          if (res!= null && res?.status == true) {
            toast.success("The request has been saved successfully.", {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
            handleSaveRequest(requestDetails.currentState, false, res.id);
          } else {
            toast.error(
              "Temporarily unable to save your request. Please try again in a few minutes.",
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
            handleSaveRequest(requestDetails.currentState, true, "");
          }
        }
      )
    );
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
            <Grid item xs={5} style={{marginBottom: 15}}>
              <h1 className="foi-review-request-text foi-ministry-requestheadertext foi-records-request-text">
                {getRequestNumber()}
              </h1>
            </Grid>
            {validLockRecordsState() ?
            <Grid item xs={isScanningTeamMember ? 1 : 1}>
              <Tooltip 
                enterDelay={1000} 
                title={isMinistryCoordinator ? "Only the IAO analyst can manually lock or unlock the records log, please contact the assigned analyst for assistance" : "Manually unlock or lock the records log"}
              >
                {isMinistryCoordinator ? 
                  <p
                    style={{ fontWeight: "bold", fontSize: "17.5px", marginTop: "4px", color: "#036" }}
                  >
                    {lockRecords ? "Records Locked" : "Records Unlocked"}
                  </p>
                : <span>
                <button
                disabled={isMinistryCoordinator}
                onClick={handleLockRecords}
                className={clsx(
                  "btn",
                  classes.createButton
                  )}
                  variant="contained"
                  color="primary"
                >
                  {lockRecords ? "Unlock Records" : "Lock Records"}
                </button>
                </span>
                }
              </Tooltip>
            </Grid> :  <Grid item xs={isScanningTeamMember ? 1 : 1}></Grid>
            }
            {(isMinistryCoordinator == false &&
              records?.length > 0 &&
              DISABLE_REDACT_WEBLINK?.toLowerCase() == "false" && (
                <Tooltip title={<div style={{ fontSize: "11px" }}>Some files are still processing or have errors. 
                  Please ensure that all files are successfully processed.</div>}>
                  <Grid item xs={isScanningTeamMember ? 1 : 1}>
                  <a
                    href={DOC_REVIEWER_WEB_URL + "/foi/" + ministryId}
                    target="_blank"
                  >
                    <button
                      className={clsx(
                        "btn",
                        "addAttachment",
                        classes.createButton
                      )}
                      variant="contained"
                      // onClick={}
                      disabled={isDisableRedactRecords(records)}
                      color="primary"
                    >
                      Redact Records
                    </button>
                  </a>
                  </Grid>
                </Tooltip>
              )
            )}
            <Grid item xs={3}>
              {hasDocumentsToDownload && !isHistoricalRequest && (
                <TextField
                  className="download-dropdown custom-select-wrapper foi-download-button"
                  id="download"
                  label={currentDownload === 0 ? "Download" : ""}
                  inputProps={{ "aria-labelledby": "download-label" }}
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
                    if (item.id !== 0) {
                      if ((item.id === 2 || item.id === 3) && isPhasedRelease) {
                        return <PhaseMenu 
                        handlePhasePackageDownload={handlePhasePackageDownload} 
                        item={item} 
                        index={index} 
                        phasedPackageDownloadStatuses={item.id === 2 ? phasedRedlineDownloadStatuses : phasedResponsePackageDownloadStatuses}
                        getPhasePackageDatetime={getPhasePackageDatetime} 
                        />
                      } else {
                      return (
                        <MenuItem
                          className="download-menu-item"
                          key={item.id}
                          value={index}
                          disabled={item.disabled}
                          sx={{ display: "flex" }}
                        >
                          {isReady(item.id) ? (
                            <FontAwesomeIcon
                              icon={faCheckCircle}
                              size="2x"
                              color="#1B8103"
                              className={classes.statusIcons}
                            />
                          ) : isFailed(item.id) ? (
                            <FontAwesomeIcon
                              icon={faExclamationCircle}
                              size="2x"
                              color="#A0192F"
                              className={classes.statusIcons}
                            />
                          ) : isInprogress(item.id) ? (
                            <FontAwesomeIcon
                              icon={faSpinner}
                              size="2x"
                              color="#FAA915"
                              className={classes.statusIcons}
                            />
                          ) : null}
                          <Tooltip enterDelay={500} title={`Created On: ${getPackageDatetime(item.id) ? getPackageDatetime(item.id) : "N/A"}`}>
                            <span>{item.label}</span>
                          </Tooltip>
                        </MenuItem>
                      )};
                    }
                  })}
                </TextField>
              )}
            </Grid> 
            <Grid item xs={2}>
              {
              (!isHistoricalRequest) && (
                <button
                  className={clsx("btn", "addAttachment", classes.createButton)}
                  variant="contained"
                  onClick={addAttachments}
                  color="primary"
                  disabled={lockRecords || conversionFormats?.length < 1 || (isMinistryCoordinator && divisions.length === 0)}
                >
                  + Upload Records
                </button>
              )}
            </Grid>
                      
                        
          </Grid>
          <Grid
            container
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            spacing={1}
          >
            {!isHistoricalRequest && <>
            <Grid item xs={7}>
              <span style={{ fontWeight: "bold" }}>
                <div >
                  Total Uploaded Size :{" "}
                  {getReadableFileSize(totalUploadedRecordSize)}
                </div>
              </span>
            </Grid>
            <Grid item xs={3}>
              <span style={{ fontWeight: "bold" }}>
                {isMCFPersonal && <div >
                  Estimated Physical Pages:{" "}    
                </div>}
              </span>
            </Grid>
            <Grid item xs={2}>
              {isMCFPersonal && <span style={{ fontWeight: "bold" }}>
                <div>                  
                  <TextField
                    type="number"
                    inputProps={{
                      step: 1,
                      min: 0,
                      style: {height: 12}
                    }}
                    style={{width: 90}}
                    size="small"
                    value={estimatedPageCount}
                    onChange={(e) => setEstimatedPageCount(e.target.value)}
                    disabled={isMinistryCoordinator}
                  ></TextField>  
                </div>
              </span>}
            </Grid>
                          
            <Grid item xs={7}>
              <span style={{ fontWeight: "bold" }}>
                <div>
                  Total Upload Limit :{" "}
                  {getReadableFileSize(TOTAL_RECORDS_UPLOAD_LIMIT)}
                </div>
              </span>
            </Grid>
            <Grid item xs={3}>
              <span style={{ fontWeight: "bold" }}>
                {isMCFPersonal && <div>
                  Estimated Pages After Tagging:{" "}
                  {/* <button 
                    class="btn" 
                    style={{
                      backgroundColor: "#38598A",
                      color: "White",
                      height: 29,
                      paddingTop: 2,
                      marginLeft: 10
                    }} 
                    onClick={saveEstimates}
                  >
                    Save
                  </button> */}
                </div>}
              </span>
            </Grid>           
            <Grid item xs={2}>
              {isMCFPersonal && 
                <>
                  <TextField
                    type="number"
                    inputProps={{
                      step: 1,
                      min: 0,
                      style: {height: 12}
                    }}
                    style={{width: 90}}
                    size="small"
                    value={estimatedTaggedPageCount}
                    onChange={(e) => setEstimatedTaggedPageCount(e.target.value)}
                    disabled={isMinistryCoordinator}
                  ></TextField>              
                  <button 
                    class="btn" 
                    style={{
                      backgroundColor: "#38598A",
                      color: "White",
                      height: 29,
                      paddingTop: 2,
                      marginLeft: 10,
                      fontWeight: "bold",
                      width: "calc(100% - 100px)"
                    }} 
                    onClick={saveEstimates}
                    disabled={isMinistryCoordinator || (estimatedTaggedPageCount === requestDetails.estimatedtaggedpagecount && 
                      estimatedPageCount === requestDetails.estimatedpagecount)}
                  >
                    Save
                  </button>
                </>
              }
            </Grid>            
            </>}
            {/* <Grid item xs={1}>
            </Grid> */}
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
                  <span className="number-spacing">
                    {recordsObj.dedupedfiles}
                  </span>
                </Grid>
                <Grid item xs={3}>
                  <span>Duplicates Removed:</span>
                  <span className="number-spacing">
                    {recordsObj.removedfiles}
                  </span>
                </Grid>
                <Grid item xs={3}>
                  <span>Files Converted to PDF:</span>
                  <span className="number-spacing">
                    {recordsObj.convertedfiles}
                  </span>
                </Grid>
                <Grid item xs={3} direction="row-reverse">
                  <span style={{ float: "right" }}>
                    <span>Batches Uploaded:</span>
                    <span className="number-spacing">
                      {recordsObj.batchcount ? recordsObj.batchcount : 0}
                    </span>
                  </span>
                </Grid>
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
                <Divider
                  className={"record-divider"}
                  style={{ backgroundColor: "#979797" }}
                />
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
                  maxWidth: "100%",
                  backgroundColor: "rgba(56,89,138,0.1)",
                  borderBottomLeftRadius: 0,
                  borderBottomRightRadius: 0,
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
                    onChange={(e) => {
                      setSearchValue(e.target.value.trim());
                    }}
                    sx={{
                      color: "#38598A",
                    }}
                    startAdornment={
                      <InputAdornment position="start">
                        <IconButton
                          aria-label="Search Icon"
                          className="search-icon"
                        >
                          <span className="hideContent">
                            Filter Records ...
                          </span>
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
                  maxWidth: "100%",
                  paddingTop: "8px",
                  borderTopLeftRadius: 0,
                  borderTopRightRadius: 0,
                  borderTop: "none",
                }}
                alignItems="center"
                justifyContent="flex-start"
                direction="row"
                container
                item
                xs={12}
                elevation={0}
              >
                {divisionFilters.map((division) => (
                  <ClickableChip
                    item
                    // id={`${division.divisionid}Filter`}
                    // key={`${division.divisionid}-filter`}
                    label={division.divisionname.toUpperCase()}
                    sx={{
                      width: "fit-content",
                      marginLeft: "8px",
                      marginBottom: "8px",
                    }}
                    color={
                      division.divisionid === -2
                        ? "#A0192F"
                        : division.divisionid === -3
                        ? "#B57808"
                        : "primary"
                    }
                    size="small"
                    onClick={(e) => {
                      setFilterValue(
                        division.divisionid === filterValue
                          ? -1
                          : division.divisionid
                      );
                      setFilterText(
                        division.divisionname === filterText
                          ? ""
                          : division.divisionname
                      );
                    }}
                    clicked={filterValue == division.divisionid}
                  />
                ))}
              </Paper>
            </Grid>
            <Grid
              container
              item
              xs={12}
              direction="row"
              justify="flex-start"
              alignItems="flex-start"
            >
              <input
                type="checkbox"
                style={{ position: "relative", top: 7, marginRight: 15 }}
                className="checkmark record-checkmark"
                key={"selectallchk" + isAllSelected}
                id={"selectallchk"}
                onChange={handleSelectAll}
                required
                checked={isAllSelected}
              />
              <Tooltip
                title={
                  <div style={{ fontSize: "11px" }}>Remove Attachments</div>
                }
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => setDeleteModalOpen(true)}
                    // title="Remove Attachments"
                    disabled={lockRecords || 
                      records.filter((record) => record.attachments?.length > 0)
                        .length === 0
                    }
                    style={
                      records.filter((record) => record.attachments?.length > 0)
                        .length === 0 || lockRecords
                        ? { pointerEvents: "none" }
                        : {}
                    }
                  >
                    <FontAwesomeIcon
                      icon={faLinkSlash}
                      size="lg"
                      color="#38598A"
                    />
                  </button>
                </span>
              </Tooltip>
              {(!isMCFPersonal) && (
              <Tooltip
                title={
                  isUpdateDivisionsDisabled() ? (
                    <div style={{ fontSize: "11px" }}>
                      To update divisions:{" "}
                      <ul>
                        <li>Records log must be unlocked</li>
                        <li>at least one record must be selected</li>
                        <li>
                          all records selected must be tagged to the same
                          division
                        </li>
                        <li>
                          {" "}
                          and all records selected must be finished processing
                        </li>
                      </ul>
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px" }}>Update Divisions</div>
                  )
                }
                sx={{ fontSize: "11px" }}
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => setDivisionsModalOpen(true)}
                    // title="Update Divisions"
                    disabled={lockRecords || isUpdateDivisionsDisabled()}
                    style={
                      lockRecords || isUpdateDivisionsDisabled()
                        ? { pointerEvents: "none" }
                        : {}
                    }
                  >
                    <FontAwesomeIcon
                      icon={faPenToSquare}
                      size="lg"
                      color="#38598A"
                    />
                  </button>
                </span>
              </Tooltip>
              )}
              {(isMCFPersonal) && (
              <Tooltip
                title={
                  isBulkEditDisabled() ? (
                    <div style={{ fontSize: "11px" }}>
                      To bulk edit tags, please select two or more files, otherwise please use the 'Edit Tags' option from the ellipses dropdown next to the individual file
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px" }}>Edit Tags</div>
                  )
                }
                sx={{ fontSize: "11px" }}
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => {
                      setCurPersonalAttributes({
                        person: "",
                        filetype: "",
                        volume: "",
                        trackingid: "",
                        personaltag: ""
                      });
                      setDivisionModalTagValue(-1);
                      setEditTagModalOpen(true);
                    }}
                    disabled={lockRecords || isBulkEditDisabled()}
                    style={
                      lockRecords || isBulkEditDisabled()
                        ? { pointerEvents: "none" }
                        : {}
                    }
                  >
                    <FontAwesomeIcon
                      icon={faPenToSquare}
                      size="lg"
                      color="#38598A"
                    />
                  </button>
                </span>
              </Tooltip>
              )}
              <Tooltip title={<div style={{ fontSize: "11px" }}>Delete</div>}>
                <span>
                  <button
                    className={` btn`}
                    onClick={() => handlePopupButtonClick("delete")}
                    // title="Delete"
                    disabled={lockRecords || !checkIsAnySelected() || isHistoricalRequest}
                    style={
                      lockRecords || !checkIsAnySelected() ? { pointerEvents: "none" } : {}
                    }
                  >
                    <FontAwesomeIcon icon={faTrash} size="lg" color="#38598A" />
                  </button>
                </span>
              </Tooltip>
              <Tooltip
                title={
                  isSelectLimitReached() ? (
                    <div style={{ fontSize: "11px" }}>
                      To download records:{" "}
                      <ul>
                        <li>at least one record must be selected</li>
                        {RECORD_DOWNLOAD_SIZE_LIMIT>0 && (<li>download size limit is {displaySizeLimit()}</li>)}
                        {RECORD_DOWNLOAD_LIMIT>0 && (<li>download records limit is {RECORD_DOWNLOAD_LIMIT}</li>)}
                      </ul>
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px" }}>Download</div>
                  )
                }
                sx={{ fontSize: "11px" }}
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => handlePopupButtonClick("downloadselected")}
                    // title="Delete"
                    disabled={isSelectLimitReached()}
                    style={
                      isSelectLimitReached() ? { pointerEvents: "none" } : {}
                    }
                  >
                    <FontAwesomeIcon icon={faDownload} size="lg" color="#38598A" />
                  </button>
                </span>
              </Tooltip>
              <Tooltip
                title={
                  disableMultiRetrieve() ? (
                    <div style={{ fontSize: "11px" }}>
                      To retrieve uncompressed files:{" "}
                      <ul>
                        <li>at least one record must be selected</li>
                        <li>selected records must not have been retrieved already.</li>
                      </ul>
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px" }}>Retrieve Uncompressed files</div>
                  )
                }
                sx={{ fontSize: "11px" }}
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => handlePopupButtonClick("retrieve_uncompressed", {})}
                    disabled={lockRecords || disableMultiRetrieve() || isHistoricalRequest}
                    style={
                      lockRecords || !checkIsAnySelected() ? { pointerEvents: "none" } : {}
                    }
                  >
                    <FontAwesomeIcon icon={faMinimize} size="lg" color="#38598A" />
                  </button>
                </span>
              </Tooltip>
              <Tooltip
                title={
                  disableMultiRetry() ? (
                    <div style={{ fontSize: "11px" }}>
                      To retry failed files:{" "}
                      <ul>
                        <li>at least one record must be selected</li>
                        <li>only records with a failed status should be selected</li>
                      </ul>
                    </div>
                  ) : (
                    <div style={{ fontSize: "11px" }}>Retry Failed files</div>
                  )
                }
                sx={{ fontSize: "11px" }}
              >
                <span>
                  <button
                    className={` btn`}
                    onClick={() => handlePopupButtonClick("retry", {})}
                    disabled={lockRecords || disableMultiRetry() || isHistoricalRequest}
                    style={
                      lockRecords || disableMultiRetry() ? { pointerEvents: "none" } : {}
                    }
                  >
                    <FontAwesomeIcon icon={faRotate} size="lg" color="#38598A" />
                  </button>
                </span>
              </Tooltip>
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
              {isRecordsfetching === "completed" && records?.length > 0 ? (
                records?.map((record, i) => (
                  <Attachment
                    key={i}
                    indexValue={i}
                    record={record}
                    handlePopupButtonClick={handlePopupButtonClick}
                    getFullname={getFullname}
                    isMinistryCoordinator={isMinistryCoordinator}
                    ministryId={ministryId}
                    classes={classes}
                    handleSelectRecord={handleSelectRecord}
                    setDivisionsModalOpen={setDivisionsModalOpen}
                    isMCFPersonal={isMCFPersonal}
                    setEditTagModalOpen={setEditTagModalOpen}
                    setCurrentEditRecord={setCurrentEditRecord}
                    isHistoricalRequest={isHistoricalRequest}
                    lockRecords={lockRecords}
                  />
                ))
              ) : (
                <div className="recordsstatus">
                  {isRecordsfetching === "inprogress"
                    ? "Records loading is in progress, please wait!"
                    : isRecordsfetching === "completed" &&
                      (records?.length === 0 ||
                        records === null ||
                        records === undefined)
                    ? "No records are available to list, please confirm whether records are uploaded or not"
                    : isRecordsfetching === "error"
                    ? "Error fetching records, please try again."
                    : { isRecordsfetching }}
                </div>
              )}
            </Grid>
          </Grid>

          {!isHistoricalRequest && <AttachmentModal
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
            divisions={divisions.filter(
              (d) => d.divisionname.toLowerCase() !== "communications"
            )}
            totalUploadedRecordSize={totalUploadedRecordSize}
            replacementfiletypes={getreplacementfiletypes()}
            requestType={requestType}
            isScanningTeamMember={isScanningTeamMember}
            curPersonalAttributes={curPersonalAttributes}
          />}
          <div className="state-change-dialog">
            <Dialog
              open={deleteModalOpen}
              onClose={() => {
                setDeleteModalOpen(false);
                setDivisionModalTagValue(-1);
              }}
              aria-labelledby="state-change-dialog-title"
              aria-describedby="state-change-dialog-description"
              maxWidth={"md"}
              fullWidth={true}
              // id="state-change-dialog"
            >
              <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Remove Attachments</h2>
                <IconButton
                  className="title-col3"
                  onClick={() => {
                    setDeleteModalOpen(false);
                    setDivisionModalTagValue(-1);
                  }}
                >
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
              <DialogContent className={"dialog-content-nomargin"}>
                <DialogContentText
                  id="state-change-dialog-description"
                  component={"span"}
                  style={{ textAlign: "center" }}
                >
                  <span className="confirmation-message">
                    Are you sure you want to delete the attachments from this
                    request? <br></br>
                    <i>
                      This will remove all attachments from the redaction app.
                    </i>
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
                <button
                  className="btn-bottom btn-cancel"
                  onClick={() => {
                    setDeleteModalOpen(false);
                    setDivisionModalTagValue(-1);
                  }}
                >
                  Cancel
                </button>
              </DialogActions>
            </Dialog>
          </div>

          {isMCFPersonal?(
            <MCFPersonal
              editTagModalOpen={editTagModalOpen}
              setEditTagModalOpen={setEditTagModalOpen}
              record={currentEditRecord}
              setNewDivision={setDivisionModalTagValue}
              comparePersonalAttributes={comparePersonalAttributes}
              curPersonalAttributes={curPersonalAttributes}
              setNewPersonalAttributes={setNewPersonalAttributes}
              updatePersonalAttributes={updatePersonalAttributes}
              setCurrentEditRecord={setCurrentEditRecord}
              setCurPersonalAttributes={setCurPersonalAttributes}
              divisionModalTagValue={divisionModalTagValue}
              divisions={divisions}
              isMinistryCoordinator={isMinistryCoordinator}
              currentEditRecord={currentEditRecord}
              isBulkEdit={isBulkEdit}
            />
          ):(
            <div className="state-change-dialog">
            <Dialog
              open={divisionsModalOpen}
              onClose={() => setDivisionsModalOpen(false)}
              aria-labelledby="state-change-dialog-title"
              aria-describedby="state-change-dialog-description"
              maxWidth={"md"}
              fullWidth={true}
              // id="state-change-dialog"
            >
              <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Update Divisions</h2>
                <IconButton
                  className="title-col3"
                  onClick={() => setDivisionsModalOpen(false)}
                >
                  <i className="dialog-close-button">Close</i>
                  <CloseIcon />
                </IconButton>
              </DialogTitle>
              <DialogContent className={"dialog-content-nomargin"}>
                <DialogContentText
                  id="state-change-dialog-description"
                  component={"span"}
                >
                  {records.filter(
                    (r) => r.isselected && r.attributes.divisions?.length > 1
                  ).length > 0 && filterValue < 0 ? (
                    <div className="tagtitle">
                      <span>
                        You have selected a record that was provided by more
                        than one division. <br></br>
                        To change the division you must first filter the Records
                        Log by the division that you want to no longer be
                        associated with the selected records.
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="tagtitle">
                        <span>
                          Select the divisions that corresponds to the records
                          you have selected.<br></br>
                          This will update the divisions on all records you have
                          selected both in the gathering records log and the
                          redaction app.
                        </span>
                      </div>

                      {requestType ==
                      FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ? (
                        bcgovcode == "MSD" ? (
                          <MSDPersonal
                            setNewDivision={setDivisionModalTagValue}
                            tagValue={
                              records.filter((r) => r.isselected)[0]?.attributes
                                .divisions[0].divisionid
                            }
                            divisionModalTagValue={divisionModalTagValue}
                            divisions={tagList}
                          />
                        ) : (
                          <div className="taglist">
                            {divisions?.filter((division) => {
                                if (
                                  division.divisionname.toLowerCase() ===
                                  "communications"
                                ) {
                                  return false;
                                } else if (
                                  filterValue > -1 &&
                                  filterValue !== division.divisionid
                                ) {
                                  return true;
                                } else if (
                                  records.filter((r) => r.isselected)[0]
                                    ?.attributes.divisions[0].divisionid !==
                                  division.divisionid
                                ) {
                                  return true;
                                } else {
                                  return false;
                                }
                              })
                              .map((division) => (
                                <ClickableChip
                                  item
                                  id={`${division.divisionid}updateTag`}
                                  key={`${division.divisionid}-updateTag`}
                                  label={division.divisionname.toUpperCase()}
                                  sx={{
                                    width: "fit-content",
                                    marginLeft: "8px",
                                    marginBottom: "8px",
                                  }}
                                  color={
                                    division.divisionid === -2
                                      ? "#A0192F"
                                      : division.divisionid === -3
                                      ? "#B57808"
                                      : "primary"
                                  }
                                  size="small"
                                  onClick={(e) => {
                                    setDivisionModalTagValue(
                                      division.divisionid
                                    );
                                  }}
                                  clicked={
                                    divisionModalTagValue ===
                                    division.divisionid
                                  }
                                />
                              ))}
                          </div>
                        )
                      ) : (
                        <div className="taglist">
                          {divisions?.filter((division) => {
                              if (
                                division.divisionname.toLowerCase() ===
                                "communications"
                              ) {
                                return false;
                              } else if (
                                filterValue > -1 &&
                                filterValue !== division.divisionid
                              ) {
                                return true;
                              } else if (
                                records.filter((r) => r.isselected)[0]
                                  ?.attributes.divisions[0].divisionid !==
                                division.divisionid
                              ) {
                                return true;
                              } else {
                                return false;
                              }
                            })
                            .map((division) => (
                              <ClickableChip
                                item
                                id={`${division.divisionid}updateTag`}
                                key={`${division.divisionid}-updateTag`}
                                label={division.divisionname.toUpperCase()}
                                sx={{
                                  width: "fit-content",
                                  marginLeft: "8px",
                                  marginBottom: "8px",
                                }}
                                color={
                                  division.divisionid === -2
                                    ? "#A0192F"
                                    : division.divisionid === -3
                                    ? "#B57808"
                                    : "primary"
                                }
                                size="small"
                                onClick={(e) => {
                                  setDivisionModalTagValue(division.divisionid);
                                }}
                                clicked={
                                  divisionModalTagValue === division.divisionid
                                }
                              />
                            ))}
                        </div>
                      )}
                    </>
                  )}
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <button
                  className={`btn-bottom btn-save btn`}
                  onClick={updateDivisions}
                  disabled={divisionModalTagValue === -1}
                >
                  Continue
                </button>
                <button
                  className="btn-bottom btn-cancel"
                  onClick={() => setDivisionsModalOpen(false)}
                >
                  Cancel
                </button>
              </DialogActions>
            </Dialog>
          </div>
          )}
        </>
      )}
    </div>
  );
};

const Attachment = React.memo(
  ({
    indexValue,
    record,
    handlePopupButtonClick,
    getFullname,
    isMinistryCoordinator,
    ministryId,
    handleSelectRecord,
    setDivisionsModalOpen,
    isMCFPersonal,
    setEditTagModalOpen,
    setCurrentEditRecord,
    isHistoricalRequest,
    lockRecords
  }) => {
    const classes = useStyles();
    const [disabled, setDisabled] = useState(false);
    const [isRetry, setRetry] = useState(false);
    const removePersonalTagsFromDivisions = record.attributes?.divisions?.filter(
      (division) => {
        return !record.attributes?.personalattributes?.personaltag || (record.attributes?.personalattributes?.personaltag && division.divisionname != record.attributes?.personalattributes?.personaltag);
      }) || [];
    const removeInValidTagsFromDivisions = record.attributes?.divisions?.filter(
      (division) => {
        return division.divisionname != "TBD";
      });

    // useEffect(() => {
    //   if(record && record.filename) {
    //     setDisabled(isMinistryCoordinator && record.category == 'personal')
    //   }
    // }, [record])

    const getCategory = (category) => {
      return AttachmentCategories.categorys.find(
        (element) => element.name === category
      );
    };

    const handleSelect = (e) => {
      handleSelectRecord(record, e);
    };

    const recordtitle = () => {
      if (disabled) {
        return (
          <div className="record-name record-disabled">{record.filename}</div>
        );
      }

      if (
        record.filename.toLowerCase().indexOf(".eml") > 0 ||
        record.filename.toLowerCase().indexOf(".msg") > 0 ||
        record.filename.toLowerCase().indexOf(".txt") > 0
      ) {
        return (
          <div
            className="record-name viewrecord"
            onClick={() => handlePopupButtonClick("download", record)}
          >
            {record.filename}
          </div>
        );
      } else {
        return (
          <div
            onClick={() => {
              opendocumentintab(record, ministryId);
            }}
            className="record-name viewrecord"
          >
            {record.filename}
          </div>
        );
      }
    };

    const showCompressedTag= (record)=> {
      /**TODO: Create ENUM for document processes */
      if (record.iscompressed && (!record.selectedfileprocessversion 
        || record.selectedfileprocessversion != 1 ))
        return true;
      return false;
    }

    const showOCRTag= (record)=> {
      if (record.ocrfilepath != null && (!record.selectedfileprocessversion 
        || record.selectedfileprocessversion != 2 ))
        return true;
      return false;
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
          <Grid item container xs={9} direction="row" alignItems="flex-start">
            <input
              type="checkbox"
              style={{ position: "relative", top: 18, marginRight: 15 }}
              className="checkmark record-checkmark"
              id={"selectchk" + record.documentmasterid}
              key={record.recordid + indexValue}
              data-iaocode={record.recordid}
              onChange={handleSelect}
              required
              checked={record.isselected}
              // defaultChecked={record.isselected}
            />
            {record.isattachment && (
              <FontAwesomeIcon
                icon={faArrowTurnUp}
                size="2x"
                className={classes.attachmentIcon}
              />
            )}
            {record.isduplicate ? (
              <FontAwesomeIcon
                icon={faClone}
                size="2x"
                color="#FF873D"
                className={classes.statusIcons}
              />
            ) : record.attributes?.incompatible &&
              record.attributes?.trigger !== "recordreplace" ? (
              <FontAwesomeIcon
                icon={faBan}
                size="2x"
                color="#FAA915"
                className={classes.statusIcons}
              />
            ) : record.isredactionready || record.selectedfileprocessversion? (
              <FontAwesomeIcon
                icon={faCheckCircle}
                size="2x"
                color="#1B8103"
                className={classes.statusIcons}
              />
            ) : record.failed && !record.selectedfileprocessversion ? (
              <FontAwesomeIcon
                icon={faExclamationCircle}
                size="2x"
                color="#A0192F"
                className={classes.statusIcons}
              />
            ) : isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) ==
                true && isRetry == false && !record.selectedfileprocessversion? (
              <FontAwesomeIcon
                icon={faExclamationCircle}
                size="2x"
                color="#A0192F"
                className={classes.statusIcons}
              />
            ) : (
              <FontAwesomeIcon
                icon={faSpinner}
                size="2x"
                color="#FAA915"
                className={classes.statusIcons}
              />
            )}
            <span title={record.filename} className={classes.filename}>
              {record.filename}{" "}
            </span>
            {/* <span className={classes.fileSize}>
              {record?.attributes?.filesize > 0
                ? (record?.attributes?.filesize / 1024).toFixed(2)
                : 0}{" "}
              KB -orginal
            </span> */}
            <span className={classes.fileSize}>
            {(
              (record?.selectedfileprocessversion == 1 ? record?.attributes?.filesize :
                record?.attributes?.ocrfilesize ? record?.attributes?.ocrfilesize 
                : record?.attributes?.compressedfilesize 
                ?? record?.attributes?.filesize ?? 0) / 1024
            ).toFixed(2)} KB
          </span>
          </Grid>
          <Grid
            item
            xs={3}
            direction="row"
            justifyContent="flex-end"
            alignItems="flex-end"
            className={classes.recordStatus}
          >
            { isHistoricalRequest ? <></>
              : record.isduplicate ? (
              <span>Duplicate of {record.duplicateof}</span>
            ) : record.attributes?.incompatible &&
              record.attributes?.trigger !== "recordreplace" ? (
              <span>Incompatible File Type</span>
            ) : (record.failed && record.isredactionready) ||
              (record.attributes?.trigger === "recordreplace" &&
                record.attributes?.isattachment) ? (
              <span>Record Manually Replaced Due to Error</span>
            ) : record.attributes?.isattachment ? (
              <span
                style={{
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={record.failed && !record.selectedfileprocessversion? `Error during ${record.failed}` : `Attachment of ${record.attachmentof}`}
              >
                {record.failed && !record.selectedfileprocessversion? `Error during ${record.failed}` : `Attachment of ${record.attachmentof}`}
              </span>
            ) : record.isredactionready || record.selectedfileprocessversion ? (
              <span>Ready for Redaction</span>
            ) : record.failed && !record.selectedfileprocessversion? (
              <span>Error during {record.failed}</span>
            ) : isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) ==
                true && isRetry == false && !record.selectedfileprocessversion ? (
              <span>Error due to timeout</span>
            ) : !record.isdedupecomplete?(
              <span>Deduplication & file conversion in progress</span>
            ): !record.iscompressed ? (
              <span>Compression in progress</span>
            ) : (
              <span>OCR in progress</span>
            )}
            <AttachmentPopup
              indexValue={indexValue}
              record={record}
              handlePopupButtonClick={handlePopupButtonClick}
              disabled={disabled}
              ministryId={ministryId}
              setRetry={setRetry}
              lockRecords={lockRecords}
              setEditTagModalOpen={setEditTagModalOpen}
              isMCFPersonal={isMCFPersonal}
              isMinistryCoordinator={isMinistryCoordinator}
              setCurrentEditRecord={setCurrentEditRecord}
              isHistoricalRequest={isHistoricalRequest}
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
            {removeInValidTagsFromDivisions?.length > 0 && removeInValidTagsFromDivisions?.map((division, i) => (
              <Chip
                item
                key={i}
                label={division.divisionname}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin:
                    record.isattachment && i === 0
                      ? "4px 4px 4px 95px"
                      : i === 0
                      ? "4px 4px 4px 35px"
                      : "4px",
                }}
              />
            ))}
            {record.attributes?.personalattributes?.person && 
              <Chip
                item
                key={record.attributes?.divisions?.length + 1}
                label={record.attributes.personalattributes.person}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin:
                    record.isattachment && removeInValidTagsFromDivisions?.length === 0
                      ? "4px 4px 4px 95px"
                      : removeInValidTagsFromDivisions?.length === 0
                      ? "4px 4px 4px 35px"
                      : "4px",
                }}
              />
            }
            {record.attributes?.personalattributes?.filetype && 
              <Chip
                item
                key={record.attributes?.divisions?.length + 2}
                label={record.attributes.personalattributes.filetype}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin: "4px",
                }}
              />
            }
            {record.attributes?.personalattributes?.volume && 
              <Chip
                item
                key={record.attributes?.divisions?.length + 3}
                label={record.attributes.personalattributes.volume}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin: "4px",
                }}
              />
            }
            {record.attributes?.personalattributes?.trackingid && 
              <Chip
                item
                key={record.attributes?.divisions?.length + 4}
                label={record.attributes.personalattributes.trackingid}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin: "4px",
                }}
              />
            }
            {record.attributes?.personalattributes?.personaltag && 
              <Chip
                item
                key={record.attributes?.divisions?.length + 5}
                label={record.attributes.personalattributes.personaltag}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  backgroundColor: "#003366",
                  margin: "4px",
                }}
              />
            }
              <Chip
                key={record.recordid}
                icon={
                  <FontAwesomeIcon
                    icon={showCompressedTag(record) ? faMinimize : faMaximize}
                    size="sm"
                    style={{
                      color:"#38598A",
                    }}
                  />
                }
                label={showCompressedTag(record) ? "Compressed" : "Uncompressed"}
                size="small"
                className={clsx(classes.chip, classes.chipPrimary)}
                style={{
                  color: "#003366",
                  backgroundColor:"#fff",
                  border: "1px solid #38598A",
                  margin: "4px 10px",
                }}
              />
          </Grid>

          <Grid
            item
            xs={2}
            direction="row"
            justifyContent="flex-end"
            alignItems="flex-end"
            className={classes.createBy}
          >
            <div
              className={`record-owner ${disabled ? "record-disabled" : ""}`}
            >
              {getFullname(record.createdby)}
            </div>
          </Grid>
          <Grid
            item
            xs={4}
            direction="row"
            justifyContent="flex-end"
            alignItems="flex-end"
            className={classes.createDate}
          >
            <div className="record-time">{record.created_at}</div>
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
        {record.attachments?.map((attachment, i) => (
          <Attachment
            key={"attachment" + i}
            indexValue={i}
            record={attachment}
            handlePopupButtonClick={handlePopupButtonClick}
            getFullname={getFullname}
            isMinistryCoordinator={isMinistryCoordinator}
            ministryId={ministryId}
            classes={classes}
            handleSelectRecord={handleSelectRecord}
            lockRecords={lockRecords}
            isMCFPersonal={isMCFPersonal}
            setEditTagModalOpen={setEditTagModalOpen}
            setCurrentEditRecord={setCurrentEditRecord}
          />
        ))}
      </>
    );
  }
);

const opendocumentintab = (record, ministryId) => {
  let relativedocpath = record.documentpath.split("/").slice(4).join("/");
  let url = `/foidocument?id=${ministryId}&filepath=${relativedocpath}`;
  window.open(url, "_blank").focus();
};

const AttachmentPopup = React.memo(
  ({
    indexValue,
    record,
    handlePopupButtonClick,
    disabled,
    ministryId,
    setRetry,
    lockRecords,
    setEditTagModalOpen,
    isMCFPersonal,
    isMinistryCoordinator,
    setCurrentEditRecord,
    isHistoricalRequest,
  }) => {
    const ref = React.useRef();
    const closeTooltip = () => (ref.current && ref ? ref.current.close() : {});

    const handleRename = () => {
      closeTooltip();
      handlePopupButtonClick("rename", record);
    };

    const handleRetrieveFileVersion = (retrieveVersion, record) => {
      closeTooltip();
      handlePopupButtonClick(retrieveVersion, record);
    };

    const handleReplace = () => {
      closeTooltip();
      handlePopupButtonClick("replace", record);
    };

    const handleReplaceAttachment = () => {
      closeTooltip();
      handlePopupButtonClick("replaceattachment", record);
    };

    const handleDownload = () => {
      closeTooltip();
      handlePopupButtonClick("download", record);
    };

    const handleDownloadPDF = () => {
      closeTooltip();
      handlePopupButtonClick("downloadPDF", record);
    };

    const handleDownloadoriginal = () => {
      closeTooltip();
      handlePopupButtonClick("downloadoriginal", record);
    };

    const handleView = () => {
      closeTooltip();
      opendocumentintab(record, ministryId);
    };

    const handleDelete = () => {
      closeTooltip();
      handlePopupButtonClick("delete", record);
    };

    const handleRetry = (record) => {
      setRetry(true);
      closeTooltip();
      handlePopupButtonClick("retry", record);
    };

    const transitionStates = [
      "statetransition",
      StateTransitionCategories.cfrreview.name,
      StateTransitionCategories.cfrfeeassessed.name,
      StateTransitionCategories.signoffresponse.name,
      StateTransitionCategories.harmsreview.name,
    ];

    const showReplace = (category) => {
      return transitionStates.includes(category.toLowerCase());
    };
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
      );
    };

    const ActionsPopover = ({
      RestrictViewInBrowser,
      record,
      setEditTagModalOpen,
      isMCFPersonal,
      isMinistryCoordinator,
      isHistoricalRequest,
      lockRecords
    }) => {
      const isUploadedByMinistryUser = (record) => {
        return hasValidDivisions(record);
      };

      const hasValidDivisions = (record) => {
        return record.attributes.divisions.length > 0 && record.attributes.divisions[0].divisionname != "TBD"
      };

      const disableMinistryUser = isMCFPersonal && isMinistryCoordinator && !isUploadedByMinistryUser(record);

      const DeleteMenu = () => {
        return (
          <MenuItem
          style={ (lockRecords || disableMinistryUser) ? { pointerEvents: "none" } : {} }
            disabled={lockRecords || disableMinistryUser}
            onClick={() => {
              handleDelete();
              setPopoverOpen(false);
            }}
          >
            Delete
          </MenuItem>
        );
      };

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
            {isMCFPersonal && (
              <MenuItem
                disabled={lockRecords || disableMinistryUser}
                onClick={() => {
                  setEditTagModalOpen(true);
                  setPopoverOpen(false);
                }}
              >
                Edit Tags
              </MenuItem>
            )}
            {!RestrictViewInBrowser ? (
              <MenuItem
                onClick={() => {
                  handleView();
                  setPopoverOpen(false);
                }}
              >
                View
              </MenuItem>
            ) : (
              ""
            )}
            {!isHistoricalRequest && !record.selectedfileprocessversion && 
              !record.attributes?.incompatible && (
              <MenuItem
                disabled={lockRecords || disableMinistryUser}
                onClick={() => {
                  handleRetrieveFileVersion("retrieve_uncompressed", record);
                  setPopoverOpen(false);
                }}
              >
                Retrieve Uncompressed
              </MenuItem>
            )}
            {(!record.attributes?.isattachment ||
              record.attributes?.isattachment === undefined) && !isHistoricalRequest && (
              <MenuItem
                disabled={lockRecords || disableMinistryUser}
                onClick={() => {
                  handleReplace();
                  setPopoverOpen(false);
                }}
              >
                Replace Manually
              </MenuItem>
            )}
            {record.attributes?.isattachment && (
              <MenuItem
                disabled={lockRecords || disableMinistryUser}
                onClick={() => {
                  handleReplaceAttachment();
                  setPopoverOpen(false);
                }}
              >
                Replace Attachment
              </MenuItem>
            )}
            {record.originalfile != "" && record.originalfile != undefined && (
              <MenuItem
                onClick={() => {
                  handleDownloadoriginal();
                  setPopoverOpen(false);
                }}
              >
                Download Original
              </MenuItem>
            )}
            {((record.isredactionready && record.isconverted) ||
              (record.attributes?.isattachment &&
                record.attributes?.trigger === "recordreplace")) && (
              <MenuItem
                onClick={() => {
                  handleDownloadPDF();
                  setPopoverOpen(false);
                }}
              >
                {record.attributes?.isattachment &&
                record.attributes?.trigger === "recordreplace"
                  ? "Download Replaced"
                  : "Download Converted"}
              </MenuItem>
            )}
            <MenuItem
              onClick={() => {
                handleDownload();
                setPopoverOpen(false);
              }}
            >
              {record.originalfile != "" && record.originalfile != undefined
                ? "Download Replaced"
                : record.attributes?.isattachment
                ? "Download Original"
                : "Download"}
            </MenuItem>
            {!record.isattachment && !isHistoricalRequest && <DeleteMenu />}
            {!record.isredactionready && !record.selectedfileprocessversion &&
              (record.failed ||
                isrecordtimeout(record.created_at, RECORD_PROCESSING_HRS) ==
                  true) && (
                <MenuItem
                  onClick={() => {
                    handleRetry(record);
                    setPopoverOpen(false);
                  }}
                >
                  Re-Try
                </MenuItem>
              )}

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
          aria-label="actions"
          id={`ellipse-icon-${indexValue}`}
          key={`ellipse-icon-${indexValue}`}
          color="primary"
          disabled={disabled}
          onClick={(e) => {
            setCurrentEditRecord(record);
            setPopoverOpen(true);
            setAnchorPosition(e?.currentTarget?.getBoundingClientRect());
          }}
        >
          <MoreHorizIcon />
        </IconButton>
        <ActionsPopover
          RestrictViewInBrowser={true}
          record={record}
          setEditTagModalOpen={setEditTagModalOpen}
          isMCFPersonal={isMCFPersonal}
          isMinistryCoordinator={isMinistryCoordinator}
          isHistoricalRequest={isHistoricalRequest}
          lockRecords={lockRecords}
        />
      </>
    );
  }
);

export default RecordsLog;
