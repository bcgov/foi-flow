import React, { useRef, useState } from "react";
import "./FileUpload.scss"

const FileUpload = ({
    multipleFiles,
    mimeTypes,
    updateFilesCb
}) => {
    const fileInputField = useRef(null);
    const fileInputFieldMultiple = useRef(null);
    const [files, setFiles] = useState({});
    const [errorMessage, setErrorMessage] = useState("");
  
    const handleUploadBtnClick = () => {
      if (fileInputField.current)
        fileInputField.current.click();
      else
        fileInputFieldMultiple.current.click();
    };    

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

