const MimeTypeList = Object.freeze({
    stateTransition: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'],
    attachmentLog: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
    'image/bmp','image/gif','image/jpeg','image/png','image/svg+xml','image/tiff','image/webp',
    'application/vnd.ms-excel.sheet.macroEnabled.12','.msg', '.eml'],
    extensionAttachment: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', '.msg', '.eml', 'image/jpeg']
});

const MaxFileSizeInMB = Object.freeze({
    stateTransition: 50,
    attachmentLog: 100,
    totalFileSize: 500,
    extensionAttachment: 50
});

const extensionStatusId = Object.freeze({
  denied: 3,
  pending: 1,
  approved: 2,
});

export { MimeTypeList, MaxFileSizeInMB, extensionStatusId };