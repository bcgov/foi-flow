import React, { useEffect, useState }  from 'react';
import {
  DataGrid,
  gridPageCountSelector,
  gridPageSelector,
  useGridApiContext,
  useGridSelector,
} from '@mui/x-data-grid';
import Pagination from '@mui/material/Pagination';
import "./dashboard.scss";
import useStyles from './CustomStyle';
import { useDispatch, useSelector } from "react-redux";
import {push} from "connected-react-router";
import { fetchFOIMinistryRequestListByPage } from "../../../apiManager/services/FOI/foiRequestServices";
import { formatDate } from "../../../helper/FOI/helper";
import Loading from "../../../containers/Loading";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { debounce } from "./utils";
import Grid from "@material-ui/core/Grid";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import SearchIcon from "@material-ui/icons/Search";

const MinistryDashboard = ({ userDetail }) => {
  const dispatch = useDispatch();

  const requestQueue = useSelector(
    (state) => state.foiRequests.foiMinistryRequestsList
  );
  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(defaultRowsState);

  const defaultSortModel = [
    { field: "currentState", sort: "asc" },
    { field: "cfrduedate", sort: "asc" },
  ];
  const [sortModel, setSortModel] = React.useState(defaultSortModel);
  let serverSortModel;
  const [filterModel, setFilterModel] = React.useState({
    fields: [
      "applicantcategory",
      "requestType",
      "idNumber",
      "axisRequestId",
      "currentState",
      "assignedministrypersonLastName",
      "assignedministrypersonFirstName",
    ],
    keyword: null,
  });
  const [requestFilter, setRequestFilter] = useState("All");

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
      field: "axisRequestId",
      headerName: "ID NUMBER",
      width: 150,
      headerAlign: "left",
    },
    {
      field: "applicantcategory",
      headerName: "APPLICANT TYPE",
      width: 180,
      headerAlign: "left",
    },
    {
      field: "requestType",
      headerName: "REQUEST TYPE",
      width: 150,
      headerAlign: "left",
    },

    {
      field: "currentState",
      headerName: "REQUEST STATE",
      width: 180,
      headerAlign: "left",
    },
    {
      field: "assignedToName",
      headerName: "ASSIGNEE",
      width: 180,
      headerAlign: "left",
    },
    {
      field: "CFRDueDateValue",
      headerName: "RECORDS DUE",
      width: 150,
      headerAlign: "left",
      valueGetter: getRecordsDue,
    },
    {
      field: "DueDateValue",
      headerName: "LDD",
      width: 150,
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

  const requestFilterChange = (e) => {
    setRowsState(defaultRowsState);
    setRequestFilter(e.target.value);
  };

  const setSearch = debounce((e) => {
    var keyword = e.target.value;
    setFilterModel((prev) => ({ ...prev, keyword }));
    setRowsState(defaultRowsState);
  }, 500);

  const updateAssigneeName = (data) => {
    if (data)
      return data.map((row) => ({
        ...row,
        assignedToName: getAssigneeValue(row),
      }));
    else return data;
  };

  const renderReviewRequest = (e) => {
    if (e.row.ministryrequestid) {
      dispatch(
        push(
          `/foi/ministryreview/${e.row.id}/ministryrequest/${e.row.ministryrequestid}`
        )
      );
    }
  };

  return (
    <div className="container foi-container">
      <Grid
        container
        direction="row"
        className="foi-grid-container"
        spacing={1}
      >
        <Grid
          item
          container
          direction="row"
          alignItems="center"
          xs={12}
          className="foi-dashboard-row2"
        >
          <Grid item xs={12}>
            <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
          </Grid>
        </Grid>
        <>
          {!isLoading ? (
            <>
              <Grid item container alignItems="center" xs={12}>
                <Grid item xs={12} lg={6} className="form-group has-search">
                  <SearchIcon className="form-control-search" />
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search . . ."
                    onChange={setSearch}
                  />
                </Grid>

                <Grid item container lg={6} xs={12} justifyContent="flex-end">
                  <RadioGroup
                    name="controlled-radio-buttons-group"
                    value={requestFilter}
                    onChange={requestFilterChange}
                    row
                  >
                    <FormControlLabel
                      className="form-control-label"
                      value="myRequests"
                      control={<Radio className="mui-radio" color="primary" />}
                      label="My Requests"
                    />
                    <FormControlLabel
                      className="form-control-label"
                      value="watchingRequests"
                      control={<Radio className="mui-radio" color="primary" />}
                      label="Watching Requests"
                    />
                    <FormControlLabel
                      className="form-control-label"
                      value="All"
                      control={<Radio className="mui-radio" color="primary" />}
                      label="My Team Requests"
                    />
                  </RadioGroup>
                </Grid>
              </Grid>
              <Grid
                item
                xs={12}
                style={{ height: 450 }}
                className={classes.root}
              >
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
                  page={rowsState.page}
                  onPageChange={(page) =>
                    setRowsState((prev) => ({ ...prev, page }))
                  }
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
          ) : (
            <Grid item xs={12} container alignItems="center">
              <Loading
                costumStyle={{ position: "relative", marginTop: "4em" }}
              />
            </Grid>
          )}
        </>
      </Grid>
    </div>
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

export default MinistryDashboard;