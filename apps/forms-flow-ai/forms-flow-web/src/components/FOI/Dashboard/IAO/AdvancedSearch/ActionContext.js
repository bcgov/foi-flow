import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  return <ActionContext.Provider value={{}}>{children}</ActionContext.Provider>;
};
