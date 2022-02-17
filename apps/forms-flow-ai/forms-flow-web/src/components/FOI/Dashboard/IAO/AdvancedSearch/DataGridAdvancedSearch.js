import React, { useEffect, useContext } from "react";
import {
  DataGrid,
  gridPageCountSelector,
  gridPageSelector,
  useGridApiContext,
  useGridSelector,
} from '@mui/x-data-grid';
import Pagination from '@mui/material/Pagination';
import "../../dashboard.scss";
import useStyles from "../../CustomStyle";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import {
  getAssigneeValue,
  updateSortModel,
  getFullName,
  getLDD,
  getDaysLeft,
} from "../../utils";
import { ActionContext } from "./ActionContext";
import { ConditionalComponent } from "../../../../../helper/FOI/helper";

const DataGridAdvancedSearch = ({ userDetail }) => {
  const dispatch = useDispatch();

  const {
    handleUpdateSearchFilter,
    searchResults,
    searchLoading,
    queryData,
    setSearchLoading,
    advancedSearchComponentLoading,
  } = useContext(ActionContext);

  const assignedToList = useSelector(
    (state) => state.foiRequests.foiFullAssignedToList
  );

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(defaultRowsState);

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = React.useState(defaultSortModel);

  useEffect(() => {
    if (searchResults) {
      setSearchLoading(true);
      // page+1 here, because initial page value is 0 for mui-data-grid
      handleUpdateSearchFilter({
        page: rowsState.page + 1,
        size: rowsState.pageSize,
        sort: updateSortModel(sortModel),
        userId: userDetail.preferred_username,
      });
    }
  }, [rowsState, sortModel]);

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
      field: "DueDateValue",
      headerName: "LDD",
      width: 100,
      headerAlign: "left",
      valueGetter: getLDD,
    },
    {
      field: "DaysLeftValue",
      headerName: "DAYS LEFT",
      width: 100,
      headerAlign: "left",
      valueGetter: getDaysLeft,
    },
    { field: "xgov", headerName: "XGOV", width: 100, headerAlign: "left" },
  ]);

  const updateAssigneeName = (data) => {
    if (!data) {
      return [];
    }
    return data.map((row) => ({
      ...row,
      assignedToName: getAssigneeValue(row, assignedToList),
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

  if (advancedSearchComponentLoading && queryData) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }

  return (
    <ConditionalComponent condition={!!queryData}>
      <Grid
        item
        xs={12}
        className={classes.root}
        container
        direction="row"
        spacing={1}
      >
        <Grid item xs={12}>
          <h4 className="foi-request-queue-text">Search Results</h4>
        </Grid>
        <Grid item xs={12} style={{ height: 450 }}>
          <DataGrid
            className="foi-data-grid"
            getRowId={(row) => row.idNumber}
            rows={updateAssigneeName(searchResults?.data)}
            columns={columns.current}
            rowHeight={30}
            headerHeight={50}
            rowCount={searchResults?.meta?.total || 0}
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
            components={{
              Pagination: CustomPagination,
            }}
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
            loading={searchLoading}
          />
        </Grid>
      </Grid>
    </ConditionalComponent>
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

export default DataGridAdvancedSearch;
