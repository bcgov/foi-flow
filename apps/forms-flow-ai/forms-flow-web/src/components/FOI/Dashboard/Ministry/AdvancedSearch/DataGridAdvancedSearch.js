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
import Link from "@mui/material/Link";
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
    advancedSearchParams,
  } = useContext(ActionContext);

  const assignedToList = useSelector(
    (state) => state.foiRequests.foiFullAssignedToList
  );

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(
    Object.keys(advancedSearchParams).length > 0 ? 
      {page: advancedSearchParams.page - 1, pageSize: advancedSearchParams.size} : 
      defaultRowsState
  );

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = React.useState(advancedSearchParams?.sort || defaultSortModel);

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

  const hyperlinkRenderCell = (params) => {
    var link;
    link = "./ministryreview/" + params.row.id + "/ministryrequest/" + params.row.ministryrequestid;
    return (
      <Link href={link} onClick={e => renderReviewRequest(e, params.row)}>
        <div className="MuiDataGrid-cellContent">{params.value}</div>
      </Link>
    )
  }

  const renderReviewRequest = (e, row) => {
    e.preventDefault()
    dispatch(push(`/foi/ministryreview/${row.id}/ministryrequest/${row.ministryrequestid}`));
  };

  const columns = React.useRef([
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        getFullName(params.row.firstName, params.row.lastName),
    },
    {
      field: "requestType",
      headerName: "REQUEST TYPE",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    {
      field: "currentState",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      flex: 1,
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    {
      field: "assignedToFormatted",
      headerName: "ASSIGNED TO",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    {
      field: "DueDateValue",
      headerName: "LDD",
      flex: 1,
      headerAlign: "left",
      valueGetter: getLDD,
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    {
      field: "DaysLeftValue",
      headerName: "DAYS LEFT",
      flex: 0.5,
      headerAlign: "left",
      valueGetter: getDaysLeft,
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'
    },
    { field: "xgov", headerName: "XGOV", flex: 0.5, headerAlign: "left", renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell'},
  ]);

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
            rows={searchResults?.data}
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
            initialState={{
              pagination: rowsState
            }}
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
            onSortModelChange={(model) => setSortModel(model)}
            getRowClassName={(params) =>
              `super-app-theme--${params.row.currentState
                .toLowerCase()
                .replace(/ +/g, "")}`
            }
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
