import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { formatDate, errorToast } from "../../../../helper/FOI/helper";
import { useParams } from "react-router-dom";
import {
  fetchExtensionReasons,
  fetchExtension,
  createExtensionRequest,
  updateExtensionRequest,
} from "../../../../apiManager/services/FOI/foiExtensionServices";
import { extensionStatusId } from "../../../../constants/FOI/enum";

export const ActionContext = createContext();
ActionContext.displayName = "ExtensionContext"
export const ActionProvider = ({ children, requestDetails, requestState }) => {

  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [extensionLoading, setExtensionLoading] = useState(true)
  const [extensionReasons, setExtensionReasons] = useState(null);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  const [extensionId, setExtensionId] = useState(null);
  const [selectedExtension, setSelectedExtension] = useState(null);

  const currentDueDate = formatDate(requestDetails.dueDate);
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.legislativeDueDate);
  const extensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );
  const idNumber = requestDetails?.idNumber;
  const pendingExtensionExists = extensions.some(
    (ex) => ex.extensionstatusid === extensionStatusId.pending
  );

  useEffect(() => {
    if (requestId && !extensionReasons) {
      fetchExtensionReasons({
        callback: (data) => {
          setExtensionReasons(data);
        },
        dispatch: dispatch,
      });
    }
  }, [extensions]);

  useEffect(() => {
    if (extensionId && saveModalOpen) {
      setExtensionLoading(true);
      fetchExtension({
        extensionId: extensionId,
        callback: (data) => {
          setSelectedExtension(data);
        },
        errorCallback: (errorMessage) => {
          setSaveModalOpen(false)
          errorToast(errorMessage)
        },
        dispatch: dispatch,
      });
    } else {
        setSelectedExtension(null);
    }
  }, [saveModalOpen, extensionId]);

  const saveExtensionRequest = ({ data, callback, errorCallback }) => {
    if (extensionId) {
      updateExtensionRequest({
        data,
        extensionId,
        ministryId,
        requestId,
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

  return (
    <ActionContext.Provider
      value={{
        saveModalOpen,
        setSaveModalOpen,
        extensionLoading,
        setExtensionLoading,
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
        deleteModalOpen,
        setDeleteModalOpen,
        requestState
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
