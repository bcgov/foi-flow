import { getFullName, getDaysLeft, getReceivedDate } from "../utils";
import {
  isProcessingTeam,
  isIntakeTeam,
  isFlexTeam,
} from "../../../../helper/FOI/helper";

const ProcessingTeamColumns = [
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: getFullName,
    flex: 1,
  },
  {
    field: "onBehalf",
    headerName: "ON BEHALF",
    headerAlign: "left",
    flex: 1,
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
    headerAlign: "left",
    valueGetter: getDaysLeft,
    flex: 1,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "pages",
    headerName: "PAGES",
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "xgov",
    headerName: "XGOV",
    headerAlign: "left",
    flex: 1,
  },
];

const IntakeTeamColumns = [
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    width: 170,
    headerAlign: "left",
    valueGetter: getFullName,
    flex: 1,
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    width: 150,
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    width: 150,
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
    width: 180,
    headerAlign: "left",
    flex: 1,
  },
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    width: 180,
    headerAlign: "left",
    valueGetter: getReceivedDate,
    flex: 1,
  },
  {
    field: "xgov",
    headerName: "XGOV",
    width: 100,
    headerAlign: "left",
    flex: 0.5,
  },
  {
    field: "receivedDateUF",
    headerName: "",
    width: 0,
    hide: true,
    renderCell: (params) => <span></span>,
    flex: 1,
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
  if (!userGroups) {
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

  return defaultTableInfo;
};

export { getTableInfo };
