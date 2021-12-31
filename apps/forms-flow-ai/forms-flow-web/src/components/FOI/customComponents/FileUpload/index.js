import React, { useRef, useState } from "react";
import FilePreviewContainer from "./FilePreviewContainer";
import { countOccurrences, 
  generateNewFileName, 
  getErrorMessage, 
  allowedFileType, 
  allowedFileSize, 
  convertNestedObjectToArray, 
  convertBytesToMB } from "./util";
import "./FileUpload.scss"

const FileUpload = ({
    multipleFiles,
    mimeTypes,
    maxFileSize,
    totalFileSize,
    updateFilesCb,
    attchmentFileNameList,
    attachment
}) => {
    const fileInputField = useRef(null);
    const fileInputFieldMultiple = useRef(null);
    const [files, setFiles] = useState({});
    const [totalFileSizeCalculated, setTotalFileSize] = useState(0);
    const [errorMessage, setErrorMessage] = useState([]); 
    const handleUploadBtnClick = () => {
      if (fileInputField.current)
        fileInputField.current.click();
      else
        fileInputFieldMultiple.current.click();
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
        for (let file of newFiles) {
          file.filename = file.name;
          const sizeInMB = convertBytesToMB(file.size);
          _totalFileSizeInMB += parseFloat(sizeInMB);
          
          if (allowedFileType(file, mimeTypes, multipleFiles)) {
            if (allowedFileSize(_totalFileSizeInMB, multipleFiles, totalFileSize)) {
              if (sizeInMB <= maxFileSize) {
                const duplicateFileName = handleDuplicateFiles(file);
            _duplicateFiles.push(duplicateFileName);
              }
              else {
                _totalFileSizeInMB -= parseFloat(sizeInMB);
                _overSizedFiles.push(file.name);
              }
            }
            else {
              removeFileSize = convertBytesToMB(file.size);
            }
          }
          else {
            _typeErrorFiles.push(file.name);
          }
        }
        setTotalFileSize(_totalFileSizeInMB);
        setErrorMessage(getErrorMessage(_duplicateFiles, _typeErrorFiles, _overSizedFiles, maxFileSize, multipleFiles));
        return [{...files}, _totalFileSizeInMB, removeFileSize];
    };

    const callUpdateFilesCb = (_files) => {
        const filesAsArray = convertNestedObjectToArray(_files);
        updateFilesCb(filesAsArray, errorMessage);
    };

    const validateFiles = (newFiles, totalFiles) => {

      if (multipleFiles && (newFiles.length > 10  || totalFiles > 10)) {
        setErrorMessage(["A maximum of 10 files can be uploaded at one time. Only 10 files have been added this upload window, please upload additional files separately"]);
      }
      else if (newFiles.length) {
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
      if (multipleFiles)
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
        return "Drag and drop request letter(s) or"
    }
  return (
    <>
      <section className="file-upload-container">       
      <div className="row file-upload-preview" 
          onDragOver={dragOver}
          onDragEnter={dragEnter}
          onDragLeave={dragLeave}
          onDrop={fileDrop} >
          <div className="file-upload-column">
            {Object.entries(files).length === 0 ?
          
            <div className="file-upload-btn">
              <p className="drag-and-drop-text">{showDragandDrop()}</p>               
                       
            </div>
            :         
            <FilePreviewContainer files={files} removeFile={removeFile} />
            }
          </div>
          <div className="file-upload-column file-upload-column-2">
            <input
            className="file-upload-input-multiple"
            type="file"
            ref={fileInputFieldMultiple}
            onChange={handleNewFileUpload}
            title=""
            value=""
            multiple={true}
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
        {Object.entries(files).length === 0 ?
        <input
          className="file-upload-input"
          type="file"
          ref={fileInputField}
          onChange={handleNewFileUpload}
          title=""
          value=""
          multiple={multipleFiles}
          accept={mimeTypes}
        />
        : null}
        
      </section>
      <ul className="error-message-ul">
      {errorMessage ? errorMessage.map(error => 
           <li>
            <div className="error-message-container">
              <p>{error}</p>
            </div>
           </li>
           )
      : null}
     </ul>
    </>
  );
};

export default FileUpload;