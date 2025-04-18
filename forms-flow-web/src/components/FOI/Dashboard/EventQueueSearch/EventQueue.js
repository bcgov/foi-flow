import React, { useEffect, useMemo, useState, useContext } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIEventListByPage, fetchFOIMinistryEventListByPage } from "../../../../apiManager/services/FOI/foiEventDashboardServices";
import Loading from "../../../../containers/Loading";
import { setEventQueueFilter, setEventQueueParams } from "../../../../actions/FOI/foiRequestActions";
import {
  debounce,
  ClickableChip,
  updateEventSortModel,
} from "../utils";
import { isMinistryLogin } from "../../../../helper/FOI/helper";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { CustomFooter } from "../CustomFooter"
import { ActionContext } from "./ActionContext";

const EventQueue = ({ userDetail, eventQueueTableInfo }) => {
  const dispatch = useDispatch();

  const userGroups = userDetail?.groups?.map(group => group.slice(1));
  const isMinistry = isMinistryLogin(userGroups);
  const eventQueue = useSelector((state) => state.foiRequests.foiEventsList);
  const isEventsLoading = useSelector((state) => state.foiRequests.isEventsLoading);
  const classes = useStyles();

  const { showEventQueueTable } = useContext(ActionContext);
  const [loading, setLoading] = useState(false);

  const filterFields = [
    "createdat",
    "axisRequestId",
    "creatorFormatted",
    "assignedToFormatted",
    "userFormatted",    
    "notification"
  ];

  const ministryFilterFields = [
    "createdat",
    "axisRequestId",
    "creatorFormatted",
    "ministryAssignedToFormatted",
    "userFormatted",    
    "notification"
  ];

  const eventQueueParams = useSelector((state) => state.foiRequests.eventQueueParams);
  const rowsState = useSelector((state) => state.foiRequests.eventQueueParams?.rowsState);
  const sortModel = useSelector((state) => state.foiRequests.eventQueueParams?.sortModel || eventQueueTableInfo.sort);

  let serverSortModel;

  const keyword = useSelector((state) => state.foiRequests.eventQueueParams?.keyword);
  const eventFilter = useSelector((state) => state.foiRequests.eventQueueFilter);
  const dateFilter = useSelector((state) => state.foiRequests.eventQueueParams.dateFilter);

  useEffect(() => {
    if (!showEventQueueTable) {
      setLoading(false);
      return;
    } 

    const { dateRangeType, fromDate, toDate } = dateFilter || {};
    if (!dateRangeType || !fromDate || !toDate) {
      setLoading(false);
      return;
    }

    serverSortModel = updateEventSortModel(sortModel, isMinistry);
    
    if (isMinistry) {
      dispatch(
        fetchFOIMinistryEventListByPage(
          rowsState.page + 1,
          rowsState.pageSize,
          serverSortModel,
          ministryFilterFields,
          keyword,
          eventFilter,
          userDetail.preferred_username,
          dateFilter?.dateRangeType,
          dateFilter?.fromDate,
          dateFilter?.toDate,
        )
      );
    } else {
      dispatch(
        fetchFOIEventListByPage(
          rowsState.page + 1,
          rowsState.pageSize,
          serverSortModel,
          filterFields,
          keyword,
          eventFilter, 
          userDetail.preferred_username,
          dateFilter?.dateRangeType,
          dateFilter?.fromDate,
          dateFilter?.toDate,
        )
      );
    }
    setLoading(true)
  }, [rowsState, sortModel, keyword, eventFilter]); 
  
  const eventColumnsRef = React.useRef(eventQueueTableInfo?.columns || []);

  const requestFilterChange = (filter) => {
    if (filter === eventFilter) {
      return;
    }
    dispatch(setEventQueueParams({...eventQueueParams, rowsState: {...rowsState, page: 0}}));
    dispatch(setEventQueueFilter(filter));
  };

  const setSearch = debounce((e) => {
    dispatch(setEventQueueParams({
      ...eventQueueParams,
      keyword: e.target.value.trim(),
      rowsState: {...rowsState, page: 0}
    }));
  }, 500);

  const rows = useMemo(() => {
    return eventQueue?.data || [];
  }, [JSON.stringify(eventQueue)]);


  const renderReviewRequest = (e) => {
    let url = ''
    
    if (e.row?.notificationType?.toLowerCase()?.includes('comments')) {
      url = redirectToComments(isMinistry, e.row.rawrequestid, e.row.requestid, e.row.ministryrequestid)
    }
    else if (e.row?.notificationType?.toLowerCase()?.includes('pdfstitch')) {
      url = redirectToRecords(isMinistry, e.row.requestid, e.row.ministryrequestid)
    }
    else {
      url = redirectToRequestView(isMinistry, e.row.rawrequestid, e.row.requestid, e.row.ministryrequestid)
    }    
    dispatch(push(url));

  }


  const redirectToRequestView = (isMinistry, rawrequestid, requestid,  ministryrequestid) => {
    let url = "";
    if (isMinistry) {
      url = `/foi/ministryreview/${requestid}/ministryrequest/${ministryrequestid}`
    }
    else if (ministryrequestid) {
      url = `/foi/foirequests/${requestid}/ministryrequest/${ministryrequestid}`
    }
    else {
      url = `/foi/reviewrequest/${rawrequestid}`
    }
    return url;
  }

  const redirectToComments = (isMinistry, rawrequestid, requestid,  ministryrequestid) => {
    let url = "";
    if (isMinistry) {
      url = `/foi/ministryreview/${requestid}/ministryrequest/${ministryrequestid}/comments`
    }
    else if (ministryrequestid) {
      url = `/foi/foirequests/${requestid}/ministryrequest/${ministryrequestid}/comments`
    }
    else {
      url = `/foi/reviewrequest/${rawrequestid}/comments`
    }
    return url;
  }

  const redirectToRecords = (isMinistry, requestid,  ministryrequestid) => {
    let url = "";
    if (isMinistry) {
      url = `/foi/ministryreview/${requestid}/ministryrequest/${ministryrequestid}/records`
    }
    else {
      url = `/foi/foirequests/${requestid}/ministryrequest/${ministryrequestid}/records`
    }   
    return url;
  }

  if (eventQueue === null && loading) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }

  const handleSortChange = (model) => {
    if (model.length === 0) {
      return;
    }
    dispatch(setEventQueueParams({...eventQueueParams, sortModel: model}));
  };

  return (
    <>
    { loading && (
      <>
        <Grid item container alignItems="center" xs={12}>
          <Paper
            component={Grid}
            sx={{
              border: "1px solid #38598A",
              color: "#38598A",
            }}
            alignItems="center"
            justifyContent="center"
            direction="row"
            container
            item
            xs={12}
            elevation={0}
          >
            <Grid
              item
              container
              alignItems="center"
              direction="row"
              xs={true}
              sx={{
                borderRight: "2px solid #38598A",
                backgroundColor: "rgba(56,89,138,0.1)",
              }}
            >
              <label className="hideContent" for="filter">Search in Queue</label>
              <InputBase
                id="filter"
                placeholder="Search in Queue ..."
                defaultValue={keyword}
                onChange={setSearch}
                sx={{
                  color: "#38598A",
                }}
                startAdornment={
                  <InputAdornment position="start">
                    <IconButton sx={{ color: "#38598A" }}>
                      <span className="hideContent">Search in Queue</span>
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                }
                fullWidth
              />
            </Grid>
            <Grid
              item
              container
              alignItems="flex-start"
              justifyContent="center"
              xs={3}
              minWidth="390px"
            >
              <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
                <ClickableChip
                  id="myRequests"
                  key={`my-requests`}
                  label={"MY REQUESTS"}
                  color="primary"
                  size="small"
                  onClick={() => requestFilterChange("myRequests")}
                  clicked={eventFilter === "myRequests"}
                />
                <ClickableChip
                  id="teamRequests"
                  key={`team-requests`}
                  label={"MY TEAM'S REQUESTS"}
                  color="primary"
                  size="small"
                  onClick={() => requestFilterChange("All")}
                  clicked={eventFilter === "All"}
                />
                <ClickableChip
                  id="watchingRequests"
                  key={`watching-requests`}
                  label={"WATCHING REQUESTS"}
                  color="primary"
                  size="small"
                  onClick={() => requestFilterChange("watchingRequests")}
                  clicked={eventFilter === "watchingRequests"}
                />
              </Stack>
            </Grid>
          </Paper>
        </Grid>
        <Grid item xs={12} style={{ minHeight: 300 }} className={classes.root}>      
          <DataGrid
            autoHeight
            className="foi-data-grid"
            getRowId={(row) => row.id}
            rows={rows}
            columns={eventColumnsRef.current}
            rowHeight={30}
            headerHeight={50}
            rowCount={eventQueue?.meta?.total || 0}
            pageSize={rowsState?.pageSize}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
            paginationMode="server"
            page={rowsState?.page}
            onPageChange={(newPage) => dispatch(setEventQueueParams({...eventQueueParams, rowsState: {...rowsState, page: newPage}}))}
            onPageSizeChange={(newpageSize) =>
              dispatch(setEventQueueParams({...eventQueueParams, rowsState: {...rowsState, pageSize: newpageSize}}))
            }
            components={{
              Footer: ()=> <CustomFooter rowCount={eventQueue?.meta?.total || 0} defaultSortModel={eventQueueTableInfo.sort} footerFor={"queue"}></CustomFooter>
            }}
            sortingOrder={["asc", "desc"]}
            sortModel={[sortModel[0]]}
            sortingMode={"server"}
            onSortModelChange={(model) => {
              if (model) {
                handleSortChange(model);
              }
            }}
            onRowClick={renderReviewRequest}
            loading={isEventsLoading}
          />
        </Grid>
      </>
    )} 
    </>
  );
};

export default EventQueue;
