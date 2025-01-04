import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIProgramAreaList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import { fetchAdvancedSearchData } from "../../../../../apiManager/services/FOI/foiAdvancedSearchServices";
import { errorToast } from "../../../../../helper/FOI/helper";
import { setAdvancedSearchParams } from "../../../../../actions/FOI/foiRequestActions";
export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [advancedSearchComponentLoading, setAdvancedSearchComponentLoading] =
    useState(true);
  const [searchResults, setSearchResults] = useState(null);
  const advancedSearchParams = useSelector((state) => state.foiRequests.foiAdvancedSearchParams);

  const handleUpdateSearchFilter = (filterData) => {
    dispatch(setAdvancedSearchParams(filterData))
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    // { field: "receivedDateUF", sort: "desc" },
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
          setAdvancedSearchComponentLoading(false);
          setSearchResults(data);
        },
        errorCallback: (error) => {
          setSearchLoading(false);
          setAdvancedSearchComponentLoading(false);
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
        advancedSearchComponentLoading,
        setAdvancedSearchComponentLoading,
        advancedSearchParams,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
