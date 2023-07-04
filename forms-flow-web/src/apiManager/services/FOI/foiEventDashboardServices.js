import {
  httpGETRequest,
} from "../../httpRequestHandler";
import API from "../../endpoints";
import {
  setFOIEventList,
  serviceActionError,
  setFOIEventsLoader,
  setFOIMinistryEventList
} from "../../../actions/FOI/foiRequestActions";
import { fetchFOIAssignedToList, fetchFOIMinistryAssignedToList, fetchFOIProcessingTeamList } from "./foiMasterDataServices";
import { catchError} from './foiServicesUtil';
import UserService from "../../../services/UserService";

export const fetchFOIEventListByPage = (
  page = 1,
  size = 10,
  sort = [{ field: "defaultSorting", sort: "asc" }],
  filters = null,
  keyword = null,
  additionalFilter = "All",
  userID = null
) => {
  let sortingItems = [];
  let sortingOrders = [];
  sort.forEach((item) => {
    sortingItems.push(item.field);
    sortingOrders.push(item.sort);
  });

  return (dispatch) => {
    dispatch(setFOIEventList(null));
    dispatch(setFOIEventsLoader(true));
    httpGETRequest(
      API.FOI_GET_EVENTS_PAGE_API,
      {
        page: page,
        size: size,
        sortingitems: sortingItems,
        sortingorders: sortingOrders,
        filters: filters,
        keyword: keyword,
        additionalfilter: additionalFilter,
        userid: userID,
      },
      UserService.getToken()
    )
      .then((res) => {
        if (res.data) {
          dispatch(setFOIEventList(res.data));
          dispatch(setFOIEventsLoader(false));
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for IAO");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};

export const fetchFOIMinistryEventListByPage = (page = 1, size = 10, sort = [{field:'defaultSorting', sort:'asc'}], filters = null, keyword = null, additionalFilter = 'All', userID = null) => {
  let sortingItems = [];
  let sortingOrders = [];
  sort.forEach((item)=>{
    sortingItems.push(item.field);
    sortingOrders.push(item.sort);
  });

  return (dispatch) => {
    dispatch(setFOIEventList(null));
    dispatch(setFOIEventsLoader(true));    
    httpGETRequest(
          API.FOI_GET_MINISTRY_EVENTS_PAGE_API,
          {
            "page": page,
            "size": size,
            "sortingitems": sortingItems,
            "sortingorders": sortingOrders,
            "filters": filters,
            "keyword": keyword,
            "additionalfilter": additionalFilter,
            "userid": userID
          },
          UserService.getToken())
      .then((res) => {
        if (res.data) {
          // dispatch(setFOIMinistryEventList(res.data));
          dispatch(setFOIEventList(res.data));
          dispatch(setFOIEventsLoader(false));
          if (res.data?.data[0]?.bcgovcode)
            dispatch(fetchFOIMinistryAssignedToList(res.data.data[0].bcgovcode));     
        } else {
          dispatch(serviceActionError(res));
          throw new Error("Error in fetching dashboard data for IAO");
        }
      })
      .catch((error) => {
        catchError(error, dispatch);
      });
  };
};
