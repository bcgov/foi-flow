import { httpPOSTRequest, httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import { catchError, fnDone } from "./foiServicesUtil";
import UserService from "../../../services/UserService";
import { replaceUrl } from "../../../helper/FOI/helper";

export const fetchAdvancedSearchData = ({
  page = 1,
  size = 10,
  sort = [{ field: "currentState", sort: "desc" }],
  userID = null,
  search = "",
  keywords = [],
  requestState = [],
  requestType = [],
  fromDate = null,
  toDate = null,
  publicBodies = [],
  callback,
  errorCallback,
  dispatch,
}) => {
  let sortingItems = [];
  let sortingOrders = [];
  sort.forEach((item) => {
    sortingItems.push(item.field);
    sortingOrders.push(item.sort);
  });

  console.log({
    page: page,
    size: size,
    sortingitems: sortingItems,
    sortingorders: sortingOrders,
    userid: userID,
    search: search,
    keywords: keywords,
    requestState: requestState,
    requestType: requestType,
    fromDate: fromDate,
    toDate: toDate,
    publicBodies: publicBodies,
  });

  httpGETRequest(
    API.FOI_GET_ADVANCED_SEARCH,
    {
      page: page,
      size: size,
      sortingitems: sortingItems,
      sortingorders: sortingOrders,
      userid: userID,
      search: search,
      keywords: keywords,
      requestState: requestState,
      requestType: requestType,
      fromDate: fromDate,
      toDate: toDate,
      publicBodies: publicBodies,
    },
    UserService.getToken()
  )
    .then((res) => {
      if (res.data) {
        callback(res.data);
      } else {
        throw new Error();
      }
    })
    .catch((error) => {
      catchError(error, dispatch);
      errorCallback("Error in fetching dashboard advanced search data for IAO");
    });
};
