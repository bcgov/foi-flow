import React, { createContext } from "react";
import { useDispatch, useSelector } from "react-redux";
import { formatDate } from "../../../../../helper/FOI/helper";

export const ActionContext = createContext();
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();
  
  const currentDueDate = formatDate(requestDetails.dueDate)
  const startDate = formatDate(requestDetails.requestProcessStart);
  const originalDueDate = formatDate(requestDetails.originalDueDate);
  const extensions = useSelector(
    (state) => state.foiRequests.foiRequestExtesions
  );

  return (
    <ActionContext.Provider
      value={{
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
