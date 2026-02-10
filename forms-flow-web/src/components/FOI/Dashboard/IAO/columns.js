import {
  getFullName,
  getDaysLeft,
  getReceivedDate,
  // onBehalfFullName,
  displayIcon,
  displayHeaderIcon,
  displayQueueFlagIcons,
  cellTooltipRender,
  pagecountcellTooltipRender,
  calculateFromClosed,
} from "../utils";
import {
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
  isOITeam,
  formatDate,
} from "../../../../helper/FOI/helper";

const ProcessingTeamColumns = [
  {
    field: "flags",
    // renderHeader: displayHeaderIcon,
    headerName: "FLAGS",
    headerAlign: "left",
    renderCell: displayQueueFlagIcons,
    // cellClassName: 'foi-dashboard-',
    // flex: 1,
  },
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    width: 160,
    renderCell: cellTooltipRender,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? "N/A"
        : getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "onBehalfFormatted",
    headerName: "ON BEHALF",
    headerAlign: "left",
    // valueGetter: onBehalfFullName,
    // sortable: false,
    width: 180,
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
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? params.row.proactivedisclosurecategory
        : params.row.applicantcategory,
    flex: 1,
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "assignedToFormatted",
    headerName: "ASSIGNED TO",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 0.75,
    // sortable: false,
  },
  {
    field: "cfrduedate",
    headerName: "CFR DUE",
    flex: 1,
    headerAlign: "left",
    valueGetter: (params) =>
      formatDate(params.row.cfrduedate, "MMM dd yyyy").toUpperCase(),
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
    flex: 0.5,
    // sortable: false,
    valueGetter: (params) =>
      params.row.extensions === undefined ? "N/A" : params.row.extensions,
  },
  {
    field: "requestpagecount",
    headerName: "PAGES",
    headerAlign: "left",
    flex: 0.5,
    valueGetter: (params) => parseInt(params.row.requestpagecount),
    renderCell: pagecountcellTooltipRender,
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
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    width: 160,
    renderCell: cellTooltipRender,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? "N/A" :
        getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "onBehalfFormatted",
    headerName: "ON BEHALF",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.onBehalfFormatted === undefined ||
        params.row.onBehalfFormatted === null
        ? "N/A"
        : params.row.onBehalfFormatted,
    width: 120,
  },
  {
    field: "applicantcategory",
    headerName: "CATEGORY",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? params.row.proactivedisclosurecategory
        : params.row.applicantcategory,
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
    field: "assignedToFormatted",
    headerName: "ASSIGNEE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "cfrduedate",
    headerName: "CFR DUE",
    flex: 1,
    headerAlign: "left",
    valueGetter: (params) =>
      formatDate(params.row.cfrduedate, "MMM dd yyyy").toUpperCase(),
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 0.75,
    // sortable: false,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
    flex: 0.5,
    valueGetter: (params) =>
      params.row.extensions === undefined ? 0 : params.row.extensions,
  },
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    headerAlign: "left",
    valueGetter: getReceivedDate,
    flex: 1,
  },
  {
    field: "requestpagecount",
    headerName: "PAGES",
    headerAlign: "left",
    flex: 0.5,
    valueGetter: (params) => parseInt(params.row.requestpagecount),
    renderCell: pagecountcellTooltipRender,
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
    width: 160,
    renderCell: cellTooltipRender,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? "N/A" :
        getFullName(params.row.firstName, params.row.lastName),
    width: 180,
  },
  {
    field: "applicantcategory",
    headerName: "CATEGORY",
    headerAlign: "left",
    valueGetter: (params) =>
      params.row.requestType == "proactive disclosure"
        ? params.row.proactivedisclosurecategory
        : params.row.applicantcategory,
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
    field: "assignedToFormatted",
    headerName: "ASSIGNED TO",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "cfrduedate",
    headerName: "CFR DUE",
    flex: 1,
    headerAlign: "left",
    valueGetter: (params) =>
      formatDate(params.row.cfrduedate, "MMM dd yyyy").toUpperCase(),
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 0.75,
    // sortable: false,
  },
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    headerAlign: "left",
    valueGetter: getReceivedDate,
    flex: 1,
  },
];

const OITeamColumns = [
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    flex: 1,
    headerAlign: "left",
    valueGetter: (params) => params.row.requestType == "PD" ?
      params.row.idNumber : params.row.axisRequestId
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "requestType",
    headerName: "TYPE",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "recordspagecount",
    headerName: "PAGES",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "publicationStatus",
    headerName: "PUBLICATION STATUS",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "closedDate",
    headerName: "FROM CLOSED",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "cfrduedate",
    headerName: "CFR DUE DATE",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "publicationDate",
    headerName: "PUBLICATION DATE",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "assignedTo",
    headerName: "ASSIGNEE",
    flex: 1,
    headerAlign: "left",
  },
  {
    field: "proactivedisclosurecategory",
    headerName: "CATEGORY",
    flex: 1,
    headerAlign: "left",
  },
];

const defaultTableInfo = {
  sort: [{ field: "defaultSorting", sort: "asc" }],
  noAssignedClassName: "not-assigned",
};

const getTableInfo = (userGroups) => {
  if (!userGroups || isIntakeTeam(userGroups)) {
    defaultTableInfo.columns = IntakeTeamColumns;
    defaultTableInfo.sort = [{ field: "intakeSorting", sort: "asc" }];
  }

  if (isProcessingTeam(userGroups)) {
    defaultTableInfo.columns = ProcessingTeamColumns;
  }

  if (isFlexTeam(userGroups)) {
    defaultTableInfo.columns = FlexTeamColumns;
  }

  if (isOITeam(userGroups)) {
    defaultTableInfo.columns = OITeamColumns;
  }

  return defaultTableInfo;
};

export { getTableInfo };
