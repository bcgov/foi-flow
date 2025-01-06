import React, { useEffect, useMemo } from "react"
import { DataGrid } from "@mui/x-data-grid";
import "../dashboard.scss";
import useStyles from "../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import { fetchFOIOIRequestListByPage } from "../../../../apiManager/services/FOI/foiRequestServices";
import Loading from "../../../../containers/Loading";
import { debounce, ClickableChip, } from "../utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { setQueueFilter, setQueueParams } from "../../../../actions/FOI/foiRequestActions";
import { CustomFooter } from "../CustomFooter"

const Queue = ({ userDetail, tableInfo }) => {
  const dispatch = useDispatch();

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiMinistryRequestsList
  );

  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();

  const filterFields = [
    "applicantcategory",
    "requestType",
    "idNumber",
    "axisRequestId",
    "currentState",
    "assignedministrypersonLastName",
    "assignedministrypersonFirstName",
  ];

  const queueParams = useSelector((state) => state.foiRequests.queueParams);
  const rowsState = useSelector((state) => state.foiRequests.queueParams?.rowsState);
  const sortModel = useSelector((state) => state.foiRequests.queueParams?.sortModel || tableInfo.sort);

  let serverSortModel;

  const keyword = useSelector((state) => state.foiRequests.queueParams?.keyword);
  const requestFilter = useSelector((state) => state.foiRequests.queueFilter);

  // update sortModel for records due, ldd & assignedTo
  const updateSortModel = () => {
    let smodel = JSON.parse(JSON.stringify(sortModel));
    if (smodel) {
      smodel.map((row) => {
        if (row.field === "CFRDueDateValue") {
          row.field = "cfrduedate";
        }
        if (row.field === "DueDateValue"){
          row.field = "duedate";
        }
      });

      //add cfrduedate asc to default sorting
      if(smodel[0]?.field === "defaultSorting") {
        smodel.push(
          { field: "receivedDate", sort: "asc" },
        );
      }
    }

    return smodel;
  };

  useEffect(() => {
    serverSortModel = updateSortModel();
    // page+1 here, because initial page value is 0 for mui-data-grid
    dispatch(
      fetchFOIOIRequestListByPage(
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

  const columns = React.useRef([
    {
      field: "receivedDate",
      headerName: "RECEIVED DATE",
      flex: 1,
      headerAlign: "left"
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      flex: 1,
      headerAlign: "left"
    },
    {
      field: "requestType",
      headerName: "TYPE",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "recordspagecount",
      headerName: "PAGES",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "publicationStatus",
      headerName: "PUBLICATION STATUS",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "fromClosed",
      headerName: "FROM CLOSED",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "publicationDate",
      headerName: "PUBLICATION DATE",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "assignedTo",
      headerName: "ASSIGNEE",
      flex: 1,
      headerAlign: "left",
    },
    {
      field: "applicantType",
      headerName: "APPLICANT TYPE",
      flex: 1,
      headerAlign: "left",
    }
    // {
    //   field: "ministryAssignedToFormatted",
    //   headerName: "ASSIGNED TO",
    //   flex: 1,
    //   headerAlign: "left",
    // },
    // {
    //   field: "CFRDueDateValue",
    //   headerName: "RECORDS DUE",
    //   flex: 1,
    //   headerAlign: "left",
    //   valueGetter: getRecordsDue,
    // },
    // {
    //   field: "DueDateValue",
    //   headerName: "LDD",
    //   flex: 1,
    //   headerAlign: "left",
    //   valueGetter: getLDD,
    // },
    // {
    //   field: "cfrduedate",
    //   headerName: "",
    //   width: 0,
    //   hide: true,
    //   renderCell: (_params) => <span></span>,
    // }
  ]);

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
          columns={columns.current}
          rowHeight={30}
          headerHeight={50}
          rowCount={requestQueue?.meta?.total || 0}
          pageSize={rowsState?.pageSize}
          // rowsPerPageOptions={[10,20,50,100]}
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
            if (model.length > 0) {
              dispatch(setQueueParams({...queueParams, sortModel: model}));
            }
          }}
          getRowClassName={(params) => (params.row.assignedministryperson == null) && "not-assigned"}
          onRowClick={renderReviewRequest}
          loading={isLoading}
        />
      </Grid>
    </>
  );
};

export default Queue;
