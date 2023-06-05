//Remove duplicate records
export const removeDuplicateFiles = (recordList) => (
    recordList.filter(({isduplicate}) => !isduplicate)
  );
  
  // Helper function to sort files by lastmodified date
export const sortByLastModified = (files) => (
    files.sort((a, b) => new Date(a.lastmodified) - new Date(b.lastmodified))
  );
  
export const getPDFFilePath = (item) => {
 
    let pdffilepath = item.s3uripath
    let pdffilename = item.filename
 
    if (item.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(item.attributes?.extension?.toLowerCase())) {
        pdffilepath = pdffilepath.substr(0, pdffilepath.lastIndexOf(".")) + ".pdf";
        pdffilename += ".pdf";
    }
    return [pdffilepath, pdffilename];
 }
 
 // Get records with only necessary fields
 export const getUpdatedRecords = (_records, isattachment=false) =>{
    return _records.map(_record => {
        const [filepath, filename] = getPDFFilePath(_record)
        const deduplicatedAttachments = _record?.attachments?.length > 0 ? removeDuplicateFiles(_record.attachments): []
        const _recordObj =
            {
                recordid: _record.recordid,
                filename: filename,
                s3uripath: filepath,
                filesize: _record.attributes.convertedfilesize || _record.attributes.filesize,
                lastmodified: _record.attributes.lastmodified,
                isduplicate: _record.isduplicate,
                divisions: _record.attributes.divisions,
                divisionids: _record.attributes.divisions.map(d => d.divisionid),
                attachments: !isattachment ? sortByLastModified(getUpdatedRecords(deduplicatedAttachments, true)) : undefined
            }
        return _recordObj
        
    })
 }
 
 //Get files for specified divisionid with necessary fields
 export const getFiles = (_records, _divisionid) => {
     return _records.filter(_record => _record.divisionids.includes(_divisionid)).map(r => {
         return ({
             recordid: r.recordid,
             filename: r.filename,
             s3uripath: r.s3uripath,
             filesize: r.filesize,
             lastmodified: r.lastmodified
         })
     })
 }
 
 // calculate divisional total file size
 export const calculateDivisionFileSize = (_files) => {
     return _files.reduce((total, _file) => {
         return total + +_file.filesize;
       }, 0);
 }
 
 // calculate final file size
export const calculateTotalFileSize = (divisions) => {
     return divisions.reduce((total, division) => {
       return total + division.divisionfilesize;
     }, 0);
   }

export const addDeduplicatedAttachmentsToRecords = (exporting) => {
    for (let record of exporting) {
        if (record.attachments) for (let attachment of record.attachments) {
          if (!attachment.isduplicate) exporting.push(attachment);
        }
    }
    return exporting;
}


export const sortDivisionalFiles = (divisionMap) => {
    return Array.from(divisionMap.values()).map(({ divisionid, divisionname, files, divisionfilesize }) => ({
        divisionid,
        divisionname,
        files: files.sort((a, b) => new Date(a.lastmodified) - new Date(b.lastmodified)),
        divisionfilesize
    }));
}


export const calculateTotalUploadedFileSizeInKB = (records) => {
    return records.reduce((total, record) => {
        return total + (record.attributes.convertedfilesize ? record.attributes.convertedfilesize : record.attributes.filesize);
    }, 0);
}

export const getReadableFileSize = (mb) => {
    if (mb < 1) {
        return (mb * 1024).toFixed(4) + ' KB'
    } else if (mb > 1000) {
        return (mb/ 1024).toFixed(4) + ' GB'
    } else {
        return mb.toFixed(4) + ' MB'
    }
  }
