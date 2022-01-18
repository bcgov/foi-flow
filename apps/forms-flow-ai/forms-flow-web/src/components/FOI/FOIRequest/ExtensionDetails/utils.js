import {
  getOSSHeaderDetails,
  saveFilesinS3,
} from "../../../../apiManager/services/FOI/foiOSSServices";

export const getFileInfoList = (files, idNumber) => {
  return files.map((file) => {
    return {
      ministrycode: idNumber.split("-")[0],
      requestnumber: idNumber,
      filestatustransition: "extension",
      filename: file.filename || file.name,
    };
  });
};

export const uploadFiles = async (filesToUpload, idNumber, dispatch) => {
  const fileInfoList = getFileInfoList(filesToUpload, idNumber);

  const headers = await new Promise((resolve, reject) => {
    getOSSHeaderDetails(fileInfoList, dispatch, (err, res) => {
      if (err) {
        reject(
          "An internal server error occured while attempting to upload files"
        );
      }
      resolve(res);
    });
  });

  return Promise.all(
    headers.map((header) => {
      const _file = filesToUpload.find(
        (file) => file.filename === header.filename
      );
      return new Promise((resolve, reject) => {
        saveFilesinS3(header, _file, dispatch, (err, res) => {
          if (err) {
            reject("An error occurred while attempting to upload files");
          }
          resolve({
            documentpath: header.filepath,
            filename: header.filename,
            category: header.filestatustransition,
          });
        });
      });
    })
  );
};

export const checkPublicBodyError = (numberDays, publicBodySelected) => {
  if (!numberDays) {
    return true;
  }
  if (publicBodySelected) {
    return numberDays > 30;
  }

  return false;
};
