import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { formatDate } from "../../../../helper/FOI/helper";
import { useParams } from "react-router-dom";
import {
  fetchExtensionReasons,
} from "../../../../apiManager/services/FOI/foiExtensionServices";

export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {

  const dispatch = useDispatch();
  const { requestId } = useParams();

  const [modalOpen, setModalOpen] = useState();
  const [extensionReasons, setExtensionReasons] = useState()
  
  const currentDueDate = formatDate(requestDetails.dueDate)
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.originalDueDate);
  const extensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );

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

  return (
    <ActionContext.Provider
      value={{
        modalOpen,
        setModalOpen,
        extensionReasons,
        dispatch,
        currentDueDate,
        originalDueDate,
        startDate,
        extensions
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
