import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIProgramAreaList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import { fetchAdvancedSearchData } from "../../../../../apiManager/services/FOI/foiAdvancedSearchServices";
import { fetchHistoricalSearchData } from "../../../../../apiManager/services/FOI/foiHistoricalSearchServices";
import { errorToast } from "../../../../../helper/FOI/helper";
import { setAdvancedSearchParams, setHistoricalSearchParams } from "../../../../../actions/FOI/foiRequestActions";
export const ActionContext = createContext();
ActionContext.displayName = "AdvancedSearchContext";
export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const [queryData, setQueryData] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [advancedSearchComponentLoading, setAdvancedSearchComponentLoading] =
    useState(true);

  const [queryHistoricalData, setQueryHistoricalData] = useState(null);
  const [searchHistoricalDataLoading, setHistoricalSearchLoading] = useState(false);
  const [historicalSearchComponentLoading, setHistoricalSearchComponentLoading] =
      useState(true);  

  const [searchResults, setSearchResults] = useState(null);
  const [searchHistoricalSearchResults, setHistoricalSearchResults] = useState(null);

  const advancedSearchParams = useSelector((state) => state.foiRequests.foiAdvancedSearchParams);
  const historicSearchParams = useSelector((state) => state.foiRequests.foiHistoricalSearchParams);

  const handleUpdateSearchFilter = (filterData) => {
    dispatch(setAdvancedSearchParams(filterData))
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  const handleUpdateHistoricSearchFilter = (filterData) => {
    dispatch(setHistoricalSearchParams(filterData))
    setQueryHistoricalData({ ...(queryHistoricalData || {}), ...filterData });
  };

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];

  const defaultHistoricSearchSortModel = [    
    { field: "receivedDate", sort: "desc" },
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

    if(queryHistoricalData)
      {
        
      fetchHistoricalSearchData({
        ...queryHistoricalData,
        callback: (data) => {
          setHistoricalSearchLoading(false);
          setHistoricalSearchComponentLoading(false);
          setHistoricalSearchResults(data);
        },
        errorCallback: (error) => {
          setHistoricalSearchLoading(false);
          setHistoricalSearchComponentLoading(false);
          errorToast(error);
        },
        dispatch,
      });
      }
  }, [queryData,queryHistoricalData]);

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

        handleUpdateHistoricSearchFilter,
        searchHistoricalDataLoading,
        setHistoricalSearchLoading,
        searchHistoricalSearchResults,
        queryHistoricalData,
        defaultHistoricSearchSortModel,
        historicalSearchComponentLoading,
        setHistoricalSearchComponentLoading,
        historicSearchParams,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
