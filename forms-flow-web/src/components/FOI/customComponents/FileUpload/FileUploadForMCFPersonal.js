import React, { useRef, useState, useEffect } from "react";
import { useSelector } from "react-redux";
import FilePreviewContainer from "./FilePreviewContainer";
import { countOccurrences, 
  generateNewFileName, 
  getErrorMessage, 
  allowedFileType, 
  allowedFileSize, 
  convertNestedObjectToArray, 
  convertBytesToMB } from "./util";
import {
  ClickableChip  
} from "../../Dashboard/utils";
import Stack from "@mui/material/Stack";
import "./FileUpload.scss";
import clsx from "clsx";
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@material-ui/core/IconButton";
import TextField from '@material-ui/core/TextField';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import _ from 'lodash';

const FileUploadForMCFPersonal = ({
    multipleFiles,
    mimeTypes,
    maxFileSize,
    totalFileSize,
    updateFilesCb,
    attchmentFileNameList,
    attachment,
    customFormat = {},
    existingDocuments = [],
    maxNumberOfFiles,
    modalFor,
    handleTagChange,
    tagValue,
    handlePersonalTagChange,
    personalTag,
    handlePersonChange,
    person,
    handleVolumeChange,
    volume,
    handleFileTypeChange,
    fileType,
    handleTrackingIDChange,
    trackingID,
    divisions = [],
    tagList = [],
    otherTagList = [],
    isMinistryCoordinator,
    uploadFor="attachment",
    totalUploadedRecordSize,
    totalRecordUploadLimit,
    isScanningTeamMember
}) => {
    const fileInputField = useRef(null);
    const [files, setFiles] = useState({ ...existingDocuments });    
    const [totalFileSizeCalculated, setTotalFileSize] = useState(0);
    const [errorMessage, setErrorMessage] = useState([]); 
    const [includeAttachments, setIncludeAttachments] = useState(true);
    const [searchValue, setSearchValue] = useState("");
    const [additionalTagList, setAdditionalTagList] = useState([]);
    const [showAdditionalTags, setShowAdditionalTags] = useState(false);

    const MCFPeople = useSelector(
      (state) => state.foiRequests.foiPersonalPeople
    );
    const MCFFiletypes = useSelector(
      (state) => state.foiRequests.foiPersonalFiletypes
    );
    const MCFVolumes = useSelector(
      (state) => state.foiRequests.foiPersonalVolumes
    );

    let recordsObj = useSelector((state) => state.foiRequests.foiRequestRecords);
    const [records, setRecords] = useState(recordsObj?.records);

    const [allPeople, setAllPeople] = useState(
      isMinistryCoordinator?MCFPeople?.people.filter((p)=>{return p.name !== 'PERSON 1'}):MCFPeople?.people.filter((p)=>{return p.name !== 'APPLICANT'})
    );
    const [allVolumes, setAllVolumes] = useState(MCFVolumes?.volumes);
    const [fileTypes, setFileTypes] = useState(MCFFiletypes?.filetypes.slice(0, 6));
    const [otherFileTypes, setOtherFileTypes] = useState(MCFFiletypes?.filetypes.slice(6, MCFFiletypes?.filetypes.length));
    const [people, setPeople] = useState(allPeople.slice(0, 5));
    const [volumes, setVolumes] = useState(allVolumes.slice(0, 5));
    const [showAllPeople, setShowAllPeople] = useState(false);
    const [showAllVolumes, setShowAllVolumes] = useState(false);
    const [fileTypeSearchValue, setFileTypeSearchValue] = useState("");
    const [additionalFileTypes, setAdditionalFileTypes] = useState([]);
    const [showAdditionalFileTypes, setShowAdditionalFileTypes] = useState(false);

    const [isPersonSelected, setIsPersonSelected] = useState(false);
    const [enableTrackingIDInput, setEnableTrackingIDInput] = useState(true);

    const handleUploadBtnClick = (e) => {
      e.stopPropagation();
      fileInputField.current.click();
    };
    const handleUploadAreaClick = () => {
      if (Object.entries(files).length === 0)
        fileInputField.current.click();
    };

    const handleDuplicateFiles = (file) => {
      let exists = false;
      let duplicateFileName = "";
      if (Object.entries(files).length > 0) {
        exists = Object.keys(files).some((k) => {
          return k.toLowerCase() === file.name.toLowerCase();
        });
      }
      if (exists) {
        duplicateFileName = file.name;
      }
      else if (attchmentFileNameList) {
        let countFileOccurrences = countOccurrences(file.name, attchmentFileNameList);
        if (countFileOccurrences > 0 && multipleFiles) {
          duplicateFileName = file.name;
        }
        else if (countFileOccurrences > 0 && !multipleFiles && (attachment == null || (attachment && attachment.filename.toLowerCase() !== file.name.toLowerCase()))) {
          const filename = file.name.split('.');
          const newFileName =  generateNewFileName(`${filename[0]}(${countFileOccurrences}).${filename[1]}`, file.name, attachment && attachment.filename, attchmentFileNameList);
          file.filename = newFileName;
          files[file.name] = file;          
        }
        else {
          files[file.name] = file;          
        }
      }
      else {
        files[file.name] = file;        
      }
      return duplicateFileName;
    }

    const addNewFiles = (newFiles) => {
      let _totalFileSizeInMB = totalFileSizeCalculated;
      let _duplicateFiles = [];
      let _typeErrorFiles = [];
      let _overSizedFiles = [];
      let removeFileSize = 0;
      let recordUploadLimitReached = false;
        for (let file of newFiles) {
          file.filename = file.name;
          const sizeInMB = convertBytesToMB(file.size);
          _totalFileSizeInMB += parseFloat(sizeInMB);
          if (allowedFileType(file, mimeTypes)) {
            if (allowedFileSize(_totalFileSizeInMB, multipleFiles, totalFileSize)) {
              if (sizeInMB <= maxFileSize) {
                if (totalUploadedRecordSize > 0) {
                  if (_totalFileSizeInMB + totalUploadedRecordSize <= totalRecordUploadLimit) {
                    recordUploadLimitReached = false;
                    const duplicateFileName = handleDuplicateFiles(file);
                    _duplicateFiles.push(duplicateFileName);
                  } else {
                    recordUploadLimitReached = true;
                    _totalFileSizeInMB -= parseFloat(sizeInMB);
                  }
                } else {
                  const duplicateFileName = handleDuplicateFiles(file);
                  _duplicateFiles.push(duplicateFileName);
                }
              } else {
                  _totalFileSizeInMB -= parseFloat(sizeInMB);
                  _overSizedFiles.push(file.name);
              }
            } else {
              removeFileSize = convertBytesToMB(file.size);
            }
          }
          else {
            _typeErrorFiles.push(file.name);
          }
        }
        setTotalFileSize(_totalFileSizeInMB);
        let errMsg = getErrorMessage(_duplicateFiles, _typeErrorFiles, _overSizedFiles, maxFileSize, multipleFiles, mimeTypes, recordUploadLimitReached, totalRecordUploadLimit);
        setErrorMessage(errMsg);
        return [{...files}, _totalFileSizeInMB, removeFileSize, errMsg];
    };

    const callUpdateFilesCb = (_files, errMsg) => {
        const filesAsArray = convertNestedObjectToArray(_files);
        updateFilesCb(filesAsArray, errMsg);
    };

    const validateFiles = (newFiles, totalFiles) => {
      
      if (multipleFiles && maxNumberOfFiles && (newFiles.length > maxNumberOfFiles  || totalFiles > maxNumberOfFiles)) {
        setErrorMessage([`A maximum of ${maxNumberOfFiles} files can be uploaded at one time. Only ${maxNumberOfFiles} files have been added on this upload window, please upload additional files separately`]);
      } else if (!multipleFiles && totalFiles > 1) {
        return
      } else if (newFiles.length) {
        let updatedFilesDetails = addNewFiles(newFiles);
        if (multipleFiles && updatedFilesDetails[1] > totalFileSize) {
          setTotalFileSize(updatedFilesDetails[1] - parseFloat(updatedFilesDetails[2]))
          setErrorMessage([`The total size of all files uploaded can not exceed  ${totalFileSize}MB. Please upload additional files separately.`]);
        }
        setFiles(updatedFilesDetails[0]);
        callUpdateFilesCb(updatedFilesDetails[0]);
      }
    }

    const handleNewFileUpload = (e) => {
      const { files: newFiles } = e.target;
      const totalFiles = Object.entries(files).length + newFiles.length;
      validateFiles(newFiles, totalFiles);
    };
    const fileDrop = (e) => {
      e.preventDefault();

      if(modalFor === "add" && (!isPersonSelected || ((isMinistryCoordinator && tagValue == "")))) {
        return
      } else {
        const newFiles = e.dataTransfer.files;
        const totalNoOfFiles = Object.entries(files).length + newFiles.length; 
        validateFiles(newFiles, totalNoOfFiles);
      }
    }
    const removeFile = (fileName) => {
        const _file = files[fileName];
        const sizeInMB = (_file.size / (1024*1024)).toFixed(2);
        setTotalFileSize(totalFileSizeCalculated - parseFloat(sizeInMB))
        delete files[fileName];
        setFiles({ ...files });
        callUpdateFilesCb({ ...files });
        setErrorMessage([]);
    };
    const dragOver = (e) => {
      e.preventDefault();
    }
  
    const dragEnter = (e) => {
        e.preventDefault();
    }
    
    const dragLeave = (e) => {
        e.preventDefault();
    }    
    
    const showDragandDrop = () => {
      if (Object.entries(files).length === 0)
        return "Drag and drop attachments, or click Add Files"
    }

    const searchSections = (_sectionArray, _keyword, _selectedSectionValue) => {
      let newSectionArray = [];
      if(_keyword || _selectedSectionValue) {
        _sectionArray.map((section) => {
          if(_keyword && section.name.toLowerCase().includes(_keyword.toLowerCase())) {
            newSectionArray.push(section);
          } else if(section.divisionid === _selectedSectionValue) {
            newSectionArray.unshift(section);
          }
        });
      }

      if(newSectionArray.length > 0) {
        setShowAdditionalTags(true);
      } else {
        setShowAdditionalTags(false);
      }
      return newSectionArray;
    }

    React.useEffect(() => {
      setIsPersonSelected(Object.keys(person).length !== 0 && Object.keys(fileType).length !== 0);
    },[person, fileType])

    React.useEffect(() => {
      setAdditionalTagList(searchSections(otherTagList, searchValue, personalTag));
    },[searchValue, otherTagList, personalTag])

    const handleTrackingIDUpdate = (e) => {
      handleTrackingIDChange(e.target.value);
    }

    const searchFileTypes = (_fileTypeArray, _keyword, _selectedFileType) => {
      let newFileTypeArray = [];
      if(_keyword || _selectedFileType) {
        _fileTypeArray.map((section) => {
          if(_keyword && section.name.toLowerCase().includes(_keyword.toLowerCase())) {
            newFileTypeArray.push(section);
          } else if(section.divisionid === _selectedFileType.divisionid) {
            newFileTypeArray.unshift(section);
          }
        });
      }

      if(newFileTypeArray.length > 0) {
        setShowAdditionalFileTypes(true);
      } else {
        setShowAdditionalFileTypes(false);
      }

      return newFileTypeArray;
    }

    React.useEffect(() => {
      if(showAllPeople) {
        setPeople(allPeople)
      } else {
        setPeople(allPeople.slice(0, 5))
      }
      if(showAllVolumes) {
        setVolumes(allVolumes)
      } else {
        setVolumes(allVolumes.slice(0, 5))
      }
    },[showAllPeople, showAllVolumes])

    React.useEffect(() => {
      setAdditionalFileTypes(searchFileTypes(otherFileTypes, fileTypeSearchValue, fileType));
    },[fileTypeSearchValue, otherFileTypes, fileType])

    React.useEffect(() => {
      let filtered = [];
      filtered = records.filter((record)=>{
        return Object.keys(person).length !== 0 && record.attributes?.personalattributes?.person === person.name;
      });

      filtered = filtered.filter((record)=>{
        return Object.keys(fileType).length !== 0 && record.attributes?.personalattributes?.filetype === fileType.name;
      });

      if(filtered.length > 0) {
        if(filtered[0]?.attributes?.personalattributes?.trackingid) {
          setEnableTrackingIDInput(false);
          handleTrackingIDChange(filtered[0]?.attributes?.personalattributes?.trackingid);
        }
      } else {
        setEnableTrackingIDInput(true);
        handleTrackingIDChange("");
      }
    },[records, person, fileType])

    return (
    <>
      {(modalFor === "add" && (uploadFor === "attachment" || uploadFor === 'record')) && (<div>

        <div className="tagtitle">
          <span>
            Select the records type, input the tracking id # 
            and select the name of the section of records you are uploading. 
            Once you have selected the section name you will be able to 
            select the respective documents from your computer to add to the records log.
          </span>
        </div>

        {divisions.length > 0 && isMinistryCoordinator && (<>
        <div className="tagtitle">
          <span>Select Divisional Tracking: *</span>
        </div>  
        <div className="taglist-cfdpersonal">
          {divisions.map(tag =>
            <ClickableChip
              id={`${tag.name}Tag`}
              key={`${tag.name}-tag`}
              label={tag.display.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handleTagChange(tag.name)}}
              clicked={tagValue === tag.name}
            />
          )}
        </div>
        </>)}

        <div className="tagtitle">
          <span>Select Person (IAO will have the ability to edit this when redacting records): *</span>
        </div>        
        <div className="taglist-cfdpersonal">
          {people.map(p =>
            <ClickableChip
              id={`${p.name}Tag`}
              key={`${p.name}-tag`}
              label={p.name.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handlePersonChange(p)}}
              clicked={person?.name === p.name}
            />
          )}
          {!showAllPeople && (<AddCircleIcon
            id={`showallpeopleTag`}
            key={`showallpeople-tag`}
            color="primary"
            size="small"
            className="pluscircle"
            onClick={()=>{setShowAllPeople(true)}}
          />)}
        </div>

        <div className="tagtitle">
          <span>Select Volume:</span>
        </div>  
        <div className="taglist-cfdpersonal">
          {volumes.map(v =>
            <ClickableChip
              id={`${v.name}Tag`}
              key={`${v.name}-tag`}
              label={v.name.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handleVolumeChange(v)}}
              clicked={volume?.name === v.name}
              // disabled={!isPersonSelected}
            />
          )}
          {!showAllVolumes && (<AddCircleIcon
            id={`showallvolumeTag`}
            key={`showallvolume-tag`}
            color="primary"
            size="small"
            className="pluscircle"
            onClick={()=>{setShowAllVolumes(true)}}
          />)}
        </div>

        <div className="tagtitle">
          <span>Select File Type: *</span>
        </div>  
        <div className="taglist-cfdpersonal">
          {fileTypes.map(f =>
            <ClickableChip
              id={`${f.name}Tag`}
              key={`${f.name}-tag`}
              label={f.name.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handleFileTypeChange(f)}}
              clicked={fileType?.name === f.name}
              // disabled={!isPersonSelected}
            />
          )}
        </div>
        <div className="taglist-cfdpersonal">
          <Grid
            container
            item
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            xs={12}
            sx={{
              marginTop: "1em",
            }}
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
                <label className="hideContent">Search any additional filetypes here</label>
                <InputBase
                  id="foirecordsfilter"
                  placeholder="Search any additional filetypes here"
                  defaultValue={""}
                  onChange={(e)=>{setFileTypeSearchValue(e.target.value.trim())}}
                  sx={{
                    color: "#38598A",
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <IconButton
                        aria-label="Search Icon"
                        className="search-icon"
                      >
                        <span className="hideContent">Search any additional filetypes here</span>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  }
                  fullWidth
                  // disabled={!isPersonSelected}
                />
              </Grid>
            </Paper>
            {showAdditionalFileTypes === true && (<Paper
              component={Grid}
              sx={{
                border: "1px solid #38598A",
                color: "#38598A",
                maxWidth:"100%",
                padding: "8px 15px 0 15px",
                borderTopLeftRadius: 0,
                borderTopRightRadius: 0,
                borderTop: "none",
                maxHeight:"120px",
                overflowY:"auto"
              }}
              alignItems="center"
              justifyContent="flex-start"
              direction="row"
              container
              item
              xs={12}
              elevation={0}
            >
              {additionalFileTypes.map(f =>
                <ClickableChip
                  id={`${f.name}Tag`}
                  key={`${f.name}-tag`}
                  label={f.name.toUpperCase()}
                  sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
                  color="primary"
                  size="small"
                  onClick={()=>{handleFileTypeChange(f)}}
                  clicked={fileType?.name === f.name}
                />
              )}
            </Paper>)}
          </Grid>
        </div>

        <div className="taglist-cfdpersonal">
          <TextField
            id="trackingid"
            label="Tracking ID #"
            inputProps={{ "aria-labelledby": "trackingID-label"}}
            InputLabelProps={{ shrink: true }}
            variant="outlined"
            value={trackingID}
            fullWidth
            onChange={handleTrackingIDUpdate}
            required={true}
            disabled={!isPersonSelected || !enableTrackingIDInput}
            helperText={enableTrackingIDInput?"":"If you've made an error with the file number, you will need to use the edit function in the records log."}
          />
        </div>

        <div className="tagtitle">
          <span>Select Section Name:</span>
        </div>
        <div className="taglist-cfdpersonal">
          {tagList.map(tag =>
            <ClickableChip
              id={`${tag.name}Tag`}
              key={`${tag.name}-tag`}
              label={tag.name.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handlePersonalTagChange(tag);}}
              clicked={personalTag?.name === tag.name}
              disabled={!isPersonSelected || trackingID===""}
            />
          )}
        </div>
        <div className="taglist-cfdpersonal">
          <Grid
            container
            item
            direction="row"
            justify="flex-start"
            alignItems="flex-start"
            xs={12}
            sx={{
              marginTop: "1em",
            }}
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
                <label className="hideContent">Search any additional sections here</label>
                <InputBase
                  id="foirecordsfilter"
                  placeholder="Search any additional sections here"
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
                        <span className="hideContent">Search any additional sections here</span>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  }
                  fullWidth
                  disabled={!isPersonSelected || trackingID===""}
                />
              </Grid>
            </Paper>
            {showAdditionalTags === true && (<Paper
              component={Grid}
              sx={{
                border: "1px solid #38598A",
                color: "#38598A",
                maxWidth:"100%",
                padding: "8px 15px 0 15px",
                borderTopLeftRadius: 0,
                borderTopRightRadius: 0,
                borderTop: "none",
                maxHeight:"120px",
                overflowY:"auto"
              }}
              alignItems="center"
              justifyContent="flex-start"
              direction="row"
              container
              item
              xs={12}
              elevation={0}
            >
              {additionalTagList.map(tag =>
                <ClickableChip
                  id={`${tag.name}Tag`}
                  key={`${tag.name}-tag`}
                  label={tag.name.toUpperCase()}
                  sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
                  color="primary"
                  size="small"
                  onClick={()=>{handlePersonalTagChange(tag)}}
                  clicked={personalTag?.name === tag.name}
                />
              )}
            </Paper>)}
          </Grid>
        </div>
      </div>)}
      {modalFor === "add" && (<div className="tag-message-container-scanning">
        <p>Please drag and drop or add records associated with the section name you have selected above. All records upload will show under the selected section in the redaction application.</p>
      </div>)}
      <section
        className={clsx("file-upload-container-scanning", {
          [customFormat.container]: !!customFormat.container,
        })}
      >
        <div
          className={clsx("row", "file-upload-preview", {
            [customFormat.preview]: !!customFormat.preview,
          })}
          onDragOver={dragOver}
          onDragEnter={dragEnter}
          onDragLeave={dragLeave}
          onDrop={fileDrop}
          onClick={handleUploadAreaClick}>
          <div className="file-upload-column">
            {Object.entries(files).length === 0 ? (
              <div className="file-upload-btn">
                <p className="drag-and-drop-text">{showDragandDrop()}</p>
              </div>
            ) : (
              <FilePreviewContainer files={files} removeFile={removeFile} />
            )}
          </div>
          <div className="file-upload-column file-upload-column-2">
            <input
            id="fileupload"
            aria-label="fileUpload"
            className={multipleFiles ? "file-upload-input-multiple" : "file-upload-input"}
            type="file"
            ref={fileInputField}
            onChange={handleNewFileUpload}
            value=""
            multiple={multipleFiles}
            accept={mimeTypes}
            disabled={modalFor === "add" && (!isPersonSelected || ((isMinistryCoordinator && tagValue == "")))}
            />
          </div>
          <div className="file-upload-column file-upload-column-3">
            {(Object.entries(files).length === 0 && !multipleFiles) || multipleFiles ?
            <button className="btn-add-files" type="button" onClick={handleUploadBtnClick} disabled={modalFor === "add" && (!isPersonSelected || ((isMinistryCoordinator && tagValue == "")))}>
                  Add Files
            </button>  : null}
          </div>
        </div>
      </section>
      <ul className="error-message-ul">
        {errorMessage
          ? errorMessage.map((error) => (
              <li>
                <div className="error-message-container">
                  <p>{error}</p>
                </div>
              </li>
            ))
          : null}
      </ul>
    </>
    );
};

export default FileUploadForMCFPersonal;