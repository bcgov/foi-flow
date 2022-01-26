import {
  getOSSHeaderDetails,
  saveFilesinS3,
} from "../../../../apiManager/services/FOI/foiOSSServices";
import { toast } from "react-toastify";

export const getFileInfoList = (files, idNumber, statusLabel) => {
  return files.map((file) => {
    return {
      ministrycode: idNumber.split("-")[0],
      requestnumber: idNumber,
      filestatustransition: !statusLabel
        ? "extension"
        : `extension - ${statusLabel?.toLowerCase()}`,
      filename: file.filename || file.name,
    };
  });
};

export const uploadFiles = async (
  filesToUpload,
  idNumber,
  dispatch,
  statusLabel
) => {
  const fileInfoList = getFileInfoList(filesToUpload, idNumber, statusLabel);

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

export const filterExtensionReason = (
  extensionReasonsToFilter,
  extensions,
  selectedExtension
) => {
  if (!extensionReasonsToFilter || extensionReasonsToFilter.length < 1) {
    return extensionReasonsToFilter;
  }

  const publicBodyExtensions = new Set(
    extensions
      .filter((ex) => ex.extensiontype === "Public Body")
      .map((ex) => ex.extensionreasonid)
  );

  if (selectedExtension?.extensiontype === "Public Body") {
    return extensionReasonsToFilter.filter(
      (ex) =>
        !publicBodyExtensions.has(ex.extensionreasonid) ||
        selectedExtension.extensionreasonid === ex.extensionreasonid
    );
  }

  if (publicBodyExtensions.size > 0) {
    return extensionReasonsToFilter.filter((ex) => {
      return ex.extensiontype !== "Public Body";
    });
  }

  return extensionReasonsToFilter;
};

export const errorToast = (errorMessage) => {
  return toast.error(errorMessage, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: true,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    progress: undefined,
  });
};
