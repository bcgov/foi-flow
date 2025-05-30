import { httpGETRequest, httpPOSTRequest} from "../../httpRequestHandler";
import API from "../../endpoints";
import { catchError } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { FOI_SOLR_API_BASE } from "../../../constants/constants";


export const getCrossTextSearchAuth = ({
  callback,
  errorCallback,
  dispatch,
}) => {

  httpGETRequest(
    API.FOI_GET_CROSSTEXTSEARCH_AUTH,
    UserService.getToken()
  )
    .then((res) => {
      if (res.data) {
        //console.log("res:",res)
        const result = res.data;
        callback(result);
      } else {
        errorCallback("Failed to retrieve auth data");
      }
    })
    .catch((error) => {
      catchError(error, dispatch);
      errorCallback("Error in fetching auth for Solr search - ",error);
    });
};

export const getSolrKeywordSearchData = ({
    queryParams,
    authorization,
    callback,
    errorCallback,
    dispatch,
  }) => {

    let isBearer = false;  
    const serializedQueryParams = new URLSearchParams(queryParams).toString();
    const fixedQueryParams = serializedQueryParams.replace(/\+/g, '%20');
    let solrEndPoint = `${FOI_SOLR_API_BASE}/select?${fixedQueryParams}`; 
    httpGETRequest(
      solrEndPoint,
      {},
      authorization,
      isBearer
    )
      .then((res) => {
        if (res && res.status == 200) {
          callback(res.data.response.docs);
        } else {
          errorCallback("No results found for the given search parameters.");
        }
      })
      .catch((error) => {
        console.log(error)
        catchError(error, dispatch);
        errorCallback("Error in fetching keyword search data.", error);
      });
  };

  
  export const getKeywordSearchRequestDetails = ({
    foirequestNumbers,
    callback,
    errorCallback,
    dispatch,
  }) => {
    let requestjson={"requestnumbers":foirequestNumbers}
    let apiUrlPost = API.FOI_GET_CROSSTEXTSEARCH_REQUEST_DETAILS;
    httpPOSTRequest(apiUrlPost, requestjson, UserService.getToken() ?? '', true)
      .then((res) => {
        if (res.data) {           
          callback(res.data);
        } else {
          errorCallback("Failed to retrieve keyword search request details.");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
        errorCallback("Error in fetching keyword search request details.");
      });
  };