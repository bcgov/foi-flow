import { httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import { catchError } from "./foiServicesUtil";
import UserService from "../../../services/UserService";

export const fetchAdvancedSearchData = ({
  page = 1,
  size = 10,
  sort = [{ field: "currentState", sort: "desc" }],
  userID = null,
  search = "",
  keywords = [],
  requestState = [],
  requestStatus = [],
  requestType = [],
  dateRangeType = null,
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
      requestStatus: requestStatus,
      requestType: requestType,
      dateRangeType: dateRangeType,
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
