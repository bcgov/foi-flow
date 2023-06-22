import {   cellTooltipRender,
    eventCellTooltipRender
  } from "./utils";
   
  const EventQueueIAOColumns = [
  
    {
      field: "createdat",
      headerName: "DATE | TIME STAMP",
      width: 200,
      headerAlign: "left",
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      width: 160,
      renderCell: cellTooltipRender
    },
    {
      field: "creatorFormatted",
      headerName: "FROM",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "userFormatted",
      headerName: "TO",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "assignedToFormatted",
      headerName: "ASSIGNEE",
      headerAlign: "left",
      width: 160,
    },
  
    {
      field: "notification",
      headerName: "CONTENT",
      headerAlign: "left",
      width: 300,
     renderCell: eventCellTooltipRender
    }
    
  ];

  const EventQueueMinistryColumns = [
  
    {
      field: "createdat",
      headerName: "DATE | TIME STAMP",
      width: 200,
      headerAlign: "left",
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "creatorFormatted",
      headerName: "FROM",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "userFormatted",
      headerName: "TO",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "ministryAssignedToFormatted",
      headerName: "ASSIGNEE",
      headerAlign: "left",
      width: 160,
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
      // { field: "defaultSorting", sort: "asc" },
      { field: "createdat", sort: "desc" }
    ],
    noAssignedClassName: "not-assigned"
  };
  
  const getIAOEventQueueTableInfo = () => {
    
    defaultTableInfo.columns = EventQueueIAOColumns;
    return defaultTableInfo;
  };

  const getMinistryEventQueueTableInfo = () => {
    
    defaultTableInfo.columns = EventQueueMinistryColumns;
    return defaultTableInfo;
  };
  
  export { getIAOEventQueueTableInfo, getMinistryEventQueueTableInfo };
  