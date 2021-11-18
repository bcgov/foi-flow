const MimeTypeList = Object.freeze({
    stateTransition: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'],
    attachmentLog: ['application/pdf', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword',
    'image/bmp','image/gif','image/jpeg','image/png','image/svg+xml','image/tiff','image/webp',
    'application/vnd.ms-excel.sheet.macroEnabled.12','.msg'],    
});

const MaxFileSize = Object.freeze({
    stateTransition: 50,
    attachmentLog: 1,
});

export { MimeTypeList, MaxFileSize };