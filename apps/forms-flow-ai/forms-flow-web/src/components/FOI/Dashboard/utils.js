import {
  formatDate,
  addBusinessDays,
  businessDay,
  calculateDaysRemaining,
} from "../../../helper/FOI/helper";
import { StateEnum } from "../../../constants/FOI/statusEnum";

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

export const getAssigneeValue = (row, assignedToList) => {
  const groupName = row.assignedGroup ? row.assignedGroup : "Unassigned";
  const assignedTo = row.assignedTo ? row.assignedTo : groupName;
  if (assignedToList && assignedToList.length > 0) {
    const assigneeDetails = assignedToList.find(
      (assigneeGroup) => assigneeGroup.name === groupName
    );
    const assignee =
      assigneeDetails &&
      assigneeDetails.members &&
      assigneeDetails.members.find(
        (_assignee) => _assignee.username === assignedTo
      );
    if (groupName === assignedTo) {
      return assignedTo;
    } else {
      return assignee !== undefined
        ? `${assignee.lastname}, ${assignee.firstname}`
        : "invalid user";
    }
  } else {
    return assignedTo;
  }
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
    smodel.map((row) => {
      if (row.field === "assignedToName") row.field = "assignedTo";
    });

    let field = smodel[0]?.field;
    let order = smodel[0]?.sort;
    if (field == "applicantName") {
      smodel.shift();
      smodel.unshift(
        { field: "lastName", sort: order },
        { field: "firstName", sort: order }
      );
    }
  }

  return smodel;
};

export const getFullName = (params) => {
  return `${params.row.lastName || ""}, ${params.row.firstName || ""}`;
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
  if (
    params.row.currentState.toLowerCase() ===
    StateEnum.onhold.name.toLowerCase()
  ) {
    return "N/A";
  } else {
    return calculateDaysRemaining(params.row.duedate);
  }
};
