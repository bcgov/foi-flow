import {
  formatDate,
  addBusinessDays,
  businessDay,
  calculateDaysRemaining,
} from "../../../helper/FOI/helper";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import Chip from "@mui/material/Chip";
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

export const updateEventSortModel = (sortModel) => {
  let smodel = JSON.parse(JSON.stringify(sortModel));
  if (smodel) {
    let field = smodel[0]?.field;
    let order = smodel[0]?.sort;

    // if (field == "applicantName") {
    //   smodel.shift();
    //   smodel.unshift(
    //     { field: "lastName", sort: order },
    //     { field: "firstName", sort: order }
    //   );
    // }

    // if (field == "DueDateValue") {
    //   smodel.shift();
    //   smodel.unshift(
    //     { field: "duedate", sort: order },
    //   );
    // }

    // if (field == "DaysLeftValue") {
    //   smodel.shift();
    //   smodel.unshift(
    //     { field: "duedate", sort: order },
    //   );
    // }

    //add duedate to default sorting
    if (smodel.length == 1 && (field == "defaultSorting" || field == "intakeSorting")) {
      smodel.push(
        { field: "cfrduedate", sort: order },
      );
    }
    // if (smodel.length == 1 && field == "currentState") {
    //   smodel.push(
    //     { field: "receivedDateUF", sort: "desc" },
    //   );
    // }
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

export const getRecordsDue = (params) => {
  let receivedDateString = params.row.cfrduedate;
  const currentStatus = params.row.currentState;
  if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
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
  if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
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
    params.row.currentState.toLowerCase() ===
    StateEnum.onhold.name.toLowerCase()
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

export const displayHeaderIcon = (params) => {
  return (
    <span className="foi-dashboard-restricted"><FontAwesomeIcon icon={faFlag} size='2x' className='restrict-icon' />
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
  return <LightTooltip placement="bottom-start" title={
    <div style={{whiteSpace: "pre-line"}}>
      {description}
    </div>
  }>
    <span className="table-cell-truncate">{params.row.axisRequestId}</span>
  </LightTooltip>
};

export const eventCellTooltipRender = (params) => {

  let description = params.row.description;

  const truncatedDescription = description.length > 100 ? description.slice(0, 100) + '...' : description;

  return (
    <LightTooltip placement="bottom-start" title={<div style={{ whiteSpace: 'pre-line' }}>{description}</div>}>
      <span className="table-cell-truncate">{truncatedDescription}</span>
    </LightTooltip>
  );
  
};