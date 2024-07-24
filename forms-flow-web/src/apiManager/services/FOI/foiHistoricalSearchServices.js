import { httpGETRequest } from "../../httpRequestHandler";
import API from "../../endpoints";
import { catchError } from "./foiServicesUtil";
import UserService from "../../../services/UserService";

export const fetchHistoricalSearchData = ({
  page = 1,
  size = 10,
  sort = [{ field: "receivedDate", sort: "desc" }],  
  search = "",
  keywords = [],  
  requestType = [],
  requestFlags = [],
  dateRangeType = null,
  fromDate = null,
  toDate = null,
  publicBodies = [],
  callback,
  errorCallback,
  dispatch,
}) => {
  // let sortingItems = [];
  // let sortingOrders = [];
  // sort.forEach((item) => {
  //   sortingItems.push(item.field);
  //   sortingOrders.push(item.sort);
  // });

  if (sort[0].field === 'axisrequestid') {
    sort[0].field = 'visualrequestfilenumber'
  }

  httpGETRequest(
    API.FOI_HISTORICAL_SEARCH_API,
    {
      page: page,
      size: size,
      sortingitem: sort[0]['field'],
      sortingorder: sort[0]['sort'],
      search: search,
      keywords: keywords,
      requestType: requestType,
      requestFlags: requestFlags,
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
      errorCallback("Error in fetching historicalsearch for IAO");
    });
};
