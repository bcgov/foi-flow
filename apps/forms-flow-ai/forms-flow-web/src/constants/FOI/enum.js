const MimeTypeList = Object.freeze({
    stateTransition: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
    '.xls', '.xlsx', '.doc', '.docx'],
    attachmentLog: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
    'image/bmp','image/gif','image/jpeg','image/png','image/svg+xml','image/tiff','image/webp',
    'application/vnd.ms-excel.sheet.macroEnabled.12','.msg', '.eml', '.xls', '.xlsx', '.doc', '.docx'],
    extensionAttachment: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', '.msg', '.eml', 'image/jpeg',
    '.xls', '.xlsx', '.doc', '.docx']
});

const MaxFileSizeInMB = Object.freeze({
    stateTransition: 50,
    attachmentLog: 100,
    totalFileSize: 500,
    extensionAttachment: 50
});

const extensionStatusId = Object.freeze({
  pending: 1,
  approved: 2,
  denied: 3,
});

const extensionStatusLabel = Object.freeze({
  1: "Pending",
  2: "Approved",
  3: "Denied",
});

const KCProcessingTeams = [
  "Scanning Team", 
  "Central Team", 
  "Justice Health Team", 
  "MCFD Personals Team", 
  "Resource Team", 
  "Social Education"]

export {
  MimeTypeList,
  MaxFileSizeInMB,
  extensionStatusId,
  extensionStatusLabel,
  KCProcessingTeams,
};