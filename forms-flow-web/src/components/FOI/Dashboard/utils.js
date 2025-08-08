import {
  formatDate,
  addBusinessDays,
  businessDay,
  calculateDaysRemaining,
} from "../../../helper/FOI/helper";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { MinistryNeedsLANPages, RequestTypes, ConsultTypes } from "../../../constants/FOI/enum";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import LabelIcon from '@mui/icons-material/Label';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFlag } from '@fortawesome/free-solid-svg-icons'; 
import Tooltip, { tooltipClasses } from '@mui/material/Tooltip';
import { styled } from '@mui/material/styles';

export const debounce = (func, wait) => {
  let timeout;

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const getAssigneeValue = (row) => {
  const groupName = row.assignedGroup ? row.assignedGroup : "Unassigned";
  return row.assignedTo && row.assignedToFirstName && row.assignedToLastName
    ? `${row.assignedToLastName}, ${row.assignedToFirstName}`
    : groupName;
};

export const getReceivedDate = (params) => {
  let receivedDateString = params.row.receivedDateUF;
  const dateString = receivedDateString
    ? receivedDateString.substring(0, 10)
    : "";
  receivedDateString = receivedDateString ? new Date(receivedDateString) : "";

  if (
    receivedDateString !== "" &&
    (receivedDateString.getHours() > 16 ||
      (receivedDateString.getHours() === 16 &&
        receivedDateString.getMinutes() > 30) ||
      !businessDay(dateString))
  ) {
    receivedDateString = addBusinessDays(receivedDateString, 1);
  }
  return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
};

export const getClosedDate = (params) => {
  let closedDateString = params.row.closedate;
  const dateString = closedDateString
    ? closedDateString.substring(0, 10)
    : "";
    closedDateString = closedDateString ? new Date(closedDateString) : "";
  if (
    closedDateString !== "" &&
    (closedDateString.getHours() > 16 ||
      (closedDateString.getHours() === 16 &&
        closedDateString.getMinutes() > 30) ||
      !businessDay(dateString))
  ) {
    closedDateString = addBusinessDays(closedDateString, 1);
  }
  return formatDate(closedDateString, "MMM dd yyyy").toUpperCase();
};

// update sortModel for applicantName & assignedTo
export const updateSortModel = (sortModel) => {
  let smodel = JSON.parse(JSON.stringify(sortModel));
  if (smodel) {
    let field = smodel[0]?.field;
    let order = smodel[0]?.sort;

    if (field == "applicantName") {
      smodel.shift();
      smodel.unshift(
        { field: "lastName", sort: order },
        { field: "firstName", sort: order }
      );
    }

    if (field == "DueDateValue") {
      smodel.shift();
      smodel.unshift(
        { field: "duedate", sort: order },
      );
    }

    if (field == "DaysLeftValue") {
      smodel.shift();
      smodel.unshift(
        { field: "duedate", sort: order },
      );
    }

    //add duedate to default sorting
    if (smodel.length == 1 && (field == "defaultSorting" || field == "intakeSorting")) {
      smodel.push(
        { field: "duedate", sort: order },
      );
    }
    if (smodel.length == 1 && field == "currentState") {
      smodel.push(
        { field: "receivedDateUF", sort: "desc" },
      );
    }
  }

  return smodel;
};

export const updateEventSortModel = (sortModel, isMinistry) => {
  let smodel = JSON.parse(JSON.stringify(sortModel));
  if (smodel) {
    let field = smodel[0]?.field;
    let order = smodel[0]?.sort;
    
    //add createdat to default sorting
    if (smodel.length == 1 && field == "defaultSorting") {
      smodel.push(
        { field: "createdat", sort: order },
      );
    }
  }

  return smodel;
};

export const getFullName = (firstName, lastName) => {
  if (!firstName && !lastName) {
    return "";
  }
  return `${lastName || ""}, ${firstName || ""}`;
};

export const onBehalfFullName = (params) => {
  if (!params.row.onBehalfFirstName && !params.row.onBehalfLastName) {
    return "N/A";
  }
  return `${params.row.onBehalfFirstName || ""} ${
    params.row.onBehalfLastName || ""
  }`;
};

export const formatRequestType = (requeststatus) => {
  if (!requeststatus) {
    return "";
  }
  let formattedRequestState= Object.values(StateEnum).find(state => state.label === requeststatus).name
  return formattedRequestState;
};


export const getRecordsDue = (params) => {
  let receivedDateString = params.row.cfrduedate;
  const currentStatus = params.row.currentState;
  if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase() || currentStatus.toLowerCase() === StateEnum.onholdother.name.toLowerCase()) {
    return "N/A";
  } else if(!receivedDateString) {
    return "";
  } else {
    return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
  }
};

