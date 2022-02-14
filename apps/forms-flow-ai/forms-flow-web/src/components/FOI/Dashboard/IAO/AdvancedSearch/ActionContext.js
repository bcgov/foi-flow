import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { fetchFOIFullAssignedToList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import { fetchAdvancedSearchData } from "../../../../../apiManager/services/FOI/foiAdvancedSearchServices";
import { errorToast } from "../../../../../helper/FOI/helper";
export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children, requestDetails }) => {
  const dispatch = useDispatch();
  const { requestId, ministryId } = useParams();

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  const handleUpdateSearchFilter = (filterData) => {
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  useEffect(() => {
    if (queryData) {
      console.log("not empty", queryData);
      fetchAdvancedSearchData({
        ...queryData,
        callback: (data) => {
          setSearchLoading(false);
          setSearchResults(data);
        },
        errorCallback: (error) => {
          setSearchLoading(false);
          errorToast(error);
        },
        dispatch,
      });
    }
  }, [queryData]);

  return (
    <ActionContext.Provider
      value={{
        handleUpdateSearchFilter,
        searchLoading,
        setSearchLoading,
        searchResults,
        queryData,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
