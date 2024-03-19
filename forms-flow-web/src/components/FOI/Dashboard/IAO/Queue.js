import React, { useEffect, useMemo } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIRequestListByPage } from "../../../../apiManager/services/FOI/foiRequestServices";
import Loading from "../../../../containers/Loading";
import { setQueueFilter, setQueueParams } from "../../../../actions/FOI/foiRequestActions";
import {
  debounce,
  ClickableChip,
  updateSortModel,
} from "../utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import clsx from "clsx";
import { CustomFooter } from "../CustomFooter"

const Queue = ({ userDetail, tableInfo }) => {
  const dispatch = useDispatch();

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiRequestsList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();

  const filterFields = [
    "firstName",
    "lastName",
    "requestType",
    "idNumber",
    "axisRequestId",
    "currentState",
    "assignedToLastName",
    "assignedToFirstName",
  ];

  const queueParams = useSelector((state) => state.foiRequests.queueParams);
  const rowsState = useSelector((state) => state.foiRequests.queueParams?.rowsState);
  const sortModel = useSelector((state) => state.foiRequests.queueParams?.sortModel || tableInfo.sort);

  let serverSortModel;


  const keyword = useSelector((state) => state.foiRequests.queueParams?.keyword);
  const requestFilter = useSelector((state) => state.foiRequests.queueFilter);

  useEffect(() => {
    serverSortModel = updateSortModel(sortModel);
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(
      fetchFOIRequestListByPage(
        rowsState.page + 1,
        rowsState.pageSize,
        serverSortModel,
        filterFields,
        keyword,
        requestFilter,
        userDetail.preferred_username
      )
    );
  }, [rowsState, sortModel, keyword, requestFilter]);

  const columnsRef = React.useRef(tableInfo?.columns || []);
  if (requestFilter == 'unassignedRequests') {
    columnsRef.current = tableInfo.columns.concat(tableInfo.unassignedQueueColumns)
  }

  const requestFilterChange = (filter) => {
    if (filter === requestFilter) {
      return;
    }
    dispatch(setQueueParams({...queueParams, rowsState: {...rowsState, page: 0}}));
    dispatch(setQueueFilter(filter));
  };

  const setSearch = debounce((e) => {
    dispatch(setQueueParams({
      ...queueParams,
      keyword: e.target.value.trim(),
      rowsState: {...rowsState, page: 0}
    }));
  }, 500);

  const rows = useMemo(() => {
    return requestQueue?.data || [];
  }, [JSON.stringify(requestQueue)]);

  const renderReviewRequest = (e) => {
    if (e.row.ministryrequestid) {
      dispatch(
        push(
          `/foi/foirequests/${e.row.id}/ministryrequest/${e.row.ministryrequestid}`
        )
      );
    } else {
      dispatch(push(`/foi/reviewrequest/${e.row.id}`));
    }
  };

  if (requestQueue === null) {
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
    dispatch(setQueueParams({...queueParams, sortModel: model}));
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
            xs={'auto'}
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
                clicked={requestFilter === "myRequests"}
              />
              <ClickableChip
                id="teamRequests"
                key={`team-requests`}
                label={"MY TEAM'S REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("All")}
                clicked={requestFilter === "All"}
              />
              <ClickableChip
                id="watchingRequests"
                key={`watching-requests`}
                label={"WATCHING REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("watchingRequests")}
                clicked={requestFilter === "watchingRequests"}
              />
              <ClickableChip
                id="unassignedRequests"
                key={`unassigned-requests`}
                label={"UNASSIGNED REQUESTS"}
                color="primary"
                size="small"
                onClick={() => {
                  requestFilterChange("unassignedRequests")
                }}
                clicked={requestFilter === "unassignedRequests"}
              />
            </Stack>
          </Grid>
        </Paper>
      </Grid>
      <Grid item xs={12} style={{ minHeight: 300 }} className={classes.root}>
        <DataGrid
          autoHeight
          className="foi-data-grid"
          getRowId={(row) => row.idNumber}
          rows={rows}
          columns={columnsRef.current}
          rowHeight={30}
          headerHeight={50}
          rowCount={requestQueue?.meta?.total || 0}
          pageSize={rowsState?.pageSize}
          // rowsPerPageOptions={[10]}
          hideFooterSelectedRowCount={true}
          disableColumnMenu={true}
          pagination
          paginationMode="server"
          page={rowsState?.page}
          onPageChange={(newPage) => dispatch(setQueueParams({...queueParams, rowsState: {...rowsState, page: newPage}}))}
          onPageSizeChange={(newpageSize) =>
            dispatch(setQueueParams({...queueParams, rowsState: {...rowsState, pageSize: newpageSize}}))
          }
          components={{
            Footer: ()=> <CustomFooter rowCount={requestQueue?.meta?.total || 0} defaultSortModel={tableInfo.sort} footerFor={"queue"}></CustomFooter>
          }}
          sortingOrder={["desc", "asc"]}
          sortModel={[sortModel[0]]}
          sortingMode={"server"}
          onSortModelChange={(model) => {
            if (model) {
              handleSortChange(model);
            }
          }}
          getRowClassName={(params) =>
            clsx(
              `super-app-theme--${params.row.currentState
                .toLowerCase()
                .replace(/ +/g, "")}`,
              tableInfo?.stateClassName?.[
                params.row.currentState.toLowerCase().replace(/ +/g, "")
              ],
              (params.row.assignedTo == null && userDetail?.groups?.indexOf("/" + params.row.assignedGroup) > -1)
              && tableInfo?.noAssignedClassName
            )
          }
          onRowClick={renderReviewRequest}
          loading={isLoading}
        />
      </Grid>
    </>
  );
};

export default Queue;
