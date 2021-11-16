import React, { useRef, useState } from "react";
import { MimeTypeList } from "../../../constants/FOI/enum";
import "./FileUpload.scss"

const FileUpload = ({
    multipleFiles,
    updateFilesCb
}) => {
    const fileInputField = useRef(null);
    const [files, setFiles] = useState({});
    const [errorMessage, setErrorMessage] = useState("");
  
    const handleUploadBtnClick = () => {
        fileInputField.current.click();
    };
    const mimeTypes = MimeTypeList.stateTransition;

    const addNewFiles = (newFiles) => {
        for (let file of newFiles) {
          if (mimeTypes.includes(file.type)) {
            const sizeInMB = (file.size / (1024*1024)).toFixed(2);
            if (sizeInMB <= 50) {             
                files[file.name] = file;
                setErrorMessage("");
            }
            else {
              setErrorMessage(`The specified file ${file.name} could not be uploaded. Only files 50mb or under can be uploaded. `);
            }
          }
          else {
            setErrorMessage(`The specified file ${file.name} could not be uploaded. Only files with the following extensions are allowed: pdf, xlsx, docx`);
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
        const { files: newFiles } = e.target;
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
    
  return (
    <>
      <section className="file-upload-container">       
        <div className="row file-upload-preview" >
          {Object.entries(files).length === 0 ?
         
          <div className="col-lg-12 file-upload-btn">
            <p className="drag-and-drop-text">Drag and drop request letter(s) or</p>
            <button className="btn-add-files" type="button" onClick={handleUploadBtnClick}>              
              Add Files
            </button>           
          </div>
          :         
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
      {errorMessage ?
           <div className="error-message-container">
             <p>{errorMessage}</p>
           </div>
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

