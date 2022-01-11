import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchExtensionReasons } from "../../../../apiManager/services/FOI/foiExtensionServices";
import { formatDate } from "../../../../helper/FOI/helper";
export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();

  const [modalOpen, setModalOpen] = useState();
  const [extensionReasons, setExtensionReasons] = useState()
  
  const currentDueDate = formatDate(requestDetails.dueDate)
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.dueDate);
  const extensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );
  return (
    <ActionContext.Provider
      value={{
        modalOpen,
        setModalOpen,
        extensionReasons,
        setExtensionReasons,
        dispatch,
        currentDueDate,
        startDate,
        extensions
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
