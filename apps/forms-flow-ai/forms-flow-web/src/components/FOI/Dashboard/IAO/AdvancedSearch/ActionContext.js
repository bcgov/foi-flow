import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);

  const handleApplyFilterData = (filterData) => {
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  useEffect(() => {
    if (queryData) {
      // Get DataGrid data
      setSearchLoading(false);
    }
  }, [queryData]);

  return (
    <ActionContext.Provider
      value={{
        handleApplyFilterData,
        searchLoading,
        setSearchLoading,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
