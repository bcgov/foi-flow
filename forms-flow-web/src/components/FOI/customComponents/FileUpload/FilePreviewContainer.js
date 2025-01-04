import React from "react";

function FilePreviewContainer({files, removeFile, clickHandler}) {
    return (
      <article className="file-preview-container">     
        <section>
          <ol className={`${Object.keys(files).length === 1 ? "ol-display-none": ""}`}>
          {Object.keys(files).map((fileName, _index) => {
            let file = files[fileName];
            return (
              <li key={_index} className={`${Object.keys(files).length === 1 ? "ol-display-none": ""}`}>
                <FilePreviewList key={fileName} file={file} fileName={fileName} removeFile={removeFile} clickHandler={clickHandler} />
              </li>
            );
          })}
          </ol>
        </section>
      </article>
    );
  }
  
  function FilePreviewList({file, fileName, removeFile, clickHandler}) {
    return (
    <section>
      <div>
        <div>
          <aside>  
            <span style={{cursor: clickHandler ? "pointer" : "auto"}} onClick={() => clickHandler(fileName)} className="file-name">{file.filename ? file.filename : file.name}</span>                                       
            <i style={{cursor: "pointer"}} className="fas fa-times-circle foi-file-close" onClick={(event) => {event.stopPropagation(); removeFile(fileName);}} />
          </aside>
        </div>
      </div>
    </section>
    );
  }

  export default FilePreviewContainer;