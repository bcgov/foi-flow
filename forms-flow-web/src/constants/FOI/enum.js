const MimeTypeList = Object.freeze({
  stateTransition: ['application/pdf', 
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
  '.xls', '.xlsx', '.doc', '.docx'],
  stateTransitionFees: ['application/pdf'],
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
  extensionAttachment: 50,
  feeEstimateAttachment: 25,
  totalFeeEstimateFileSize:50
});

const MaxNumberOfFiles = Object.freeze({
  feeEstimateFiles:2,
  attachments:10
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
"Social Education",
"Central and Economy Team",
"Justice and Resource Team",
"Community and Health Team",
"Children and Family Team",
"Children and Education Team",
"Coordinated Response Unit",
]

export {
MimeTypeList,
MaxFileSizeInMB,
MaxNumberOfFiles,
extensionStatusId,
extensionStatusLabel,
KCProcessingTeams,
};