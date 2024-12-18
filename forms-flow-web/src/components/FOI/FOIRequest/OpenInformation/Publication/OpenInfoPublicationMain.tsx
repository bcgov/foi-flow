import {
  Grid,
  TextField,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Typography,
  MenuItem,
  Radio,
  RadioGroup,
  FormControlLabel,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { makeStyles } from "@material-ui/styles";
import { formatDate } from "../../../../../helper/FOI/helper";
import { useDispatch, useSelector } from "react-redux";
import FilePreviewContainer from "../../../customComponents/FileUpload/FilePreviewContainer";
import clsx from "clsx";
import { useState, useEffect } from "react";
import { deleteFOIOpenInfoAdditionalFiles, fetchFOIOpenInfoAdditionalFiles, saveFOIOpenInfoAdditionalFiles } from "../../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { setFOILoader } from "../../../../../actions/FOI/foiRequestActions";
import AttachmentModal from "../../../customComponents/Attachments/AttachmentModal";
import {
  saveFilesinS3,
  postFOIS3DocumentPreSignedUrl,
  completeMultiPartUpload,
} from "../../../../../apiManager/services/FOI/foiOSSServices";
import { toast } from "react-toastify";
import { readUploadedFileAsBytes } from "../../../../../helper/FOI/helper";
import { OSS_S3_CHUNK_SIZE } from "../../../../../constants/constants";

type OIPublicationStatus = {
  oipublicationstatusid: number;
  name: string;
  isactive: boolean;
};

const OpenInfoPublicationMain = ({
  requestId,
  ministryId,
  oiPublicationData,
  currentOIRequestState,
  handleOIDataChange,
  bcgovcode,
  requestNumber,
}: any) => {  
  const dispatch = useDispatch();

  //App State
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );
  let foiOpenInfoAdditionalFiles = useSelector(
    (state: any) => state.foiRequests.foiOpenInfoAdditionalFiles
  );

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
  }, [foiOpenInfoAdditionalFiles])

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
            console.log("Error while deleting additional files, please try again")
          }
        }
      )
    );
  }

  const handleModal = (value: any, fileInfoList: any, files: any) => {
    console.log(value)
    console.log(fileInfoList)
    console.log(files)
    setOpenModal(false)
    if (value) {
      saveDocument(value, fileInfoList, files)
    }
  }

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
                  ")"
              );
              for (let header of res) {
                const _file = files.find(
                  (file: any) => file.filename === header.filename
                );
                const _fileInfo = fileInfoList.find(
                  (fileInfo: any) => fileInfo.filename === header.filename
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
                    (chunk + 1) * CHUNK_SIZE
                  );
                  let response: any = await saveFilesinS3(
                    { filepath: header.filepaths[chunk] },
                    CHUNK,
                    dispatch,
                    (_err: any, _res: any) => {
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
                  }
                );
              }
              if (_documents.length > 0) {
                dispatch(
                  saveFOIOpenInfoAdditionalFiles(
                    requestId,
                    ministryId,
                    { additionalfiles: _documents },
                    (err: any, _res: any) => {
                      dispatch(fetchFOIOpenInfoAdditionalFiles(requestId, ministryId));
                    }
                  )
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
            }
          }
        );
      }
    }
  };

  const openDocuemnt = (index: any) => {    
    let file: any = additionalFiles[index];
    let filepath = file.s3uripath.split("/").slice(4).join("/");
    let url = `/foidocument?id=${ministryId}&filepath=${filepath}&filetype=additionalfiles&bcgovcode=${bcgovcode}`;
    window.open(url, "_blank")?.focus();
  }

  const disableUserInput = !oiPublicationData?.oiexemptionapproved && oiPublicationData.oipublicationstatus_id === 1;

  return (
    <div className="request-accordian">
      <Accordion defaultExpanded={true}>
        <AccordionSummary
          className={classes.accordionSummary}
          expandIcon={<ExpandMoreIcon />}
        >
          <Typography className={classes.heading}>
            PUBLICATION DETAILS
          </Typography>
        </AccordionSummary>
        <AccordionDetails className={classes.accordionDetails}>
          <Grid container spacing={3}>
            <Grid item md={6}>
              <TextField
                fullWidth
                name="oipublicationstatus_id"
                label="Publication Status"
                variant="outlined"
                value={oiPublicationData?.oipublicationstatus_id === 1 ? 2 : oiPublicationData?.oipublicationstatus_id}
                select
                disabled={disableUserInput}
                required
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
              >
                {oiPublicationStatuses.map((status) => {
                  if (status.oipublicationstatusid === 1) {
                    return null;
                  }
                  return (
                    <MenuItem
                      key={status.oipublicationstatusid}
                      value={status.oipublicationstatusid}
                    >
                      {status.name}
                    </MenuItem>
                  );
                })}
              </TextField>
            </Grid>
            <Grid item md={6}>
              <TextField
                fullWidth
                name="publicationdate"
                label="Publication Date"
                variant="outlined"
                disabled={disableUserInput || ["OI Review", "Exemption Request", "Do Not Publish", "Publication Review"].includes(currentOIRequestState)}
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                value={oiPublicationData?.publicationdate ? formatDate(new Date(oiPublicationData?.publicationdate)) : ""}
                type="date"
              ></TextField>
            </Grid>
            <Grid item md={6}>
              <RadioGroup
                row
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
              >
                <FormControlLabel
                  disabled={disableUserInput}
                  value={true}
                  name="copyrightsevered"
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(true, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.copyrightsevered === true}
                    />
                  }
                  label="Copyright Severed"
                />
                <FormControlLabel
                  disabled={disableUserInput}
                  value={false}
                  name="copyrightsevered"
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(false, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.copyrightsevered === false}
                    />
                  }
                  label="No Copyright"
                />
              </RadioGroup>
            </Grid>
          </Grid>
          {!disableUserInput &&         
          <div className="oi-main-text">
          <section
            className={clsx("file-upload-container")}
            style={{padding: 0}}
          >
            <div
              className={clsx("row", "file-upload-preview")}              
              style={{margin: 0, width: "100%"}}
            >
              <div className="file-upload-column">
                {(
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
              <div className="file-upload-column file-upload-column-2">
                {/* <input
                id="fileupload"
                aria-label="fileUpload"
                className={"file-upload-input-multiple"}
                type="file"
                ref={fileInputField}
                onChange={handleNewFileUpload}
                value=""
                multiple={multipleFiles}
                accept={mimeTypes}
                /> */}
              </div>
              <div className="file-upload-column file-upload-column-3">
                {
                <button className="btn-add-files" type="button" 
                onClick={() => setOpenModal(true)}
                >              
                      Add Files
                </button>}
              </div>
            </div>
          </section>
          </div>
          }
        </AccordionDetails>
      </Accordion>
      <AttachmentModal
        modalFor={"add"}
        openModal={openModal}
        handleModal={handleModal}
        multipleFiles={true}
        requestNumber={requestNumber}
        requestId={requestId}
        attachmentsArray={[]}
        existingDocuments={[]}
        attachment={{}}
        handleRename={undefined}
        handleReclassify={undefined}
        isMinistryCoordinator={false}
        uploadFor={"additionalFiles"}
        maxNoFiles={10}
        bcgovcode={bcgovcode}
      />
    </div>
  );
};

export default OpenInfoPublicationMain;
