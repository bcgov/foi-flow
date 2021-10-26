import React, { useRef, useState } from "react";
import "./FileUpload.scss"

const DEFAULT_MAX_FILE_SIZE_IN_BYTES = 13397960;
//1073741824;
//13397965
const KILO_BYTES_PER_BYTE = 1000;

const convertBytesToKB = (bytes) => Math.round(bytes / KILO_BYTES_PER_BYTE);

const FileUpload = ({
    multipleFiles,
    updateFilesCb,
    maxFileSizeInBytes = DEFAULT_MAX_FILE_SIZE_IN_BYTES
}) => {
    const fileInputField = useRef(null);
    const [files, setFiles] = useState({});
    const [errorMessage, setErrorMessage] = useState("");
  
    const handleUploadBtnClick = () => {
        fileInputField.current.click();
    };
    const mimeTypes = ['application/pdf', 
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];

    const addNewFiles = (newFiles) => {
      console.log(`add`);
      console.log(newFiles);
      
        for (let file of newFiles) {
          console.log(file);
          if (mimeTypes.includes(file.type)) {
            if (file.size <= maxFileSizeInBytes) {                
                files[file.name] = file;
            }
            else {
              setErrorMessage(`invalid size, file name: ${file.name}`);
            }
          }
          else {
            setErrorMessage(`invalid filetype, file name: ${file.name}`);
          }
        }
        return { ...files };
    };

    const convertNestedObjectToArray = (nestedObj) =>
        Object.keys(nestedObj).map((key) => nestedObj[key]);

    const callUpdateFilesCb = (files) => {
        const filesAsArray = convertNestedObjectToArray(files);
        updateFilesCb(filesAsArray);
    };
    const handleNewFileUpload = (e) => {
      console.log(e);
        const { files: newFiles } = e.target;
        console.log(newFiles);
        if (newFiles.length) {
            let updatedFiles = addNewFiles(newFiles);
            setFiles(updatedFiles);
            callUpdateFilesCb(updatedFiles);
        }
    };
    const removeFile = (fileName) => {
        delete files[fileName];
        setFiles({ ...files });
        callUpdateFilesCb({ ...files });
        setErrorMessage("");
    };
    console.log(files);
  return (
    <>
      <section className="file-upload-container">       
        <div className="row file-upload-preview" >
          {Object.entries(files).length === 0 ?
          <>
          <div className="col-lg-12 file-upload-btn">
            <p className="drag-and-drop-text">Drag and drop request letter(s) or</p>
            <button className="btn-add-files" type="button" onClick={handleUploadBtnClick}>
              {/* <i className="fas fa-file-upload" /> */}
              {/* <span> Upload {otherProps.multiple ? "files" : "a file"}</span> */}
              Add Files
            </button>           
          </div>
           {errorMessage ? 
            <p className="error-message">{errorMessage}</p>
            : null}
          </>
          :
          // {files != undefined && Object.entries(files).length > 0 ?
          <FilePreviewContainer files={files} removeFile={removeFile} />
          }
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
     
    </>
  );
};


function FilePreviewContainer({files, removeFile}) {
  return (
    <article className="file-preview-container">
      {/* <span>To Upload</span> */}
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

