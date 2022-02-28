import {
  getFullName,
  getDaysLeft,
  getReceivedDate,
  onBehalfFullName,
} from "../utils";
import { isProcessingTeam, isIntakeTeam } from "../../../../helper/FOI/helper";

const ProcessingTeamColumns = [
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    headerAlign: "left",
    width: 150,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: (params) =>
      getFullName(params.row.firstName, params.row.lastName),
    width: 170,
  },
  {
    field: "onBehalf",
    headerName: "ON BEHALF",
    headerAlign: "left",
    valueGetter: onBehalfFullName,
    flex: 1,
    sortable: false,
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "applicantcategory",
    headerName: "APPLICANT TYPE",
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
    headerAlign: "center",
    align: "center",
    valueGetter: getDaysLeft,
    flex: 0.5,
    sortable: false,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "center",
    align: "center",
    flex: 0.5,
    sortable: false,
    valueGetter: (params) =>
      params.row.extensions === undefined ? "N/A" : params.row.extensions,
  },
  {
    field: "pages",
    headerName: "PAGES",
    headerAlign: "center",
    align: "center",
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
    flex: 1,
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    width: 180,
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

const defaultTableInfo = {
  columns: IntakeTeamColumns,
  sort: [
    { field: "currentState", sort: "desc" },
    { field: "receivedDateUF", sort: "desc" },
  ],
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

  return defaultTableInfo;
};

export { getTableInfo };
