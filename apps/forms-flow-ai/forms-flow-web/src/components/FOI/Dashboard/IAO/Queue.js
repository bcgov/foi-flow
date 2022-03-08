import React, { useEffect, useState } from "react";
import {
  DataGrid,
  gridPageCountSelector,
  gridPageSelector,
  useGridApiContext,
  useGridSelector,
} from '@mui/x-data-grid';
import Pagination from '@mui/material/Pagination';
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIRequestListByPage } from "../../../../apiManager/services/FOI/foiRequestServices";
import Loading from "../../../../containers/Loading";
import {
  debounce,
  ClickableChip,
  getAssigneeValue,
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

const Queue = ({ userDetail, tableInfo }) => {
  const dispatch = useDispatch();

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiRequestsList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(defaultRowsState);

  const [sortModel, setSortModel] = React.useState(tableInfo.sort);
  let serverSortModel;
  const [filterModel, setFilterModel] = React.useState({
    fields: [
      "firstName",
      "lastName",
      "requestType",
      "idNumber",
      "currentState",
      "assignedToLastName",
      "assignedToFirstName",
    ],
    keyword: null,
  });
  const [requestFilter, setRequestFilter] = useState("All");

  useEffect(() => {
    serverSortModel = updateSortModel(sortModel);
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(
      fetchFOIRequestListByPage(
        rowsState.page + 1,
        rowsState.pageSize,
        serverSortModel,
        filterModel.fields,
        filterModel.keyword,
        requestFilter,
        userDetail.preferred_username
      )
    );
  }, [rowsState, sortModel, filterModel, requestFilter]);

  const columnsRef = React.useRef(tableInfo?.columns || []);

  const requestFilterChange = (filter) => {
    if (filter === requestFilter) {
      return;
    }
    setRowsState(defaultRowsState);
    setRequestFilter(filter);
  };

  const setSearch = debounce((e) => {
    var keyword = e.target.value;
    setFilterModel((prev) => ({ ...prev, keyword }));
    setRowsState(defaultRowsState);
  }, 500);

  const updateAssigneeName = (data) => {
    if (!data) {
      return [];
    }
    return data.map((row) => ({
      ...row,
      assignedToName: getAssigneeValue(row),
    }));
  };

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

    setSortModel(model);
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
            xs={7.5}
            sx={{
              borderRight: "2px solid #38598A",
              backgroundColor: "rgba(56,89,138,0.1)",
            }}
          >
            <InputBase
              placeholder="Search in Queue ..."
              onChange={setSearch}
              sx={{
                color: "#38598A",
              }}
              startAdornment={
                <InputAdornment position="start">
                  <IconButton sx={{ color: "#38598A" }}>
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
            xs={4.5}
          >
            <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
              <ClickableChip
                key={`my-requests`}
                label={"MY REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("myRequests")}
                clicked={requestFilter === "myRequests"}
              />
              <ClickableChip
                key={`team-requests`}
                label={"MY TEAM'S REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("All")}
                clicked={requestFilter === "All"}
              />
              <ClickableChip
                key={`watching-requests`}
                label={"WATCHING REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("watchingRequests")}
                clicked={requestFilter === "watchingRequests"}
              />
            </Stack>
          </Grid>
        </Paper>
      </Grid>
      <Grid item xs={12} style={{ height: 450 }} className={classes.root}>
        <DataGrid
          className="foi-data-grid"
          getRowId={(row) => row.idNumber}
          rows={updateAssigneeName(requestQueue?.data)}
          columns={columnsRef.current}
          rowHeight={30}
          headerHeight={50}
          rowCount={requestQueue?.meta?.total || 0}
          pageSize={rowsState.pageSize}
          rowsPerPageOptions={[10]}
          hideFooterSelectedRowCount={true}
          disableColumnMenu={true}
          pagination
          paginationMode="server"
          page={rowsState.page}
          onPageChange={(page) => setRowsState((prev) => ({ ...prev, page }))}
          onPageSizeChange={(pageSize) =>
            setRowsState((prev) => ({ ...prev, pageSize }))
          }
          components={{
            Pagination: CustomPagination,
          }}
          sortingOrder={["desc", "asc"]}
          sortModel={sortModel}
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
              ]
            )
          }
          onRowClick={renderReviewRequest}
          loading={isLoading}
        />
      </Grid>
    </>
  );
};

const CustomPagination = () => {
  const apiRef = useGridApiContext();
  const page = useGridSelector(apiRef, gridPageSelector);
  const pageCount = useGridSelector(apiRef, gridPageCountSelector);

  return (
    <Pagination
      count={pageCount}
      page={page + 1}
      onChange={(event, value) => apiRef.current.setPage(value - 1)}
    />
  );
}

export default Queue;
