import React from "react";

function FilePreviewContainer({files, removeFile}) {
    return (
      <article className="file-preview-container">     
        <section>
          <ol className={`${Object.keys(files).length === 1 ? "ol-display-none": ""}`}>
          {Object.keys(files).map((fileName, _index) => {
            let file = files[fileName];
            return (
              <li className={`${Object.keys(files).length === 1 ? "ol-display-none": ""}`}>
                <FilePreviewList key={fileName} file={file} fileName={fileName} removeFile={removeFile} />
              </li>
            );
          })}
          </ol>
        </section>
      </article>
    );
  }
  
  function FilePreviewList({file, fileName, removeFile}) {
    return (
    <section>
      <div>
        <div>
          <aside>  
            <span className="file-name">{file.filename ? file.filename : file.name}</span>                                       
            <i className="fas fa-times-circle foi-file-close" onClick={(event) => {event.stopPropagation(); removeFile(fileName);}} />
          </aside>
        </div>
      </div>
    </section>
    );
  }

  export default FilePreviewContainer;