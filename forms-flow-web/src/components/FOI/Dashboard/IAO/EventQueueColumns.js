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
  formatDate
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
    width: 200,
  },
  {
    field: "assignedTo",
    headerName: "ASSIGNEE",
    headerAlign: "left",
    width: 200,
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
    // { field: "duedate", sort: "asc" }
  ],
  noAssignedClassName: "not-assigned"
};

const getEventQueueTableInfo = () => {
  
  defaultTableInfo.columns = EventQueueColumns;
  return defaultTableInfo;
};

export { getEventQueueTableInfo };
