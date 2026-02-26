import {
  Grid,
  TextField,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Typography,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { makeStyles } from "@material-ui/styles";
import { useDispatch, useSelector } from "react-redux";
import FilePreviewContainer from "../../../customComponents/FileUpload/FilePreviewContainer";
import clsx from "clsx";
import { useState, useEffect } from "react";
import {
  deleteFOIOpenInfoAdditionalFiles,
  fetchFOIOpenInfoAdditionalFiles,
  saveFOIOpenInfoAdditionalFiles,
} from "../../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { setFOILoader } from "../../../../../actions/FOI/foiRequestActions";
import AttachmentModal from "../../../customComponents/Attachments/AttachmentModal";
import {
  saveFilesinS3,
  getFileFromS3,
  postFOIS3DocumentPreSignedUrl,
  getFOIS3DocumentPreSignedUrl,
  completeMultiPartUpload,
} from "../../../../../apiManager/services/FOI/foiOSSServices";
import { toast } from "react-toastify";
import {
  readUploadedFileAsBytes,
  formatDate,
} from "../../../../../helper/FOI/helper";
import { OSS_S3_CHUNK_SIZE } from "../../../../../constants/constants";
import { RecordDownloadStatus } from "../../../../../constants/FOI/enum";
import Tooltip from "@mui/material/Tooltip";
import { OIPublicationStatus } from "../../OpenInformation/types";
import { OIPublicationStatuses } from "../../../../../helper/openinfo-helper";
import "./proactivepublication.scss";


const ProactiveDisclosureRequestPublicationMain = ({
  requestId,
  ministryId,
  oiPublicationData,
  currentOIRequestState,
  handleOIDataChange,
  bcgovcode,
  requestNumber,
  earliestPublicationDate,
}: any) => {
  const dispatch = useDispatch();

  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses,
  );
  let foiOpenInfoAdditionalFiles = useSelector(
    (state: any) => state.foiRequests.foiOpenInfoAdditionalFiles,
  );

  let foiPDFStitchedOIPackage = useSelector(
    (state: any) => state.foiRequests.foiPDFStitchedOIPackage,
  );

  let foiPDFStitchStatusForOIPackage = useSelector(
    (state: any) => state.foiRequests.foiPDFStitchStatusForOIPackage,
  );

  const totalFileCount =
    (foiOpenInfoAdditionalFiles?.length || 0) +
    (foiPDFStitchedOIPackage?.finalpackagepath ? 1 : 0);

  const [downloadDisabled, setDownloadDisabled] = useState(true);
  const [packageCreatedAt, setPackageCreatedAt] = useState("N/A");

  useEffect(() => {
    if (foiPDFStitchStatusForOIPackage === RecordDownloadStatus.completed) {
      setDownloadDisabled(false);
    }
  }, [foiPDFStitchStatusForOIPackage]);

  useEffect(() => {
    setPackageCreatedAt(foiPDFStitchedOIPackage?.createdat_datetime || "N/A");
  }, [foiPDFStitchedOIPackage]);

  //Styling
  const useStyles = makeStyles({
    heading: {
      color: "#FFF",
      fontSize: "16px !important",
      fontWeight: "bold",
    },
    accordionSummary: {
      flexDirection: "row-reverse",
    },
    accordionDetails: {
      margin: "10px 0 10px 0",
    },
  });
  const classes = useStyles();

  //Local State
  const [additionalFiles, setAdditionalFiles] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useEffect(() => {
    setAdditionalFiles(foiOpenInfoAdditionalFiles);
  }, [foiOpenInfoAdditionalFiles]);

  //Functions
  const deleteFile = (_index: any) => {
    let file: any = additionalFiles[_index];
    dispatch(setFOILoader(true));
    dispatch(
      deleteFOIOpenInfoAdditionalFiles(
        requestId,
        ministryId,
        { fileids: [file.additionalfileid] },
        (err: any, _res: any) => {
          if (!err) {
            dispatch(fetchFOIOpenInfoAdditionalFiles(requestId, ministryId));
          } else {
            console.log(
              "Error while deleting additional files, please try again",
            );
          }
        },
      ),
    );
  };

  const handleModal = (value: any, fileInfoList: any, files: any) => {
    setOpenModal(false);
    if (value) {
      saveDocument(value, fileInfoList, files);
    }
  };

  const saveDocument = (value: any, fileInfoList: any, files: any) => {
    if (value) {
      if (files.length !== 0) {
        setFOILoader(true);
        postFOIS3DocumentPreSignedUrl(
          ministryId,
          fileInfoList.map((file: any) => ({ ...file, multipart: true })),
          "additionalfiles",
          bcgovcode,
          dispatch,
          async (err: any, res: any) => {
            let _documents: any = [];
            if (!err) {
              var completed = 0;
              let failed = [];
              const toastID = toast.loading(
                "Uploading files (" +
                completed +
                "/" +
                fileInfoList.length +
                ")",
              );
              for (let header of res) {
                const _file = files.find(
                  (file: any) => file.filename === header.filename,
                );
                const _fileInfo = fileInfoList.find(
                  (fileInfo: any) => fileInfo.filename === header.filename,
                );
                var documentDetails = {
                  s3uripath: header.filepathdb,
                  filename: header.filename,
                };
                let bytes = await readUploadedFileAsBytes(_file);
                const CHUNK_SIZE = OSS_S3_CHUNK_SIZE;
                const totalChunks = Math.ceil(bytes.byteLength / CHUNK_SIZE);
                let parts = [];
                for (let chunk = 0; chunk < totalChunks; chunk++) {
                  let CHUNK = bytes.slice(
                    chunk * CHUNK_SIZE,
                    (chunk + 1) * CHUNK_SIZE,
                  );
                  let response: any = await saveFilesinS3(
                    { filepath: header.filepaths[chunk] },
                    CHUNK,
                    dispatch,
                    (_err: any, _res: any) => {
                      if (_err) {
                        failed.push(header.filename);
                      }
                    },
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
                  "additionalfiles",
                  bcgovcode,
                  dispatch,
                  (_err: any, _res: any) => {
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
                  },
                );
              }
              if (_documents.length > 0) {
                dispatch(
                  saveFOIOpenInfoAdditionalFiles(
                    requestId,
                    ministryId,
                    { additionalfiles: _documents },
                    (err: any, _res: any) => {
                      dispatch(
                        fetchFOIOpenInfoAdditionalFiles(requestId, ministryId),
                      );
                    },
                  ),
                );
              }
              var toastOptions: any = {
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
              setFOILoader(false);
            } else {
              toast.error(err, {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
            }
          },
        );
      }
    }
  };

  const openDocuemnt = (index: any) => {
    let file: any = additionalFiles[index];
    let filepath = file.s3uripath.split("/").slice(4).join("/");
    let url = `/foidocument?id=${ministryId}&filepath=${filepath}&filetype=additionalfiles&bcgovcode=${bcgovcode}`;
    window.open(url, "_blank")?.focus();
  };

  const disableUserInput =
    oiPublicationData.oipublicationstatus_id ===
    OIPublicationStatuses.DoNotPublish;

  var saveAs = (blob: any, filename: any) => {
    const fileURL = URL.createObjectURL(blob);
    const downloadLink = document.createElement("a");
    downloadLink.href = fileURL;
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    URL.revokeObjectURL(fileURL);
  };

  const downloadPackage = () => {
    const toastID = toast.loading("Downloading file (0%)");
    const s3filepath = foiPDFStitchedOIPackage?.finalpackagepath;
    getFOIS3DocumentPreSignedUrl(
      s3filepath.split("/").slice(4).join("/"),
      ministryId,
      dispatch,
      (err: any, res: any) => {
        if (!err) {
          getFileFromS3(
            { filepath: res },
            (_err: any, response: any) => {
              let blob = new Blob([response.data], {
                type: "application/octet-stream",
              });
              const filename = requestNumber + ".zip";
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
            (progressEvent: any) => {
              toast.update(toastID, {
                render:
                  "Downloading file (" +
                  Math.floor(
                    (progressEvent.loaded / progressEvent.total) * 100,
                  ) +
                  "%)",
                isLoading: true,
              });
            },
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
      "additionalfiles",
      bcgovcode,
    );
  };

  return (
    <>
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className={classes.accordionSummary}
            expandIcon={<ExpandMoreIcon />}
          >
            <Typography className={classes.heading}>
              Publication Due Date
            </Typography>
          </AccordionSummary>
          <AccordionDetails className={classes.accordionDetails}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  name="publicationdate"
                  label="Earliest eligible publication date"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  fullWidth
                  value={
                    (earliestPublicationDate
                      ? formatDate(new Date(earliestPublicationDate))
                      : "") || ""
                  }
                  onChange={(event) =>
                    handleOIDataChange(event.target.value, event.target.name)
                  }
                  InputProps={{ inputProps: { min: formatDate(new Date()) } }}
                  disabled={
                    
                    disableUserInput ||
                    currentOIRequestState === "First Review" ||
                    currentOIRequestState === "Unopened"
                  }
                />
              </Grid>
              <Grid item xs={12}>
                <div
                  className="foi-publication-info-box"
                >
                  <i
                    className="fa fa-info-circle info-icon"
                  ></i>
                  <div>
                    <span className="info-title">
                      Automatic Publication Details
                    </span>
                    <span className="info-description">
                      Files will be published automatically at 1:00 PM on the
                      earliest eligible date unless you select an other date.
                    </span>
                  </div>
                </div>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className={classes.accordionSummary}
            expandIcon={<ExpandMoreIcon />}
          >
            <Typography className={classes.heading}>
              Files for Publication
            </Typography>
          </AccordionSummary>
          <AccordionDetails className={classes.accordionDetails}>
            <div className="pd-publication-files-container">
              <Typography className="files-heading">
                Files to be published: {totalFileCount}
              </Typography>
              <Typography className="files-description">
                Review the grouped PDF before publishing. Files located in
                “Records” will be published as a single PDF.
              </Typography>
              <button
                onClick={downloadPackage}
                disabled={downloadDisabled}
                className="pd-pdf-download-btn"
              >
                <i className="fa fa-download download-icon"></i>{" "}
                Download Combined PDF for Review
              </button>

              {!disableUserInput && (
                <>
                  <Typography className="files-heading">
                    Add Optional Files
                  </Typography>
                  <Typography className="files-description">
                    If you have any additional files you’d like to include in
                    this publication, you can add them using the add files
                    below.
                    <p>These files will be added alongside the ones you
                      previously uploaded.</p>
                  </Typography>

                  <section
                    className={clsx("file-upload-container", "pd-file-upload-section")}
                  >
                    <div
                      className={clsx(
                        "row",
                        "file-upload-preview",
                        "file-upload-row",
                        additionalFiles.length > 0 ? "justify-start" : "justify-between"
                      )}
                    >
                      <div
                        className="file-upload-column file-upload-col-grow"
                      >
                        {additionalFiles.length === 0 ? (
                          <span className="drag-drop-text">
                            Drag and drop attachments, or click Add Files
                          </span>
                        ) : (
                          <FilePreviewContainer
                            files={additionalFiles.map((f: any) => {
                              f.fileName = f.filename;
                              return f;
                            })}
                            removeFile={deleteFile}
                            clickHandler={openDocuemnt}
                          />
                        )}
                      </div>
                      <div className="file-upload-column file-upload-column-3">
                        <button
                          className="btn-add-files"
                          onClick={() => setOpenModal(true)}
                        // style={{
                        //   color: "#38598a",
                        //   borderColor: "#38598a",
                        //   textTransform: "none",
                        // }}
                        >
                          Add files
                        </button>
                      </div>
                    </div>
                  </section>
                </>
              )}
            </div>
          </AccordionDetails >
        </Accordion >
        <AttachmentModal
          modalFor={"add"}
          openModal={openModal}
          handleModal={handleModal}
          multipleFiles={true}
          requestNumber={requestNumber}
          requestId={requestId}
          attachmentsArray={additionalFiles}
          existingDocuments={[]}
          attachment={{}}
          handleRename={undefined}
          handleReclassify={undefined}
          isMinistryCoordinator={false}
          uploadFor={"additionalFiles"}
          maxNoFiles={10}
          bcgovcode={bcgovcode}
          handleChangeResponseDate={() => { }}
          handleChangeResponseTitle={() => { }}
          retrieveSelectedRecords={() => { }}
        />
      </div >
    </>
  );
};

export default ProactiveDisclosureRequestPublicationMain;
