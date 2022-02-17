import React, { createContext, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { fetchFOIProgramAreaList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import { fetchAdvancedSearchData } from "../../../../../apiManager/services/FOI/foiAdvancedSearchServices";
import { errorToast } from "../../../../../helper/FOI/helper";
export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  const handleUpdateSearchFilter = (filterData) => {
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];

  useEffect(() => {
    dispatch(fetchFOIProgramAreaList());
  }, [dispatch]);

  useEffect(() => {
    if (queryData) {
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
        defaultSortModel,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
