import React, { useEffect, useMemo } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "./dashboard.scss";
import useStyles from "./CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIEventListByPage, fetchFOIMinistryRequestListByPage } from "../../../apiManager/services/FOI/foiEventDashboardServices";
import Loading from "../../../containers/Loading";
import { setEventQueueFilter, setEventQueueParams } from "../../../actions/FOI/foiRequestActions";
import {
  debounce,
  ClickableChip,
  updateSortModel,
} from "./utils";
import { isMinistryLogin } from "../../../helper/FOI/helper";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { CustomFooter } from "./CustomFooter"

const EventQueue = ({ userDetail, eventQueueTableInfo }) => {
  const dispatch = useDispatch();

  const userGroups = userDetail && userDetail?.groups?.map(group => group.slice(1));
  const isMinistry = isMinistryLogin(userGroups);
  console.log(`isMinistry == ${isMinistry}`)
  const eventQueue = useSelector((state) => state.foiRequests.foiEventsList);
  const isLoading = useSelector((state) => state.foiRequests.isLoading);
  console.log(`eventQueue == ${JSON.stringify(eventQueue)}`)
  const classes = useStyles();

  const filterFields = [
    "createdat",
    "axisRequestId",
    "createdby",    
    "assignedTo",
    "assignedToLastName",
    "assignedToFirstName",
    "assignedGroup",
    "assignedministrygroup",
    "assignedministrypersonFirstName",
    "assignedministrypersonLastName",
    "to",
    "notification"
  ];

  const eventQueueParams = useSelector((state) => state.foiRequests.eventQueueParams);
  const rowsState = useSelector((state) => state.foiRequests.eventQueueParams?.rowsState);
  const sortModel = useSelector((state) => state.foiRequests.eventQueueParams?.sortModel || eventQueueTableInfo.sort);

  let serverSortModel;


  const keyword = useSelector((state) => state.foiRequests.eventQueueParams?.keyword);
  const eventFilter = useSelector((state) => state.foiRequests.eventQueueFilter);

  console.log(`eventFilter = ${JSON.stringify(eventFilter)}`)

  useEffect(() => {
    serverSortModel = updateSortModel(sortModel);
    console.log(`isMinistry UE == ${isMinistry}`)
    if (isMinistry)
    {
      // page+1 here, because initial page value is 0 for mui-data-grid
      dispatch(
        fetchFOIMinistryRequestListByPage(
          rowsState.page + 1,
          rowsState.pageSize,
          serverSortModel,
          filterFields,
          keyword,
          eventFilter,
          userDetail.preferred_username
        )
      );

    } else {
      // page+1 here, because initial page value is 0 for mui-data-grid
      dispatch(
        fetchFOIEventListByPage(
          rowsState.page + 1,
          rowsState.pageSize,
          serverSortModel,
          filterFields,
          keyword,
          eventFilter,
          userDetail.preferred_username
        )
      );
      }
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

  console.log(`rows == ${JSON.stringify(rows)}`)

  const renderReviewRequest = (e) => {
    let url = ''
    if (e.row?.status?.toLowerCase() !== 'archived') {
      if (e.row?.notificationType?.toLowerCase()?.includes('comments')) {
        if (isMinistry) {
          url = `/foi/ministryreview/${e.row.requestid}/ministryrequest/${e.row.ministryrequestid}/commnets`
        }
        else if (e.row.ministryrequestid) {
          url = `/foi/foirequests/${e.row.requestid}/ministryrequest/${e.row.ministryrequestid}/commnets`
        }
        else {
          url = `/foi/reviewrequest/${e.row.requestid}/commnets`
        }
      }
      else {
        if (isMinistry) {
          url = `/foi/ministryreview/${e.row.requestid}/ministryrequest/${e.row.ministryrequestid}`
        }
        else if (e.row.ministryrequestid) {
          url = `/foi/foirequests/${e.row.requestid}/ministryrequest/${e.row.ministryrequestid}`
        }
        else {
          url = `/foi/reviewrequest/${e.row.requestid}`
        }
      }    
      dispatch(push(url));
    }
  };

  if (eventQueue === null) {
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
          columns={eventQueueTableInfo?.columns || []}
          rowHeight={30}
          headerHeight={50}
          rowCount={eventQueue?.meta?.total || 0}
          pageSize={rowsState?.pageSize}
          // rowsPerPageOptions={[10]}
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
          sortingOrder={["desc", "asc"]}
          sortModel={[sortModel[0]]}
          sortingMode={"server"}
          onSortModelChange={(model) => {
            if (model) {
              handleSortChange(model);
            }
          }}
          // getRowClassName={(params) =>
          //   clsx(
          //     `super-app-theme--${params.row.currentState
          //       .toLowerCase()
          //       .replace(/ +/g, "")}`,
          //       eventQueueTableInfo?.stateClassName?.[
          //       params.row.currentState.toLowerCase().replace(/ +/g, "")
          //     ],
          //     (params.row.assignedTo == null && userDetail?.groups?.indexOf("/" + params.row.assignedGroup) > -1)
          //     && eventQueueTableInfo?.noAssignedClassName
          //   )
          // }
          onRowClick={renderReviewRequest}
          loading={isLoading}
        />
      </Grid>
    </>
  );
};

export default EventQueue;
