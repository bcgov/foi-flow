import { getFullName, getDaysLeft, getReceivedDate, getGroup } from "../utils";

const ProcessingTeamColumns = [
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    headerAlign: "left",
  },
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    headerAlign: "left",
    valueGetter: getFullName,
  },
  {
    field: "onBehalf",
    headerName: "ON BEHALF",
    headerAlign: "left",
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    headerAlign: "left",
  },
  {
    field: "applicantcategory",
    headerName: "APPLICANT TYPE",
    headerAlign: "left",
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
  },
  {
    field: "DaysLeftValue",
    headerName: "DAYS LEFT",
    headerAlign: "left",
    valueGetter: getDaysLeft,
  },
  {
    field: "extensions",
    headerName: "EXT.",
    headerAlign: "left",
  },
  {
    field: "pages",
    headerName: "PAGES",
    headerAlign: "left",
  },
  {
    field: "xgov",
    headerName: "XGOV",
    headerAlign: "left",
  },
];

const IntakeTeamColumns = [
  {
    field: "applicantName",
    headerName: "APPLICANT NAME",
    width: 170,
    headerAlign: "left",
    valueGetter: getFullName,
  },
  {
    field: "requestType",
    headerName: "REQUEST TYPE",
    width: 150,
    headerAlign: "left",
  },
  {
    field: "idNumber",
    headerName: "ID NUMBER",
    width: 150,
    headerAlign: "left",
  },
  {
    field: "currentState",
    headerName: "CURRENT STATE",
    headerAlign: "left",
    width: 180,
  },
  {
    field: "assignedToName",
    headerName: "ASSIGNED TO",
    width: 180,
    headerAlign: "left",
  },
  {
    field: "receivedDate",
    headerName: "RECEIVED DATE",
    width: 180,
    headerAlign: "left",
    valueGetter: getReceivedDate,
  },
  { field: "xgov", headerName: "XGOV", width: 100, headerAlign: "left" },
  {
    field: "receivedDateUF",
    headerName: "",
    width: 0,
    hide: true,
    renderCell: (params) => <span></span>,
  },
];

const getTableInfo = (userGroups) => {
  const group = getGroup(userGroups);

  if (group === "processingTeam") {
    return {
      columns: ProcessingTeamColumns,
      sort: [
        { field: "currentState", sort: "desc" },
        { field: "receivedDateUF", sort: "desc" },
      ],
    };
  }

  return {
    columns: IntakeTeamColumns,
    sort: [
      { field: "currentState", sort: "desc" },
      { field: "receivedDateUF", sort: "desc" },
    ],
  };
};

export { getTableInfo };
