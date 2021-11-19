import React, { useRef, useState } from "react";
import "./FileUpload.scss"

const FileUpload = ({
    multipleFiles,
    mimeTypes,
    maxFileSize,
    totalFileSize,
    updateFilesCb
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

    const addNewFiles = (newFiles) => {
      let _errorMessage = [];
      let _totalFileSizeInMB = 0;
        for (let file of newFiles) {
          if (mimeTypes.includes(file.type)) {
            const sizeInMB = (file.size / (1024*1024)).toFixed(2);
            _totalFileSizeInMB += parseFloat(sizeInMB);
            if (!multipleFiles || (multipleFiles && _totalFileSizeInMB <= totalFileSize)) {
              if (sizeInMB <= maxFileSize) {             
                  files[file.name] = file;
              }
              else {
                _errorMessage.push(`The specified file ${file.name} could not be uploaded. Only files ${maxFileSize}MB or under can be uploaded. `)              
              }
            }
          }
          else {
            _errorMessage.push(`The specified file ${file.name} could not be uploaded. Only files with the following extensions are allowed: ${multipleFiles ? 'Excel (xls, xlsx, macro), pdf, image, word, email' : 'pdf, xlsx, docx'}`);           
          }
        }
        _totalFileSizeInMB += totalFileSizeCalculated;
        setTotalFileSize(_totalFileSizeInMB);
        setErrorMessage(_errorMessage);
        return { ...files };
    };

    const convertNestedObjectToArray = (nestedObj) =>
        Object.keys(nestedObj).map((key) => nestedObj[key]);

    const callUpdateFilesCb = (files) => {
        const filesAsArray = convertNestedObjectToArray(files);
        updateFilesCb(filesAsArray, errorMessage);
    };
    const handleNewFileUpload = (e) => {
        const { files: newFiles } = e.target;
        const totalFiles = Object.entries(files).length + newFiles.length;
        if (multipleFiles && (newFiles.length > 10  || totalFiles > 10)) {
          setErrorMessage(["A maximum of 10 files can be uploaded at one time. Only 10 files have been added this upload window, please upload additional files separately"]);
        }
        else if (newFiles.length) {
          let updatedFiles = addNewFiles(newFiles);
          if (multipleFiles && totalFileSizeCalculated > totalFileSize) {
            setErrorMessage([`The total size of all files uploaded can not exceed  ${totalFileSize}MB. Please upload additional files separately.`]);            
          }
          setFiles(updatedFiles);
          callUpdateFilesCb(updatedFiles);
      }
    };
    const removeFile = (fileName) => {
        delete files[fileName];
        setFiles({ ...files });
        callUpdateFilesCb({ ...files });
        setErrorMessage([]);
    };
  return (
    <>
      <section className="file-upload-container">       
        <div className="row file-upload-preview" >
          <div className="file-upload-column">
            {Object.entries(files).length === 0 ?
          
            <div className="file-upload-btn">
              <p className="drag-and-drop-text">{Object.entries(files).length === 0 ? `Drag and drop request letter(s) or`: null}</p>               
                       
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
      {errorMessage ? errorMessage.map(error => 
           <div className="error-message-container">
             <p>{error}</p>
           </div>
           )
      : null}
     
    </>
  );
};


function FilePreviewContainer({files, removeFile}) {
  return (
    <article className="file-preview-container">     
      <section>
        {Object.keys(files).map((fileName, index) => {
          let file = files[fileName];
          return (
            <section key={fileName}>
              <div>
                <div>
                  <aside>  
                    <span className="file-name">{file.name}</span>                                       
                    <i className="fas fa-times-circle foi-file-close" onClick={() => removeFile(fileName)} />
                  </aside>
                </div>
              </div>
            </section>
          );
        })}
      </section>
    </article>
  );
}

export default FileUpload;

