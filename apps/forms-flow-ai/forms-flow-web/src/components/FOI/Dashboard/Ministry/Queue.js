import React, { useEffect, useState, useMemo } from "react";
import {
  DataGrid,
  gridPageCountSelector,
  gridPageSelector,
  useGridApiContext,
  useGridSelector,
} from "@mui/x-data-grid";
import Pagination from "@mui/material/Pagination";
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIMinistryRequestListByPage } from "../../../../apiManager/services/FOI/foiRequestServices";
import Loading from "../../../../containers/Loading";
import { debounce, ClickableChip } from "../utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { formatDate } from "../../../../helper/FOI/helper";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

const Queue = ({ userDetail, tableInfo }) => {
  const dispatch = useDispatch();

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiMinistryRequestsList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = useState(defaultRowsState);

  const defaultSortModel = [
    { field: "currentState", sort: "asc" },
    { field: "cfrduedate", sort: "asc" },
  ];
  const [sortModel, setSortModel] = useState(defaultSortModel);

  let serverSortModel;
  const [filterModel, setFilterModel] = useState({
    fields: [
      "applicantcategory",
      "requestType",
      "idNumber",
      "currentState",
      "assignedministrypersonLastName",
      "assignedministrypersonFirstName",
    ],
    keyword: null,
  });
  const [requestFilter, setRequestFilter] = useState("All");

  // update sortModel for records due, ldd & assignedTo
  const updateSortModel = () => {
    let smodel = JSON.parse(JSON.stringify(sortModel));
    if (smodel) {
      smodel.map((row) => {
        if (row.field === "CFRDueDateValue" || row.field === "DueDateValue")
          row.field = "cfrduedate";
      });

      let field = smodel[0]?.field;
      let order = smodel[0]?.sort;
      if (field == "assignedToName") {
        smodel.shift();
        smodel.unshift(
          { field: "assignedministrypersonLastName", sort: order },
          { field: "assignedministrypersonFirstName", sort: order }
        );
      }
    }

    return smodel;
  };

  useEffect(() => {
    serverSortModel = updateSortModel();
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(
      fetchFOIMinistryRequestListByPage(
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

  function getAssigneeValue(row) {
    const groupName = row.assignedministrygroup
      ? row.assignedministrygroup
      : "Unassigned";
    return row.assignedministryperson &&
      row.assignedministrypersonFirstName &&
      row.assignedministrypersonLastName
      ? `${row.assignedministrypersonLastName}, ${row.assignedministrypersonFirstName}`
      : groupName;
  }

  function getRecordsDue(params) {
    let receivedDateString = params.row.cfrduedate;
    const currentStatus = params.row.currentState;
    if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
      return "N/A";
    } else {
      return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
    }
  }

  function getLDD(params) {
    let receivedDateString = params.row.duedate;
    const currentStatus = params.row.currentState;
    if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
      return "N/A";
    } else {
      return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
    }
  }

  const columns = React.useRef([
    {
      field: "idNumber",
      headerName: "ID NUMBER",
      width: 170,
      headerAlign: "left",
    },
    {
      field: "applicantcategory",
      headerName: "CATEGORY",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "requestType",
      headerName: "TYPE",
      flex: 1,
      headerAlign: "left",
    },

    {
      field: "currentState",
      headerName: "REQUEST STATE",
      flex: 1,
      headerAlign: "left",
    },

    {
      field: "assignedToName",
      headerName: "ASSIGNED TO",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "CFRDueDateValue",
      headerName: "RECORDS DUE",
      flex: 1,
      headerAlign: "left",
      valueGetter: getRecordsDue,
    },
    {
      field: "DueDateValue",
      headerName: "LDD",
      flex: 1,
      headerAlign: "left",
      valueGetter: getLDD,
    },
    {
      field: "cfrduedate",
      headerName: "",
      width: 0,
      hide: true,
      renderCell: (params) => <span></span>,
    },
  ]);

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

  const rows = useMemo(() => {
    return updateAssigneeName(requestQueue?.data);
  }, [JSON.stringify(requestQueue)]);

  const renderReviewRequest = (e) => {
    if (e.row.ministryrequestid) {
      dispatch(
        push(
          `/foi/ministryreview/${e.row.id}/ministryrequest/${e.row.ministryrequestid}`
        )
      );
    }
  };

  if (requestQueue === null) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }

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
            <InputBase
              id="filter"
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
            xs={3}
            minWidth="390px"
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
          rows={rows}
          columns={columns.current}
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
          sortModel={[sortModel[0]]}
          sortingMode={"server"}
          onSortModelChange={(model) => {
            if (model) {
              setSortModel(model);
            }
          }}
          getRowClassName={(params) =>
            `super-app-theme--${params.row.currentState
              .toLowerCase()
              .replace(/ +/g, "")}-${params.row.cfrstatus
              .toLowerCase()
              .replace(/ +/g, "")}`
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
};

export default Queue;
