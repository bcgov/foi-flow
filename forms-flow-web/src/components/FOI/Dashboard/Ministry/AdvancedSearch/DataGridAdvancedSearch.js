import React, { useEffect, useContext } from "react";
import { DataGrid } from '@mui/x-data-grid';
import "../../dashboard.scss";
import useStyles from "../../CustomStyle";
import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import {
  updateSortModel,
  getLDD,
  getRecordsDue,
  LightTooltip
} from "../../utils";
import { ActionContext } from "./ActionContext";
import { ConditionalComponent } from "../../../../../helper/FOI/helper";
import { useDispatch } from "react-redux";
import Link from "@mui/material/Link";
import { push } from "connected-react-router";
import { CustomFooter } from "../../CustomFooter"

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

  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 100 };
  const [rowsState, setRowsState] = React.useState(
    Object.keys(advancedSearchParams).length > 0 ? 
      {page: advancedSearchParams.page - 1, pageSize: advancedSearchParams.size} : 
      defaultRowsState
  );

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    // { field: "receivedDateUF", sort: "desc" },
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

  const hyperlinkTooltipRenderCellforMinistry = (params) => {    
    let link;
    link = "./ministryreview/" + params.row.id + "/ministryrequest/" + params.row.ministryrequestid;
    let description = params.row.description;
    if (params.row.fromdate && params.row.todate) {
      description += "\n(" + (new Date(params.row.fromdate)).toLocaleDateString() + " to " + (new Date(params.row.todate)).toLocaleDateString() + ")"
    }
    return (<LightTooltip placement="bottom-start" title={
      <div style={{whiteSpace: "pre-line"}}>
        {description}
      </div>
    }>
      <span className="table-cell-truncate">
      <Link href={link} onClick={(e) => renderReviewRequestforMinistry(e, params.row)}>
        <div className="MuiDataGrid-cellContent">{params.value}</div>
      </Link></span>
    </LightTooltip>
    )
  };

  const hyperlinkRenderCellforMinistry = (params) => {
    let link;
    link = "./ministryreview/" + params.row.id + "/ministryrequest/" + params.row.ministryrequestid;
    return (
      <Link href={link} onClick={e => renderReviewRequestforMinistry(e, params.row)}>
        <div className="MuiDataGrid-cellContent">{params.value}</div>
      </Link>
    )
  };

  const renderReviewRequestforMinistry = (e, row) => {
    e.preventDefault()
    dispatch(push(`/foi/ministryreview/${row.id}/ministryrequest/${row.ministryrequestid}`));
  };

  const columns = React.useRef([
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      width: 170,
      headerAlign: "left",
      renderCell: hyperlinkTooltipRenderCellforMinistry,
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
      renderCell: (_params) => <span></span>,
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
        <Grid item xs={12} style={{ minHeight: 300 }}>
          <DataGrid
            autoHeight
            className="foi-data-grid"
            getRowId={(row) => row.idNumber}
            rows={searchResults?.data || []}
            columns={columns.current}
            rowHeight={30}
            headerHeight={50}
            rowCount={searchResults?.meta?.total || 0}
            pageSize={rowsState.pageSize}
            // rowsPerPageOptions={[10]}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
            paginationMode="server"
            initialState={{
              pagination: rowsState
            }}
            onPageChange={(newPage) => setRowsState((prev) => ({ ...prev, page: newPage }))}
            onPageSizeChange={(newpageSize) =>
              setRowsState((prev) => ({ ...prev, pageSize: newpageSize }))
            }
            components={{
              Footer: ()=> <CustomFooter rowCount={searchResults?.meta?.total || 0} defaultSortModel={defaultSortModel} footerFor={"advancedsearch"}></CustomFooter>
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

export default DataGridAdvancedSearch;
