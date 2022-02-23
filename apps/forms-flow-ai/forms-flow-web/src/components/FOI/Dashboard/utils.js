import {
  formatDate,
  addBusinessDays,
  businessDay,
  calculateDaysRemaining,
  isProcessingTeam,
  isIntakeTeam,
  isFlexTeam,
} from "../../../helper/FOI/helper";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import Chip from "@mui/material/Chip";

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

    if (field == "assignedToName") {
      smodel.shift();
      smodel.unshift(
        { field: "assignedToLastName", sort: order },
        { field: "assignedToFirstName", sort: order }
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

export const getLDD = (params) => {
  let receivedDateString = params.row.duedate;
  const currentStatus = params.row.currentState;
  if (currentStatus.toLowerCase() === StateEnum.onhold.name.toLowerCase()) {
    return "N/A";
  } else {
    return formatDate(receivedDateString, "MMM dd yyyy").toUpperCase();
  }
};

export const getDaysLeft = (params) => {
  const receivedDateString = params.row.duedate;
  if (!receivedDateString) {
    return "";
  }

  if (
    params.row.currentState.toLowerCase() ===
    StateEnum.onhold.name.toLowerCase()
  ) {
    return "N/A";
  } else {
    return `${calculateDaysRemaining(receivedDateString)}`;
  }
};

export const ClickableChip = ({ clicked, ...rest }) => {
  return (
    <Chip
      sx={{
        ...(clicked
          ? {
              backgroundColor: "#38598A",
              width: "100%",
            }
          : {
              color: "#38598A",
              border: "1px solid #38598A",
              width: "100%",
            }),
      }}
      variant={clicked ? "filled" : "outlined"}
      {...rest}
    />
  );
};