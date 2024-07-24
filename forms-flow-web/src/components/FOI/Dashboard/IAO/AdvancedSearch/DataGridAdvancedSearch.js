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
  pagecountcellTooltipRender, 
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

import Stack from "@mui/material/Stack";
import {
  ClickableChip,  
} from "../../utils";
import { setAdvancedSearchFilter } from "../../../../../actions/FOI/foiRequestActions";

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

    //historic search
    handleUpdateHistoricSearchFilter,
    searchHistoricalSearchResults,
    searchHistoricalDataLoading,
    queryHistoricalData,
    setHistoricalSearchLoading,
    historicalSearchComponentLoading,
    historicSearchParams,


  } = useContext(ActionContext);

  const user = useSelector((state) => state.user.userDetail);

  const foiadvsearchfilter = useSelector((state) => state.foiRequests.foiadvancedsearchfilter);

  const advancedFilterChange = (filter) => {
    if (filter === foiadvsearchfilter) {
      return;
    }
    
    dispatch(setAdvancedSearchFilter(filter));
  };

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
      renderCell: pagecountcellTooltipRender,
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

  const HistoricalSearchResultsColumns = [    
    {
      field: "applicantname",
      headerName: "APPLICANT NAME",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',     
      width: 180,
    },
    {
      field: "requesttype",
      headerName: "REQUEST TYPE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "axisrequestid",
      headerName: "ID NUMBER",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "oipcno",
      headerName: "OIPC no",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "assignee",
      headerName: "ASSIGNED TO",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
    {
      field: "receiveddate",
      headerName: "RECEIVED DATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',      
      flex: 1,
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

  const defaultHistoricalResultsTableInfo = {
    columns: HistoricalSearchResultsColumns,
    sort: [     
      { field: "receiveddate", sort: "desc" },
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

  const [historicrowsState, sethistoricRowsState] = useState(
    Object.keys(historicSearchParams).length > 0 ? 
      {page: historicSearchParams.page - 1, pageSize: historicSearchParams.size} : 
      defaultRowsState
  );

  const defaultSortModel = [
    { field: "currentState", sort: "desc" },
    // { field: "receivedDateUF", sort: "desc" },
  ];

  const defaultHistoricSearchSortModel = [
    { field: "receivedDate", sort: "desc" },
    // { field: "receivedDateUF", sort: "desc" },
  ];
  const [sortModel, setSortModel] = useState(advancedSearchParams?.sort || defaultSortModel);
  const [sortHistoricsearchSortModel, setHistoricsearchSortModel] = useState(historicSearchParams?.sort || defaultHistoricSearchSortModel);

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

    if(searchHistoricalSearchResults)
    {

      setHistoricalSearchLoading(true);

      handleUpdateHistoricSearchFilter({
        page: historicrowsState.page + 1,
        size: historicrowsState.pageSize,
        sort: updateSortModel(sortHistoricsearchSortModel),
        userId: userDetail.preferred_username,
      });

    }
    
  }, [rowsState,historicrowsState, sortModel,sortHistoricsearchSortModel]);

  const columnsRef = React.useRef(tableInfo?.columns || []);
  const historiccolumnsRef = React.useRef(defaultHistoricalResultsTableInfo?.columns || []);

  if (advancedSearchComponentLoading && queryData) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }

  const test = (model) => {
    if (model.length > 0) {
      setHistoricsearchSortModel(model)
    }
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
        <Grid item xs={3}>
          <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
          <ClickableChip
                  id="advancedsearchresults"
                  key={`foimod`}
                  label={"FOI MOD"}
                  color="primary"
                  size="small"
                  onClick={() => {advancedFilterChange("foimod"); console.log(`Value of advanced search filter on advancedsearchresults is ${foiadvsearchfilter}`)}}
                  clicked={foiadvsearchfilter === "foimod"}
                />
            <ClickableChip
                  id="historicalsearchresults"
                  key={`historicalsearchresults`}
                  label={"Historical AXIS Results"}
                  color="primary"
                  size="small"
                  onClick={() => { advancedFilterChange("historicalsearchresults"); console.log(`Value of advanced search filter on historicalsearchresults is ${foiadvsearchfilter}`)}}
                  clicked={foiadvsearchfilter === "historicalsearchresults"}
                />
          </Stack>
        </Grid>
        <Grid item xs={12} style={{ minHeight: 300 }}>
         {  (foiadvsearchfilter === "foimod") ?
         // FOI MOD Search results
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
                `super-app-theme--${params.row.currentState?.toLowerCase().replace(/ +/g, "")}`,
                tableInfo?.stateClassName?.[
                  params.row.currentState?.toLowerCase().replace(/ +/g, "")
                ]
              )
            }
            loading={searchLoading}
            
          /> : 
          // Historical Search results
          <DataGrid
            autoHeight
            className="foi-data-grid"
            getRowId={(row) => row.axisrequestid}            
            rows={searchHistoricalSearchResults?.results || []}            
            columns={historiccolumnsRef?.current}
            rowHeight={30}
            headerHeight={50}
            rowCount={searchHistoricalSearchResults?.count || 0}
            pageSize={historicrowsState.pageSize}
            // rowsPerPageOptions={[10]}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
            paginationMode="server"
            initialState={{
              pagination: historicrowsState
            }}            
            onPageChange={(newPage) => sethistoricRowsState((prev) => ({ ...prev, page: newPage }))}
            onPageSizeChange={(newpageSize) =>
              sethistoricRowsState((prev) => ({ ...prev, pageSize: newpageSize }))
            }
            components={{
              Footer: ()=> <CustomFooter rowCount={searchHistoricalSearchResults?.count || 0} defaultSortModel={defaultHistoricalResultsTableInfo.sort} footerFor={"advancedsearch"}></CustomFooter>
            }}
            sortingOrder={["desc", "asc"]}
            sortModel={[sortHistoricsearchSortModel[0]]}
            sortingMode={"server"}
            onSortModelChange={test}
            
                        
            loading={searchHistoricalDataLoading}
            
          />
}
        </Grid>
      </Grid>
    </ConditionalComponent>
  );
};

export default DataGridAdvancedSearch;
