import {
  getFullName,
  getDaysLeft,
  getReceivedDate,
  onBehalfFullName,
} from "../utils";
import {
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
  formatDate,
} from "../../../../helper/FOI/helper";

const ProcessingTeamColumns = [
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    width: 160,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "onBehalf",
    headerName: "ON BEHALF",
    headerAlign: "left",
    valueGetter: onBehalfFullName,
    sortable: false,
  },
  {
    field: "requestType",
    headerName: "TYPE",
    headerAlign: "left",
    flex: 0.75,
  },
  {
    field: "applicantcategory",
    headerName: "CATEGORY",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 0.75,
    sortable: false,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
    flex: 0.5,
    sortable: false,
    valueGetter: (params) =>
      params.row.extensions === undefined ? "N/A" : params.row.extensions,
  },
  {
    field: "pages",
    headerName: "PAGES",
    headerAlign: "left",
    flex: 0.5,
    sortable: false,
    renderCell: (params) => <span></span>,
  },
  {
    field: "xgov",
    headerName: "XGOV",
    headerAlign: "left",
    flex: 0.5,
  },
];

const IntakeTeamColumns = [
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "assignedToName",
    headerName: "ASSIGNED TO",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    headerAlign: "left",
    valueGetter: getReceivedDate,
    flex: 1,
  },
  {
    field: "xgov",
    headerName: "XGOV",
    headerAlign: "left",
    flex: 0.5,
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
    width: 160,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "applicantcategory",
    headerName: "CATEGORY",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "requestType",
    headerName: "TYPE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "assignedToName",
    headerName: "ANALYST",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "cfrduedate",
    headerName: "CFR DUE",
    flex: 1,
    headerAlign: "left",
    valueGetter: (params) => formatDate(params.row.cfrduedate, "MM/dd/yyyy"),
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 0.75,
    sortable: false,
  },
  {
    field: "xgov",
    headerName: "XGOV",
    headerAlign: "left",
    flex: 0.5,
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
      sort: [{ field: "duedate", sort: "asc" }],
    };
  }

  if (isFlexTeam(userGroups)) {
    return {
      columns: FlexTeamColumns,
      sort: [{ field: "stateForSorting", sort: "asc" }],
      stateClassName: {
        open: "flex--open",
      },
    };
  }

  return defaultTableInfo;
};

export { getTableInfo };