export const getLDD = (params) => {
  let receivedDateString = params.row.duedate;
  const currentStatus = params.row.currentState;
  if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()||currentStatus.toLowerCase() === StateEnum.onholdother.name.toLowerCase()) {
    return "N/A";
  } else if(!receivedDateString) {
    return "";
  } else {
    return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
  }
};

export const getDaysLeft = (params) => {
  const receivedDateString = params.row.duedate;

  if (
    [StateEnum.onhold.name.toLowerCase(), StateEnum.closed.name.toLowerCase(), StateEnum.onholdother.name.toLowerCase()].includes(params.row.currentState.toLowerCase())
  ) {
    return "N/A";
  } else if(!receivedDateString) {
    return "";
  } else {
    return `${calculateDaysRemaining(receivedDateString)}`;
  }
};

export const ClickableChip = ({ clicked, sx={}, color, ...rest }) => {
  return (
    <Chip
      sx={[
        {
        ...(clicked
          ? {
              backgroundColor: (color === 'primary' ? "#38598A" : color),
              color: "white",
              width: "100%",
            }
          : {
              color: (color === 'primary' ? "#38598A" : color),
              border: ("1px solid " + (color === 'primary' ? "#38598A" : color)),
              width: "100%",
            }),
          ...sx
        },
        {
          '&:focus': {
            backgroundColor: (color === 'primary' ? "#38598A" : color),
            color: "white",
          }
        },
      ]}
      variant={clicked ? "filled" : "outlined"}
      {...rest}
    />
  );
};

export const addYears = (n) => {
  const currentDate = new Date();
  return currentDate.setFullYear(currentDate.getFullYear() + n);
};

export const displayIcon = (params) => {
  return (
    params?.row?.isiaorestricted ? 
    <><FontAwesomeIcon icon={faFlag} size='2x' className='restrict-icon' />
    </> : ""
  );
};

export const displayIconMinistry = (params) => {
  return (
    params?.row?.isministryrestricted ? 
    <><FontAwesomeIcon icon={faFlag} size='2x' className='restrict-icon' />
    </> : ""
  );
};

export const displayQueueFlagIcons = (params) => {
  let restricted = <span></span>

  if (params?.row?.isiaorestricted || params?.row?.isministryrestricted) {
    restricted = <LightTooltip placement="top-end" title={
      <div style={{whiteSpace: "pre-line"}}>
        Restricted
      </div>
    }>
      <span className="dashboard-flag-restricted"><FontAwesomeIcon icon={faFlag} size='2x' /></span>
    </LightTooltip>
  } else {
    restricted = <span className="dashboard-flag-placeholder"><FontAwesomeIcon icon={faFlag} size='2x' /></span>
  }

  const oipcreview = params?.row?.isoipcreview ?
  <LightTooltip placement="top-end" title={
    <div style={{whiteSpace: "pre-line"}}>
      OIPC
    </div>
  }><span className="dashboard-flag-oipcreview"><FontAwesomeIcon icon={faFlag} size='2x' /></span>
  </LightTooltip> :
  <span className="dashboard-flag-placeholder"><FontAwesomeIcon icon={faFlag} size='2x' /></span>

  const phasedrelease = params?.row?.isphasedrelease ?
  <LightTooltip placement="top-end" title={
    <div style={{whiteSpace: "pre-line"}}>
      Phased Release
    </div>
  }><span className="dashboard-flag-phasedrelease"><FontAwesomeIcon icon={faFlag} size='2x' /></span>
  </LightTooltip> :
  <span className="dashboard-flag-placeholder"><FontAwesomeIcon icon={faFlag} size='2x' /></span>

  return  <div>
            {restricted}
            {oipcreview}
            {phasedrelease}
          </div>
}

export const displayHeaderIcon = (params) => {
  return (
    <span className="dashboard-flag-restricted"><FontAwesomeIcon icon={faFlag} size='2x' className='restrict-icon' />
    </span> 
  );
};

export const LightTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: theme.palette.common.white,
    color: 'rgba(0, 0, 0, 0.87)',
    boxShadow: theme.shadows[1],
    fontSize: 13,
  },
}));

