
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

export const getErrorMessage = (_duplicateFiles, _typeErrorFiles, _overSizedFiles, maxFileSize, multipleFiles, mimeTypes, recordUploadLimitReached, totalRecordUploadLimit) => {
  let _errorMessage = [];
  let singleFileUploadAllowedFileExtensions = "pdf, xlsx, docx";
  if(recordUploadLimitReached){
    _errorMessage.push(<>A maximum <b>{totalRecordUploadLimit > 1000 ? (totalRecordUploadLimit/ 1024).toFixed(2) +' GB': totalRecordUploadLimit +' MB'}</b> of records can be uploaded per request. Please load the records for this request onto the LAN and notify IAO by updating the request state to Deduplication and posting a comment in the request.</>);
    return _errorMessage;
  }
  if (mimeTypes.some(mimeType => mimeType === '.msg' || mimeType === '.eml')) {
    singleFileUploadAllowedFileExtensions = "pdf, xlsx, docx, msg, eml";
  }

  if (_duplicateFiles.length > 0 && _duplicateFiles[0]) {
    _errorMessage.push(<>A attachment with this file name(s) <b>{_duplicateFiles.join(", ")}</b> already exists. A duplicate records cannot be added. Please rename attachment or replace existing attachment with updated version.</>);
  }
  if (_overSizedFiles.length > 0) {
    _errorMessage.push(<>The specified file(s) <b>{_overSizedFiles.join(", ")}</b> could not be uploaded. Only files <b>{maxFileSize}MB</b> or under can be uploaded.</>);
  }
  const hasOnlyPdfMimeTypes = (mimeTypes) => {
    let result = true;
    mimeTypes.forEach((mimeType) => {
      if (mimeType !== 'application/pdf' && mimeType !== '.pdf') result = false;
    })
    return result;
  }

  if (_typeErrorFiles.length > 0) {
    if (hasOnlyPdfMimeTypes(mimeTypes)) {
      _errorMessage.push(<>The specified file(s) <b>{_typeErrorFiles.join(", ")}</b> could not be uploaded. Only PDF filetypes are allowed.</>);
    } else {
      _errorMessage.push(<>The specified file(s) <b>{_typeErrorFiles.join(", ")}</b> could not be uploaded. Only files with the following extensions are allowed: <b>{multipleFiles ? 'Excel (xls, xlsx, macro), pdf, image, word, email' : singleFileUploadAllowedFileExtensions}</b></>);
    }
  }
  return _errorMessage;
}

export const isEmailFileType = (_file) => {
  return _file.name.endsWith(".msg") || _file.name.endsWith(".eml");
}

export const allowedFileType = (_file, mimeTypes) => {
  return ((mimeTypes.includes(_file.type?.toLowerCase()) || mimeTypes.includes('.' + _file.filename.split('.').pop()?.toLowerCase())) ||
    mimeTypes.includes('.' + _file.name.split('.').pop()?.toLowerCase()));
}

export const allowedFileSize = (_totalFileSizeInMB, multipleFiles, totalFileSize) => {
  return (!multipleFiles || (multipleFiles && _totalFileSizeInMB <= totalFileSize));
}

export const convertNestedObjectToArray = (nestedObj) =>
  Object.keys(nestedObj).map((key) => nestedObj[key]);

export const convertBytesToMB = (_bytes) => {
  return (_bytes / (1024 * 1024)).toFixed(4);
}