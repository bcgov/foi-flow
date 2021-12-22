
  let countFileNameOccurence = 1;
  export const countOccurrences = (fileName, attchmentFileNameList) => {
    return attchmentFileNameList.reduce((count, attachmentName) => (attachmentName.toLowerCase() === fileName.toLowerCase() ? count + 1 : count), 0);
  }
  export const generateNewFileName = (newFileName, uploadFileName, attachedFileName, attchmentFileNameList) => {
    let count = countOccurrences(newFileName, attchmentFileNameList);      
    let _fileNameArray = uploadFileName.split('.');      
    newFileName = count > 0 ? `${_fileNameArray[0]}(${++countFileNameOccurence}).${_fileNameArray[1]}` : newFileName;      
    if (count > 0) {
      if (attachedFileName && attachedFileName === newFileName)
        return attachedFileName;
      else {
        newFileName = generateNewFileName(newFileName, uploadFileName, attachedFileName, attchmentFileNameList);
        return newFileName;
      }
    }
    return newFileName;
  }

  export const getErrorMessage = (_duplicateFiles, _typeErrorFiles, _overSizedFiles, maxFileSize, multipleFiles) => {
    let _errorMessage = [];
    if (_duplicateFiles.length > 0 && _duplicateFiles[0]) {
      _errorMessage.push(<>A attachment with this file name(s) <b>{_duplicateFiles.join(", ")}</b> already exists. A duplicate records cannot be added. Please rename attachment or replace existing attachment with updated version.</>);
    }
    if (_overSizedFiles.length > 0) {
      _errorMessage.push(<>The specified file(s) <b>{_overSizedFiles.join(", ")}</b> could not be uploaded. Only files <b>{maxFileSize}MB</b> or under can be uploaded.</>);
    }
    if (_typeErrorFiles.length > 0) {
      _errorMessage.push(<>The specified file(s) <b>{_typeErrorFiles.join(", ")}</b> could not be uploaded. Only files with the following extensions are allowed: <b>{multipleFiles ? 'Excel (xls, xlsx, macro), pdf, image, word, email' : 'pdf, xlsx, docx'}</b></>);
    }
    return _errorMessage;
  }

  export const isEmailFileType = (_file) => {
    return _file.name.endsWith(".msg") || _file.name.endsWith(".eml");
  }

  export const allowedFileType = (_file, mimeTypes, multipleFiles) => {
    return (mimeTypes.includes(_file.type) || (multipleFiles && isEmailFileType(_file)));
  }
  
  export const allowedFileSize = (_totalFileSizeInMB, multipleFiles, totalFileSize) => {
    return (!multipleFiles || (multipleFiles && _totalFileSizeInMB <= totalFileSize));
  }

  export const convertNestedObjectToArray = (nestedObj) =>
    Object.keys(nestedObj).map((key) => nestedObj[key]);
 
  export const convertBytesToMB = (_bytes) => {
    return (_bytes / (1024*1024)).toFixed(4);
  }