export const cellTooltipRender = (params) => {
  var description = params.row.description;
  if (params.row.fromdate && params.row.todate) {
    description += "\n(" + (new Date(params.row.fromdate)).toLocaleDateString() + " to " + (new Date(params.row.todate)).toLocaleDateString() + ")"
  }

  const hasSubConsults = Array.isArray(params.row.subConsults) && params.row.subConsults.length > 0;

  return (
    <Box display="flex" alignItems="center" gap={0.5} sx={{ minWidth: 0, flex: 1 }}>
      {hasSubConsults && (
        <LightTooltip placement="top" title="This request has internal consultations">
          <div className="subconsult-flag-container" style={{ flexShrink: 0 }}>
            <LabelIcon className="subconsult-label-bg" />
            <FontAwesomeIcon icon={faFlag} className="subconsult-flag-icon" />
          </div>
        </LightTooltip>
      )}
      <LightTooltip placement="bottom-start" title={
        <div style={{whiteSpace: "pre-line"}}>
          {description}
        </div>
      }>
        <span className="table-cell-truncate" style={{ minWidth: 0, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{params.row.axisRequestId}</span>
      </LightTooltip>
    </Box>
  );
};

export const pagecountcellTooltipRender = (params) => {
  const axispagecount = params.row.axispagecount;
  const recordspagecount = params.row.recordspagecount;
  const requestpagecount = params.row.requestpagecount;
  const lanpagecount = params.row.axislanpagecount;
  const bcgovcode = params.row.bcgovcode;
  const requestType = params.row.requestType;
  let toolTipText = "";
  if (requestpagecount > 0 || lanpagecount > 0) {
    if (requestpagecount > 0) {
      toolTipText += `AXIS pages: ${axispagecount} \n Mod pages: ${recordspagecount} \n`;
    }
    if (MinistryNeedsLANPages.includes(bcgovcode?.toUpperCase()) && requestType?.toLowerCase() === RequestTypes.personal) {
      toolTipText += `LAN pages: ${lanpagecount} \n`;
    }
  }
  return toolTipText ? (
    <LightTooltip placement="bottom-start" title={<div style={{ whiteSpace: "pre-line" }}>{toolTipText}</div>}>
      <span className="table-cell-truncate">{requestpagecount}</span>
    </LightTooltip>
  ) : null;
};

export const eventCellTooltipRender = (params) => {

  let notification = params.row?.notification;
  if (notification?.length > 25) {
  const truncatedNotification = notification?.length > 25 ? notification?.slice(0, 25) + '...' : notification;

  return (
    <LightTooltip placement="bottom-start" title={<div style={{ whiteSpace: 'pre-line' }}>{notification}</div>}>
      <span className="table-cell-truncate">{truncatedNotification}</span>
    </LightTooltip>
  );
  }
};

export const getConsultType = (params) => {
  const typeId = params;
  return ConsultTypes[typeId] || '';
}

export const getConsultReceivedDate = (params) => {
  let createdAtString = params.row.receivedDate;
  console.log("createdAtString : ",createdAtString)
  const dateString = createdAtString
    ? createdAtString.substring(0, 10)
    : "";
  let createdAt = createdAtString ? new Date(createdAtString) : "";

  if (
    createdAt !== "" &&
    (createdAt.getHours() > 16 ||
      (createdAt.getHours() === 16 && createdAt.getMinutes() > 30) ||
      !businessDay(dateString))
  ) {
    createdAt = addBusinessDays(createdAt, 1);
  }

  return formatDate(createdAt, "MMM dd yyyy").toUpperCase();
};

export const getConsultDueDaysLeft = (params) => {
  const receivedDateString = params.row.consultduedate;

  if (
    [StateEnum.onhold.name.toLowerCase(), StateEnum.closed.name.toLowerCase(), StateEnum.onholdother.name.toLowerCase()].includes(params.row.currentState.toLowerCase())
  ) {
    return "N/A";
  } else if(!receivedDateString) {
    return "";
  } else {
    return `${calculateDaysRemaining(receivedDateString)}`;
  }
};

export const mergeSubConsultsWithRow = (row) => {
  if (!Array.isArray(row?.subConsults)) return [];

  return row.subConsults.map((consult) => ({
    ...consult,
    firstName: row.firstName,
    lastName: row.lastName,
    onBehalfFormatted: row.onBehalfFormatted,
    extensions: row.extensions,
    applicantcategory: row.applicantcategory,
    idnumber: row.idnumber,
    duedate: row.duedate,
    cfrduedate: row.cfrduedate,
    requestpagecount: row.requestpagecount,
    applicantcategory: row.applicantcategory,
  }));
};