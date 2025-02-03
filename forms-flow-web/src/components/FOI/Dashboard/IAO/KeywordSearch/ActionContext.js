import React, { createContext, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIProgramAreaList } from "../../../../../apiManager/services/FOI/foiMasterDataServices";
import {getCrossTextSearchAuth, getSolrKeywordSearchData, 
  getKeywordSearchRequestDetails} from "../../../../../apiManager/services/FOI/foiKeywordSearchServices"
import { errorToast } from "../../../../../helper/FOI/helper";
//import { setKeywordSearchParams } from "../../../../../actions/FOI/foiRequestActions";
import { SOLR_DOC_SEARCH_LIMIT } from "../../../../../constants/constants";

export const ActionContext = createContext();
ActionContext.displayName = "KeywordSearchContext";
export const ActionProvider = ({ children }) => {
  const dispatch = useDispatch();

  const [queryData, setQueryData] = useState(null);
  const [keywordSearchLoading, setKeywordSearchLoading] = useState(false);
  const [keywordSearchComponentLoading, setKeywordSearchComponentLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [foiKeywordSearchParams, setFoiKeywordSearchParams] = useState({});

  const handleUpdateSearchFilter = (filterData) => {
    setFoiKeywordSearchParams(filterData);
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
  let booleanKeywords=[];
  if (queryData.keywords.length > 0) {
    let andKeywords= queryData.keywords?.filter(
      (keyword) =>(keyword.category === "AND"));
    let orKeywords= queryData.keywords?.filter(
      (keyword) =>(keyword.category === "OR"));
    let notKeywords= queryData.keywords?.filter(
      (keyword) =>(keyword.category === "NOT"));

    if (andKeywords.length > 0) {
      let andPart = andKeywords.map((keyword) => keyword.text).join(" AND ");
      booleanKeywords.push(andPart);
    }
    if (orKeywords.length > 0) {
      let orPart = orKeywords.map((keyword) => keyword.text).join(" OR ");
      booleanKeywords.push(orPart);
    }
    if (notKeywords.length > 0) {
      let notPart = notKeywords.map((keyword) => `NOT ${keyword.text}`).join(" NOT ");
      // if (booleanKeywords.length > 0) {
      //   notPart += ` NOT ${booleanKeywords}`;
      // }
      booleanKeywords.push(notPart);
    }
    if (booleanKeywords.length > 0) {
      queryParts.push(booleanKeywords.join(" "));
    }
    //queryParts.push(keywords);
    console.log("\nqueryParts::",queryParts);
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
  return { df: "foidocumentsentence", q: query, rows:SOLR_DOC_SEARCH_LIMIT };
};

const convertToISO = (dateStr) => {
  if(!!dateStr){
    const date = new Date(`${dateStr}T00:00:00Z`);
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
                setSearchResults([]);
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
        foiKeywordSearchParams,
        setFoiKeywordSearchParams
      }}
    >
      {children}
    </ActionContext.Provider>
  );
};
