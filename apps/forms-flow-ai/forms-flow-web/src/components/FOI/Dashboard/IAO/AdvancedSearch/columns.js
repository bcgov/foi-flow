import {
  getFullName,
  getDaysLeft,
  getReceivedDate,
  onBehalfFullName,
  hyperlinkRenderCell,
  getRecordsDue
} from "../../utils";
import {
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
} from "../../../../../helper/FOI/helper";

const ProcessingTeamColumns = [
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    renderCell: hyperlinkRenderCell,
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
    field: "onBehalf",
    headerName: "ON BEHALF",
    headerAlign: "left",
    renderCell: hyperlinkRenderCell,
    cellClassName: 'foi-advanced-search-result-cell',
    valueGetter: onBehalfFullName,
    sortable: false,
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
    sortable: false,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
    renderCell: hyperlinkRenderCell,
    cellClassName: 'foi-advanced-search-result-cell',
    flex: 0.5,
    sortable: false,
    valueGetter: (params) =>
      params.row.extensions === undefined ? "N/A" : params.row.extensions,
  },
  {
    field: "requestPageCount",
    headerName: "PAGES",
    headerAlign: "left",
    renderCell: hyperlinkRenderCell,
    cellClassName: 'foi-advanced-search-result-cell',
    flex: 0.5,
  },
];

const IntakeTeamColumns = [
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
    renderCell: (params) => <span></span>,
  },
];

const FlexTeamColumns = [
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    renderCell: hyperlinkRenderCell,
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
    sortable: false,
  },
];

const defaultTableInfo = {
  columns: IntakeTeamColumns,
  sort: [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
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
        { field: "receivedDateUF", sort: "desc" },
      ],
    };
  }

  if (isFlexTeam(userGroups)) {
    return {
      columns: FlexTeamColumns,
      sort: [
        { field: "currentState", sort: "desc" },
        { field: "receivedDateUF", sort: "desc" },
      ],
      stateClassName: {
        open: "flex--open",
      },
    };
  }

  return defaultTableInfo;
};

export { getTableInfo };
