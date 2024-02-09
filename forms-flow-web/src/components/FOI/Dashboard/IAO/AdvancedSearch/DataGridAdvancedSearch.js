import React, { useEffect, useContext, useState } from "react";
import { DataGrid } from '@mui/x-data-grid';
import "../../dashboard.scss";
import useStyles from "../../CustomStyle";
import { useSelector, useDispatch } from "react-redux";
import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import {
  updateSortModel,
  getFullName,
  getDaysLeft,
  getReceivedDate,
  // onBehalfFullName,
  getRecordsDue,
  LightTooltip,
  displayQueueFlagIcons,  
} from "../../utils";
import { ActionContext } from "./ActionContext";
import {
  ConditionalComponent,
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
} from "../../../../../helper/FOI/helper";
import clsx from "clsx";
import { push } from "connected-react-router";
import { CustomFooter } from "../../CustomFooter"
import Link from "@mui/material/Link";

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

  const user = useSelector((state) => state.user.userDetail);



  const renderReviewRequest = (e, row) => {
    e.preventDefault()
    if (row.ministryrequestid) {
      dispatch(
        push(
          `/foi/foirequests/${row.id}/ministryrequest/${row.ministryrequestid}`
        )
      );
    } else {
      dispatch(push(`/foi/reviewrequest/${row.id}`));
    }
  };
  
  const hyperlinkTooltipRenderCell = (params) => {
    let link;
    if (params.row.ministryrequestid) { 
      link = "./foirequests/" + params.row.id + "/ministryrequest/" + params.row.ministryrequestid;
    } else {
      link = "./reviewrequest/" + params.row.id;
    }
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
        <Link href={link} target="_blank" onClick={(e) => renderReviewRequest(e, params.row)}>
        <div className="MuiDataGrid-cellContent">{params.value}</div>
      </Link></span>
    </LightTooltip>
    )
  };

  const hyperlinkRenderCell = (params) => {
    let link;
    if (params.row.ministryrequestid) { 
      link = "./foirequests/" + params.row.id + "/ministryrequest/" + params.row.ministryrequestid;
    } else {
      link = "./reviewrequest/" + params.row.id;
    }
    return (
      <Link href={link} onClick={e => renderReviewRequest(e, params.row)}>
        <div className="MuiDataGrid-cellContent">{params.value}</div>
      </Link>
    )
  };

  

  const ProcessingTeamColumns = [
    {
      field: "flags",
      headerName: "FLAGS",
      headerAlign: "left",
      renderCell: displayQueueFlagIcons,
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      renderCell: hyperlinkTooltipRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      width: 160,
    },
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        getFullName(params.row.firstName, params.row.lastName),
      width: 180,
    },
    {
      field: "onBehalfFormatted",
      headerName: "ON BEHALF",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      // valueGetter: onBehalfFullName,
      // sortable: false,
      width: 180,
    },
    {
      field: "requestType",
      headerName: "TYPE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 0.75,
    },
    {
      field: "applicantcategory",
      headerName: "CATEGORY",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "currentState",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "assignedToFormatted",
      headerName: "ASSIGNED TO",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "DaysLeftValue",
      headerName: "DAYS LEFT",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getDaysLeft,
      flex: 0.75,
      // sortable: false,
    },
    {
      field: "extensions",
      headerName: "EXT.",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 0.5,
      // sortable: false,
      valueGetter: (params) =>
        params.row.extensions === undefined ? "N/A" : params.row.extensions,
    },
    {
      field: "requestpagecount",
      headerName: "PAGES",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 0.5,
    },
  ];
  
  const IntakeTeamColumns = [
    {
      field: "flags",
      headerName: "FLAGS",
      headerAlign: "left",
      renderCell: displayQueueFlagIcons,
    },
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        getFullName(params.row.firstName, params.row.lastName),
      width: 180,
    },
    {
      field: "requestType",
      headerName: "REQUEST TYPE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      renderCell: hyperlinkTooltipRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "currentState",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "assignedToFormatted",
      headerName: "ASSIGNED TO",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "receivedDate",
      headerName: "RECEIVED DATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getReceivedDate,
      flex: 1,
    },
    {
      field: "receivedDateUF",
      headerName: "",
      width: 0,
      hide: true,
      renderCell: (_params) => <span></span>,
    },
  ];
  
  const FlexTeamColumns = [
    {
      field: "flags",
      headerName: "FLAGS",
      headerAlign: "left",
      renderCell: displayQueueFlagIcons,
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      renderCell: hyperlinkTooltipRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      width: 160,
    },
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        getFullName(params.row.firstName, params.row.lastName),
      width: 180,
    },
    {
      field: "applicantcategory",
      headerName: "CATEGORY",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "requestType",
      headerName: "TYPE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "currentState",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "assignedToFormatted",
      headerName: "ASSIGNED TO",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "cfrduedate",
      headerName: "CFR DUE",
      flex: 1,
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getRecordsDue,
    },
    {
      field: "DaysLeftValue",
      headerName: "DAYS LEFT",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getDaysLeft,
      flex: 0.75,
      // sortable: false,
    },
  ];
  
  const defaultTableInfo = {
    columns: IntakeTeamColumns,
    sort: [
      { field: "currentState", sort: "desc" },
      // { field: "receivedDateUF", sort: "desc" },
    ],
    stateClassName: {
      open: "flex-open",
    },
  };
  
  const getTableInfo = (userGroups) => {
    if (!userGroups || isIntakeTeam(userGroups)) {
      return defaultTableInfo;
    }
  
    if (isProcessingTeam(userGroups)) {
      return {
        columns: ProcessingTeamColumns,
        sort: [
          { field: "currentState", sort: "desc" },
          // { field: "receivedDateUF", sort: "desc" },
        ],
      };
    }
  
    if (isFlexTeam(userGroups)) {
      return {
        columns: FlexTeamColumns,
        sort: [
          { field: "currentState", sort: "desc" },
          // { field: "receivedDateUF", sort: "desc" },
        ],
        stateClassName: {
          open: "flex--open",
        },
      };
    }
  
    return defaultTableInfo;
  };
  const tableInfo = getTableInfo(user.groups);
  
  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 100 };
  const [rowsState, setRowsState] = useState(
    Object.keys(advancedSearchParams).length > 0 ? 
      {page: advancedSearchParams.page - 1, pageSize: advancedSearchParams.size} : 
      defaultRowsState
  );

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    // { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = useState(advancedSearchParams?.sort || defaultSortModel);

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
        <Grid item xs={12} style={{ minHeight: 300 }}>
          <DataGrid
            autoHeight
            className="foi-data-grid"
            getRowId={(row) => row.idNumber}
            rows={searchResults?.data || []}
            columns={columnsRef?.current}
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
              Footer: ()=> <CustomFooter rowCount={searchResults?.meta?.total || 0} defaultSortModel={tableInfo.sort} footerFor={"advancedsearch"}></CustomFooter>
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

export default DataGridAdvancedSearch;
