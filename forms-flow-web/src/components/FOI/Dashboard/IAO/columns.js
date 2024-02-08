import {
  getFullName,
  getDaysLeft,
  getReceivedDate,
  // onBehalfFullName,
  displayIcon,
  displayHeaderIcon,
  displayQueueFlagIcons,
  cellTooltipRender
} from "../utils";
import {
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
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
    renderCell: cellTooltipRender
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
  }
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
    renderCell: cellTooltipRender
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
    valueGetter: (params) => formatDate(params.row.cfrduedate, "MM/dd/yyyy"),
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
  }
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
    renderCell: cellTooltipRender
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
    valueGetter: (params) => formatDate(params.row.cfrduedate, "MM/dd/yyyy"),
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
  }
];

const defaultTableInfo = {
  sort: [
    { field: "defaultSorting", sort: "asc" },
    // { field: "duedate", sort: "asc" }
  ],
  noAssignedClassName: "not-assigned"
};

const getTableInfo = (userGroups) => {
  if (!userGroups || isIntakeTeam(userGroups)) {
    defaultTableInfo.columns = IntakeTeamColumns;
    defaultTableInfo.sort = [
      { field: "intakeSorting", sort: "asc" },
      // { field: "duedate", sort: "asc" }
    ];
  }

  if (isProcessingTeam(userGroups)) {
    defaultTableInfo.columns = ProcessingTeamColumns;
  }

  if (isFlexTeam(userGroups)) {
    defaultTableInfo.columns = FlexTeamColumns;
  }

  return defaultTableInfo;
};

export { getTableInfo };
