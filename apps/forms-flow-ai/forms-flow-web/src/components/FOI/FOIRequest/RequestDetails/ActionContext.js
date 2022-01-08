import React, { createContext, useEffect, useState } from "react";
import { fetchExtensionReasons } from "../../../../apiManager/services/FOI/foiExtensionServices";
import { useDispatch } from "react-redux";
import { formatDate } from "../../../../helper/FOI/helper";
export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();

  const [modalOpen, setModalOpen] = useState();
  const [extensionReasons, setExtensionReasons] = useState()
  const [extensions, setExtensions] = useState([])
  
  const currentDueDate = formatDate(requestDetails.dueDate)
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.dueDate);

  useEffect(() => {
    console.log(requestDetails);
  }, [])
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
