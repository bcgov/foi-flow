import React, { useEffect, useContext, useState } from "react";
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
import { useSelector } from "react-redux";
import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import {
  updateSortModel,
} from "../../utils";
import { ActionContext } from "./ActionContext";
import { ConditionalComponent } from "../../../../../helper/FOI/helper";
import { getTableInfo } from "./columns";
import clsx from "clsx";

const DataGridAdvancedSearch = ({ userDetail }) => {

  const {
    handleUpdateSearchFilter,
    searchResults,
    searchLoading,
    queryData,
    setSearchLoading,
    advancedSearchComponentLoading,
  } = useContext(ActionContext);

  const user = useSelector((state) => state.user.userDetail);
  const tableInfo = getTableInfo(user.groups);
  
  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = React.useState(defaultRowsState);

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = useState(tableInfo?.sort || defaultSortModel);

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

  const columnsRef = React.useRef(tableInfo?.columns || []);

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
            rows={searchResults?.data || []}
            columns={columnsRef?.current}
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
              clsx(
                `super-app-theme--${params.row.currentState
                  .toLowerCase()
                  .replace(/ +/g, "")}`,
                tableInfo?.stateClassName?.[
                  params.row.currentState.toLowerCase().replace(/ +/g, "")
                ]
              )
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
