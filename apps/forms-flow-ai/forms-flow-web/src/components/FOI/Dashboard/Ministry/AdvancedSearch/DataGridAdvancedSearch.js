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
import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import {
  updateSortModel,
  getLDD,
  getRecordsDue,
  hyperlinkRenderCellforMinistry
} from "../../utils";
import { ActionContext } from "./ActionContext";
import { ConditionalComponent } from "../../../../../helper/FOI/helper";

const DataGridAdvancedSearch = ({ userDetail }) => {

  const {
    handleUpdateSearchFilter,
    searchResults,
    searchLoading,
    queryData,
    setSearchLoading,
    advancedSearchComponentLoading,
  } = useContext(ActionContext);

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
      field: "axisRequestId",
      headerName: "ID NUMBER",
      width: 170,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
    },
    {
      field: "applicantcategory",
      headerName: "CATEGORY",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
    },
    {
      field: "requestType",
      headerName: "TYPE",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
    },

    {
      field: "currentState",
      headerName: "REQUEST STATE",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
    },

    {
      field: "ministryAssignedToFormatted",
      headerName: "ASSIGNED TO",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
    },
    {
      field: "CFRDueDateValue",
      headerName: "RECORDS DUE",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getRecordsDue,
    },
    {
      field: "DueDateValue",
      headerName: "LDD",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCellforMinistry,
      cellClassName: 'foi-advanced-search-result-cell',
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
