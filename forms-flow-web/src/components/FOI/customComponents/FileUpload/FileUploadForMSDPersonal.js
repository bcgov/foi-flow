import React, { useRef, useState, useEffect } from "react";
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
import _ from 'lodash';

const FileUploadForMSDPersonal = ({
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
    parentTagValue,
    tagList = [],
    subTagList = [],
    isMinistryCoordinator,
    uploadFor="attachment",
    totalUploadedRecordSize,
    totalRecordUploadLimit
}) => {
    const fileInputField = useRef(null);
    const [files, setFiles] = useState({ ...existingDocuments });    
    const [totalFileSizeCalculated, setTotalFileSize] = useState(0);
    const [errorMessage, setErrorMessage] = useState([]); 
    const [includeAttachments, setIncludeAttachments] = useState(true);
    const [searchValue, setSearchValue] = useState("");
    const [additionalTagList, setAdditionalTagList] = useState([]);
    const [showChildTags, setShowChildTags] = useState(false);
    const [showAdditionalTags, setShowAdditionalTags] = useState(false);

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
      const newFiles = e.dataTransfer.files;
      const totalNoOfFiles = Object.entries(files).length + newFiles.length; 
      validateFiles(newFiles, totalNoOfFiles);
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
          if(_keyword && section.display.toLowerCase().includes(_keyword.toLowerCase())) {
            newSectionArray.push(section);
          } else if(section.name === _selectedSectionValue) {
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
      setAdditionalTagList(searchSections(subTagList, searchValue, tagValue));
    },[searchValue, subTagList, tagValue])

    const handleParentTagChange = (_tagValue) => {
      setAdditionalTagList([]);
      if (_tagValue === parentTagValue) {
        setShowChildTags(true);
        handleTagChange("");
      } else {
        setShowChildTags(false);
        handleTagChange(_tagValue);
      }
    }

    return (
    <>
      {(modalFor === "add" && (uploadFor === "attachment" || uploadFor === 'record')) && (<div>
        <div className="tagtitle">
          <span>Select the name of the section of records you are uploading. Once you have selected the section name you will be able to select the respective documents from your computer.</span>
        </div>
        <div className="taglist">
          {tagList.map(tag =>
            <ClickableChip
              id={`${tag.name}Tag`}
              key={`${tag.name}-tag`}
              label={tag.display.toUpperCase()}
              sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
              color="primary"
              size="small"
              onClick={()=>{handleParentTagChange(tag.name)}}
              clicked={tag.name == tagValue || (showChildTags && tag.name === parentTagValue)}
            />
          )}
        </div>
        {showChildTags === true && (<div className="taglist">
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
                  value={searchValue}
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
                  label={tag.display.toUpperCase()}
                  sx={{width: "fit-content", marginRight: "8px", marginBottom: "8px"}}
                  color="primary"
                  size="small"
                  onClick={()=>{handleTagChange(tag.name)}}
                  clicked={tagValue == tag.name}
                />
              )}
            </Paper>)}
          </Grid>
        </div>)}
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
            />
          </div>
          <div className="file-upload-column file-upload-column-3">
            {(Object.entries(files).length === 0 && !multipleFiles) || multipleFiles ?
            <button className="btn-add-files" type="button" onClick={handleUploadBtnClick}>              
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

export default FileUploadForMSDPersonal;