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
  LightTooltip,
  pagecountcellTooltipRender, 
  getClosedDate,
  formatRequestType
} from "../../utils";
import { ActionContext } from "./ActionContext";
import {
  ConditionalComponent
} from "../../../../../helper/FOI/helper";
import clsx from "clsx";
import { push } from "connected-react-router";
import { CustomFooter } from "../../CustomFooter"
import Link from "@mui/material/Link";
import { DOC_REVIEWER_WEB_URL } from "../../../../../constants/constants";

const DataGridKeywordSearch = ({ userDetail }) => {
  const dispatch = useDispatch();

  const {
    handleUpdateSearchFilter,
    searchResults,
    searchLoading,
    queryData,
    setKeywordSearchLoading,
    keywordSearchComponentLoading,
    foiKeywordSearchParams,
  } = useContext(ActionContext);

  console.log("foiKeywordSearchParams-Grid:",foiKeywordSearchParams)
  const keywordSearchParamsRef = React.useRef(foiKeywordSearchParams);
  console.log("keywordSearchParamsRef-Grid:",keywordSearchParamsRef)


  useEffect(() => {
    keywordSearchParamsRef.current = foiKeywordSearchParams;
  }, [foiKeywordSearchParams]);

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

  const goToRecordsRenderCell = (params) => {
    const keywordSearchParam = keywordSearchParamsRef.current;
    let link;
    if (params.row.ministryrequestid && keywordSearchParam?.keywords?.length > 0) {
      const keywords = keywordSearchParam.keywords
      .filter(keyword => keyword.category.toUpperCase() !== "NOT")
      .map(keyword => keyword.text)
      .join(",");
      //console.log("keywordList:", keywordList);
      let queryString= {"query": keywords };
      const queryStringParam = new URLSearchParams(queryString).toString();
      const formattedQueryString = queryStringParam.replace(/\+/g, '%20');
      link = `${DOC_REVIEWER_WEB_URL}/foi/${params.row.ministryrequestid}?${formattedQueryString}`;
    }
    return (
      <Link
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <div className="MuiDataGrid-cellContent">Go to records</div>
      </Link>
    );
  };


  const IAOColumns = [
    {
      field: "applicantName",
      headerName: "APPLICANT NAME",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        getFullName(params.row.firstname, params.row.lastname),
      width: 180,
    },
    {
      field: "requestType",
      headerName: "TYPE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) => params.row.requestType,
      flex: 0.75,
    },
    {
      field: "requestnumber",
      headerName: "ID NUMBER",
      headerAlign: "left",
      renderCell: hyperlinkTooltipRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) => params.row.requestnumber,
      width: 160,
    },  
    {
      field: "requeststatus",
      headerName: "CURRENT STATE",
      headerAlign: "left",
      renderCell: hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: (params) =>
        formatRequestType(params.row.requeststatus),
      flex: 1,
    },
    {
      field: "requestpagecount",
      headerName: "PAGES",
      headerAlign: "left",
      renderCell: pagecountcellTooltipRender,
      cellClassName: 'foi-advanced-search-result-cell',
      flex: 0.5,
    },
    {
      field: "closedDate",
      headerName: "CLOSED DATE",
      headerAlign: "left",
      renderCell:hyperlinkRenderCell,
      cellClassName: 'foi-advanced-search-result-cell',
      valueGetter: getClosedDate, //(params) => params.row.closedate,
      flex: 1,
    },
    {
      field: "goToRecords",
      headerName: "",
      renderCell: (params) => goToRecordsRenderCell( params),
      //cellClassName: 'foi-advanced-search-result-cell',
      flex: 1,
    },
  ];
    
  const defaultTableInfo = {
    columns: IAOColumns,
    sort: [
      { field: "requeststatus", sort: "desc" },
      // { field: "receivedDateUF", sort: "desc" },
    ],
    stateClassName: {
      open: "flex-open",
    },
  };

  const tableInfo = defaultTableInfo;
  
  const classes = useStyles();

  const defaultRowsState = { page: 0, pageSize: 10 };
  const [rowsState, setRowsState] = useState(defaultRowsState);
  const defaultSortModel = [
    { field: "requeststatus", sort: "desc" },
  ];
  const [sortModel, setSortModel] = useState(defaultSortModel);

  useEffect(() => {
    if (searchResults) {
      setKeywordSearchLoading(true);
      
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

  // Function to get paginated data
  const getPaginatedRows = (sortedRows) => {
    const startIndex = rowsState.page * rowsState.pageSize;
    const endIndex = startIndex + rowsState.pageSize;
    return sortedRows.slice(startIndex, endIndex); // Correctly slice rows for pagination
  };
  // Function to sort data locally
  const getSortedRows = () => {
    if (!Array.isArray(searchResults) || searchResults.length === 0) return [];
    if (sortModel.length === 0) return searchResults;
    const { field, sort } = sortModel[0];
    return [...searchResults].sort((a, b) => {
      if (a[field] < b[field]) return sort === "asc" ? -1 : 1;
      if (a[field] > b[field]) return sort === "asc" ? 1 : -1;
      return 0;
    });
  };

  // Compute rows to display (sorted and paginated)
  const rows = React.useMemo(() => {
    const sortedRows = getSortedRows();
    let currentPageRows= getPaginatedRows(sortedRows); // Get rows for the current page
    console.log("currentPageRows:",currentPageRows)
    return currentPageRows
  }, [searchResults, rowsState, sortModel]);


  if (keywordSearchComponentLoading && queryData) {
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
            getRowId={(row) => row.requestnumber}
            //rows={searchResults || []}
            rows={rows} // Display only the current page's rows
            columns={columnsRef?.current}
            rowHeight={30}
            headerHeight={50}
            rowCount={searchResults?.length || 0}
            pageSize={rowsState.pageSize}
            // rowsPerPageOptions={[10]}
            hideFooterSelectedRowCount={true}
            disableColumnMenu={true}
            pagination
            initialState={{
              pagination: rowsState
            }}
            paginationMode="server"
            onPageChange={(newPage) => setRowsState((prev) => ({ ...prev, page: newPage }))}
            onPageSizeChange={(newpageSize) =>
              setRowsState((prev) => ({ ...prev, pageSize: newpageSize }))
            }
            components={{
              Footer: ()=> <CustomFooter rowCount={searchResults?.length || 0} defaultSortModel={defaultSortModel} footerFor={"advancedsearch"}></CustomFooter>
            }}
            sortingOrder={["desc", "asc"]}
            sortModel={[sortModel[0]]}
            onSortModelChange={(model) => {
              if (model.length > 0) {
                setSortModel(model)
              }
            }}
            getRowClassName={(params) =>
              clsx(
                `super-app-theme--${params.row.requeststatus?.toLowerCase().replace(/ +/g, "")}`,
                tableInfo?.stateClassName?.[
                  params.row.requeststatus?.toLowerCase().replace(/ +/g, "")
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

export default DataGridKeywordSearch;
