import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIRequestListByPage } from "../../../../apiManager/services/FOI/foiRequestServices";
import { fetchFOIFullAssignedToList } from "../../../../apiManager/services/FOI/foiMasterDataServices";
import {
  formatDate,
  addBusinessDays,
  businessDay,
} from "../../../../helper/FOI/helper";
import Loading from "../../../../containers/Loading";
import { debounce, ClickableChip } from "../utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";

const Queue = ({ userDetail }) => {
  const dispatch = useDispatch();

  const assignedToList = useSelector(
    (state) => state.foiRequests.foiFullAssignedToList
  );
  const isAssignedToListLoading = useSelector(
    (state) => state.foiRequests.isAssignedToListLoading
  );

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiRequestsList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();
  useEffect(() => {
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOIRequestListByPage());
  }, [dispatch]);

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(defaultRowsState);

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = React.useState(defaultSortModel);
  let serverSortModel;
  const [filterModel, setFilterModel] = React.useState({
    fields: [
      "firstName",
      "lastName",
      "requestType",
      "idNumber",
      "currentState",
      "assignedTo",
    ],
    keyword: null,
  });
  const [requestFilter, setRequestFilter] = useState("All");

  useEffect(() => {
    serverSortModel = updateSortModel();
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

  function getFullName(params) {
    return `${params.row.lastName || ""}, ${params.row.firstName || ""}`;
  }

  // update sortModel for applicantName & assignedTo
  const updateSortModel = () => {
    let smodel = JSON.parse(JSON.stringify(sortModel));
    if (smodel) {
      smodel.map((row) => {
        if (row.field === "assignedToName") row.field = "assignedTo";
      });

      let field = smodel[0]?.field;
      let order = smodel[0]?.sort;
      if (field == "applicantName") {
        smodel.shift();
        smodel.unshift(
          { field: "lastName", sort: order },
          { field: "firstName", sort: order }
        );
      }
    }

    return smodel;
  };

  function getAssigneeValue(row) {
    const groupName = row.assignedGroup ? row.assignedGroup : "Unassigned";
    const assignedTo = row.assignedTo ? row.assignedTo : groupName;
    if (assignedToList && assignedToList.length > 0) {
      const assigneeDetails = assignedToList.find(
        (assigneeGroup) => assigneeGroup.name === groupName
      );
      const assignee =
        assigneeDetails &&
        assigneeDetails.members &&
        assigneeDetails.members.find(
          (_assignee) => _assignee.username === assignedTo
        );
      if (groupName === assignedTo) {
        return assignedTo;
      } else {
        return assignee !== undefined
          ? `${assignee.lastname}, ${assignee.firstname}`
          : "invalid user";
      }
    } else {
      return assignedTo;
    }
  }

  function getReceivedDate(params) {
    let receivedDateString = params.row.receivedDateUF;
    const dateString = receivedDateString
      ? receivedDateString.substring(0, 10)
      : "";
    receivedDateString = receivedDateString ? new Date(receivedDateString) : "";

    if (
      receivedDateString !== "" &&
      (receivedDateString.getHours() > 16 ||
        (receivedDateString.getHours() === 16 &&
          receivedDateString.getMinutes() > 30) ||
        !businessDay(dateString))
    ) {
      receivedDateString = addBusinessDays(receivedDateString, 1);
    }
    return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
  }

  const columns = React.useRef([
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      width: 170,
      headerAlign: "left",
      valueGetter: getFullName,
    },
    {
      field: "requestType",
      headerName: "REQUEST TYPE",
      width: 150,
      headerAlign: "left",
    },
    {
      field: "idNumber",
      headerName: "ID NUMBER",
      width: 150,
      headerAlign: "left",
    },
    {
      field: "currentState",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      width: 180,
    },
    {
      field: "assignedToName",
      headerName: "ASSIGNED TO",
      width: 180,
      headerAlign: "left",
    },
    {
      field: "receivedDate",
      headerName: "RECEIVED DATE",
      width: 180,
      headerAlign: "left",
      valueGetter: getReceivedDate,
    },
    { field: "xgov", headerName: "XGOV", width: 100, headerAlign: "left" },
    {
      field: "receivedDateUF",
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
      return data;
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

  if (isLoading || isAssignedToListLoading) {
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
        >
          <Grid
            item
            container
            alignItems="center"
            direction="row"
            xs={7}
            sx={{
              borderRight: "2px solid #38598A",
              backgroundColor: "rgba(56,89,138,0.1)",
            }}
            fullWidth
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
            justifyContent="space-around"
            xs={5}
          >
            <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={2}>
              <ClickableChip
                key={`filter-request-description`}
                label={"MY REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("myRequests")}
                clicked={requestFilter === "myRequests"}
              />
              <ClickableChip
                key={`filter-request-description`}
                label={"MY TEAM'S REQUESTS"}
                color="primary"
                size="small"
                onClick={() => requestFilterChange("All")}
                clicked={requestFilter === "All"}
              />
              <ClickableChip
                key={`filter-request-description`}
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
          rows={updateAssigneeName(requestQueue.data)}
          columns={columns.current}
          rowHeight={30}
          headerHeight={50}
          rowCount={requestQueue?.meta?.total}
          pageSize={rowsState.pageSize}
          rowsPerPageOptions={[10]}
          hideFooterSelectedRowCount={true}
          disableColumnMenu={true}
          pagination
          paginationMode="server"
          onPageChange={(page) => setRowsState((prev) => ({ ...prev, page }))}
          onPageSizeChange={(pageSize) =>
            setRowsState((prev) => ({ ...prev, pageSize }))
          }
          sortingOrder={["desc", "asc"]}
          sortModel={sortModel}
          sortingMode={"server"}
          onSortModelChange={(model) => setSortModel(model)}
          getRowClassName={(params) =>
            `super-app-theme--${params.row.currentState
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

export default Queue;
