export const removeDuplicateFiles = (recordList) => {
    return recordList.filter(record => !record.isduplicate);    
}

export const addDeduplicatedAttachmentsToRecords = (exporting) => {
    for (let record of exporting) {
        if (record.attachments) for (let attachment of record.attachments) {
          if (!attachment.isduplicate) exporting.push(attachment);
        }
    }
    return exporting;
}

export const getPDFFilePath = (item) => {

    let filepath = item.s3uripath
    let filename = item.filename

    if (item.isredactionready && ['.doc','.docx','.xls','.xlsx', '.ics', '.msg'].includes(item.attributes?.extension?.toLowerCase())) {
        filepath = filepath.substr(0, filepath.lastIndexOf(".")) + ".pdf";
        filename += ".pdf";
    }
    return [filepath, filename];
}

export const sortDivisionalFiles = (divisionMap) => {
    return Array.from(divisionMap.values()).map(({ divisionid, divisionname, files, divisionfilesize }) => ({
        divisionid,
        divisionname,
        files: files.sort((a, b) => new Date(a.lastmodified) - new Date(b.lastmodified)),
        divisionfilesize
    }));
}


export const calculateTotalFileSize = (divisions) => {
    return divisions.reduce((total, division) => {
      return total + division.divisionfilesize;
    }, 0);
  }
