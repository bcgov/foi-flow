import {
  getReceivedDate,
  getFullName,
  displayIcon,
  displayHeaderIcon,
  cellTooltipRender,
  eventCellTooltipRender
} from "../utils";
import {
  isProcessingTeam,
  isFlexTeam,
  isIntakeTeam,
  formatDateAndTimeStamp,
  formatDate,
  getUserFullName
} from "../../../../helper/FOI/helper";

const EventQueueColumns = [

  {
    field: "createdat",
    headerName: "DATE | TIME STAMP",
    width: 200,
    headerAlign: "left",
    //valueGetter: (params) => formatDate(params.row.cfrduedate, "MM/dd/yyyy"),
  },
  {
    field: "axisRequestId",
    headerName: "ID NUMBER",
    headerAlign: "left",
    width: 200,
    //renderCell: cellTooltipRender
  },
  {
    field: "createdby",
    headerName: "FROM",
    headerAlign: "left",
    width: 160,
    valueGetter: (params) => getUserFullName(params.row.createdby),
  },
  {
    field: "to",
    headerName: "TO",
    headerAlign: "left",
    width: 160,
    valueGetter: (params) => getUserFullName(params.row.createdby),
  },
  {
    field: "assignedTo",
    headerName: "ASSIGNEE",
    headerAlign: "left",
    width: 160,
    valueGetter: (params) => getUserFullName(params.row.assignedTo, params.row.assignedGroup),
  },

  {
    field: "notification",
    headerName: "CONTENT",
    headerAlign: "left",
    width: 300,
   renderCell: eventCellTooltipRender
  }
  
];

const defaultTableInfo = {
  sort: [
    { field: "defaultSorting", sort: "asc" },
    { field: "createdat", sort: "desc" }
  ],
  noAssignedClassName: "not-assigned"
};

const getEventQueueTableInfo = () => {
  
  defaultTableInfo.columns = EventQueueColumns;
  return defaultTableInfo;
};

export { getEventQueueTableInfo };
