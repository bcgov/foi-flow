import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { fetchFOIFullAssignedToList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";

export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  useEffect(() => {
    dispatch(fetchFOIFullAssignedToList());
  }, [dispatch]);

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  const handleUpdateSearchFilter = (filterData) => {
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
        handleUpdateSearchFilter,
        searchLoading,
        setSearchLoading,
        searchResults,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
