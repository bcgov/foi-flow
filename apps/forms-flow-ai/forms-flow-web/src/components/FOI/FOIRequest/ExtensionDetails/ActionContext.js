import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { formatDate } from "../../../../helper/FOI/helper";
import { useParams } from "react-router-dom";
import {
  fetchExtensionReasons,
  fetchExtension,
} from "../../../../apiManager/services/FOI/foiExtensionServices";

export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {

  const dispatch = useDispatch();
  const { requestId } = useParams();

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

  const filterExtensionReason = (extensionReasonsToFilter) => {
    if(!extensions || extensions.length < 1) {
      return extensionReasonsToFilter;
    }

    if (extensions.some((ex) => ex.extensiontype === "Public Body")) {
      return extensionReasonsToFilter.filter((ex) => {
        return ex.extensiontype !== "Public Body";
      });
    }

    return extensionReasonsToFilter;
  }

  useEffect(() => {
    if (requestId) {
      fetchExtensionReasons({
        callback: (data) => {
          const filteredExtensionReasons = filterExtensionReason(data)
          setExtensionReasons(filteredExtensionReasons);
        },
        dispatch: dispatch,
      });
    }
  }, [extensions]);

  useEffect(() => {
    if(extensionId && modalOpen) {
      setLoading(true)
      fetchExtension({
        extensionId: extensionId,
        callback: (data) => {
          setSelectedExtension(data);
        },
        dispatch: dispatch,
      });
    }
  }, [modalOpen])

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
        idNumber
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
