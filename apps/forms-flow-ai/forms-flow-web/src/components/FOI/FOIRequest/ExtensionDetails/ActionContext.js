import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { formatDate } from "../../../../helper/FOI/helper";
import { useParams } from "react-router-dom";
import {
  fetchExtensionReasons,
  fetchExtension,
  createExtensionRequest,
  updateExtensionRequest,
} from "../../../../apiManager/services/FOI/foiExtensionServices";
import { extensionStatusId } from "../../../../constants/FOI/enum";
import { toast } from "react-toastify";

export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {

  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  const [modalOpen, setModalOpen] = useState();
  const [loading, setLoading] = useState(true)
  const [extensionReasons, setExtensionReasons] = useState()  

  const [extensionId, setExtensionId] = useState(null)
  const [selectedExtension, setSelectedExtension] = useState(null)

  const currentDueDate = formatDate(requestDetails.dueDate)
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.originalDueDate);
  const extensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );
  const idNumber = requestDetails?.idNumber
  const pendingExtensionExists = extensions.some(
    (ex) => ex.extensionstatusid === extensionStatusId.pending
  );

  useEffect(() => {
    if (requestId) {
      fetchExtensionReasons({
        callback: (data) => {
          setExtensionReasons(data);
        },
        dispatch: dispatch,
      });
    }
  }, [extensions]);

  useEffect(() => {
    if (extensionId && modalOpen) {
      setLoading(true);
      fetchExtension({
        extensionId: extensionId,
        callback: (data) => {
          setSelectedExtension(data);
        },
        dispatch: dispatch,
      });
    }
  }, [modalOpen, extensionId]);

  const saveExtensionRequest = ({ data, callback, errorCallback }) => {
    if (extensionId) {
      updateExtensionRequest({
        data,
        extensionId,
        ministryId,
        callback,
        errorCallback,
        dispatch,
      });
    } else {
      createExtensionRequest({
        data,
        requestId,
        ministryId,
        callback,
        errorCallback,
        dispatch,
      });
    }
  };

  const errorToast = (errorMessage) => {
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

  return (
    <ActionContext.Provider
      value={{
        modalOpen,
        setModalOpen,
        loading,
        setLoading,
        extensionId,
        setExtensionId,
        selectedExtension,
        setSelectedExtension,
        extensionReasons,
        dispatch,
        currentDueDate,
        originalDueDate,
        startDate,
        extensions,
        idNumber,
        saveExtensionRequest,
        pendingExtensionExists,
        errorToast,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
