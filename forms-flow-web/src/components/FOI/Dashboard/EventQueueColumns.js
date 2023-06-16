import {   
    eventCellTooltipRender
  } from "./utils";
  import {  
    getUserFullName
  } from "../../../helper/FOI/helper";
  
  const EventQueueIAOColumns = [
  
    {
      field: "createdat",
      headerName: "DATE | TIME STAMP",
      width: 160,
      headerAlign: "left",
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "createdby",
      headerName: "FROM",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.creatorFirstName, params.row.creatorLastName, params.row.createdby),
    },
    {
      field: "to",
      headerName: "TO",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.userFirstName, params.row.userLastName, params.row.to),
    },
    {
      field: "assignedTo",
      headerName: "ASSIGNEE",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.assignedToFirstName, params.row.assignedToLastName, params.row.assignedTo, params.row.assignedGroup),
    },
  
    {
      field: "notification",
      headerName: "CONTENT",
      headerAlign: "left",
      width: 400,
     renderCell: eventCellTooltipRender
    }
    
  ];

  const EventQueueMinistryColumns = [
  
    {
      field: "createdat",
      headerName: "DATE | TIME STAMP",
      width: 160,
      headerAlign: "left",
    },
    {
      field: "axisRequestId",
      headerName: "ID NUMBER",
      headerAlign: "left",
      width: 160,
    },
    {
      field: "createdby",
      headerName: "FROM",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.creatorFirstName, params.row.creatorLastName, params.row.createdby),
    },
    {
      field: "to",
      headerName: "TO",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.userFirstName, params.row.userLastName, params.row.to),
    },
    {
      field: "assignedTo",
      headerName: "ASSIGNEE",
      headerAlign: "left",
      width: 160,
      valueGetter: (params) => getUserFullName(params.row.assignedministrypersonFirstName, params.row.assignedministrypersonLastName, params.row.assignedministryperson, params.row.assignedministrygroup),
    },
  
    {
      field: "notification",
      headerName: "CONTENT",
      headerAlign: "left",
      width: 400,
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
  