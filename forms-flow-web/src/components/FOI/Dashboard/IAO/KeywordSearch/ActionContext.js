import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIProgramAreaList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import { fetchAdvancedSearchData } from "../../../../../apiManager/services/FOI/foiAdvancedSearchServices";
import {getCrossTextSearchAuth, getSolrKeywordSearchData, 
  getKeywordSearchRequestDetails} from "../../../../../apiManager/services/FOI/foiKeywordSearchServices"
import { errorToast } from "../../../../../helper/FOI/helper";
import { setKeywordSearchParams } from "../../../../../actions/FOI/foiRequestActions";

export const ActionContext = createContext();
ActionContext.displayName = "KeywordSearchContext";
export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const [queryData, setQueryData] = useState(null);
  const [keywordSearchLoading, setKeywordSearchLoading] = useState(false);
  const [keywordSearchComponentLoading, setKeywordSearchComponentLoading] =
    useState(true);

  const [searchResults, setSearchResults] = useState(null);
  const keywordSearchParams = useSelector((state) => state.foiRequests.foiKeywordSearchParams);


  const handleUpdateSearchFilter = (filterData) => {
    dispatch(setKeywordSearchParams(filterData))
    setQueryData({ ...(queryData || {}), ...filterData });
  };

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];


  useEffect(() => {
    dispatch(fetchFOIProgramAreaList());
  }, [dispatch]);


const generateSolrQueryParams = (queryData) => {
  let queryParts = [];
  if (queryData.keywords.length > 0) {
    const keywords = queryData.keywords
      .map(keyword => `${keyword}`) // Properly quote keywords
      .join(",");
    queryParts.push(keywords);
  }
  // Handle received date range
  if (queryData.fromDate || queryData.toDate) {
    const fromDate = convertToISO(queryData.fromDate);
    const toDate = convertToISO(queryData.toDate);
    queryParts.push(`foirequestreceiveddate:[${fromDate} TO ${toDate}]`);
  }
  // Handle public bodies
  if (queryData.publicBodies?.length >0) {
    queryParts.push(`foiministrycode:${queryData.publicBodies}`);
  }
  const query = queryParts.join(" AND ");
  console.log("\nquery:",query)
  return { df: "foidocumentsentence", q: query };
};

const convertToISO = (dateStr) => {
  if(!!dateStr){
    const date = new Date(`${dateStr}T00:00:00Z`);
    // Convert to ISO 8601 format
    return date.toISOString();
  }
  else
    return "*";
};
  

  useEffect(() => {
    if (queryData) {
      let queryParams = generateSolrQueryParams(queryData) 
      getCrossTextSearchAuth({
        callback: (authToken) => {
          if (authToken) {
            // Call Solr API after getting the auth token
            getSolrKeywordSearchData({
              queryParams,
              authorization: `Basic ${authToken}`, 
            callback: (responseDocs) => {  
              //console.log("responseDocs:",responseDocs)
              const foirequestNumbers = [...new Set(
                responseDocs
                  .map((doc) => doc.foirequestnumber)
                  .flat()
              )];
              if(foirequestNumbers.length>0){
                getKeywordSearchRequestDetails({
                  foirequestNumbers,
                  callback: (data) => {
                    setKeywordSearchLoading(false);
                    setKeywordSearchComponentLoading(false);
                    setSearchResults(data || []);
                  },
                  errorCallback: (error) => {
                    setKeywordSearchLoading(false);
                    setKeywordSearchComponentLoading(false);
                    errorToast(error);
                  },
                  dispatch,
                })
              }
              else{
                setKeywordSearchComponentLoading(false);
              }
            },
            errorCallback: (message) => {
              console.error(message);
              errorToast(message); 
            },
            dispatch,
          })
          } else {
            console.error("Authorization token not found.");
            errorToast("Authorization failed."); 
          }
        },
        errorCallback: (message) => {
          console.error(message);
          errorToast(message); 
        },
        dispatch,
      })
      setKeywordSearchComponentLoading(false);
    }
  }, [queryData]);

  return (
    <ActionContext.Provider
      value={{
        handleUpdateSearchFilter,
        keywordSearchLoading,
        setKeywordSearchLoading,
        searchResults,
        queryData,
        defaultSortModel,
        keywordSearchComponentLoading,
        setKeywordSearchComponentLoading,
        keywordSearchParams,
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
