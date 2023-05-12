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

const FileUpload = ({
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
    tagList = [],
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
                  if (_totalFileSizeInMB + totalUploadedRecordSize < totalRecordUploadLimit) {
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

  return (
    <>
      {(modalFor === "add" && (uploadFor === "attachment" || uploadFor === 'record')) && (<div>
        <div className="tagtitle">
          <span>Select one {uploadFor === 'record' ? "division" : "tag"} that corresponds to the document(s) you are uploading</span>
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
              onClick={()=>{handleTagChange(tag.name)}}
              clicked={tagValue == tag.name}
            />
          )}
        </div>
      </div>)}
      <section
        className={clsx("file-upload-container", {
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
      {modalFor === "add" && (<div className="tag-message-container">
        <p>When uploading more than one {uploadFor}, all {uploadFor}s will have the same selected tag.</p>
      </div>)}
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

export default FileUpload;