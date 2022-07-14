import MenuItem from "@material-ui/core/MenuItem";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

export const getFullName = (lastName, firstName, username) => {
  return firstName !== "" ? `${lastName}, ${firstName}` : username;
};

//creates the grouped menu items for assignedTo combobox
export const getMenuItems = ({
  classes,
  assignedToList,
  selectedAssignedTo,
}) => {
  let menuItems = [];
  menuItems.push(
    <MenuItem className={classes.group} key={0} value={"|"}>
      {}
    </MenuItem>
  );
  menuItems.push(
    <MenuItem
      key={1}
      className={classes.item}
      value={selectedAssignedTo}
      disabled={true}
    >
      {"Unassigned"}
    </MenuItem>
  );
  if (assignedToList && assignedToList.length < 1) {
    return menuItems;
  }
  else {
    assignedToList = assignedToList.filter(assignedTo => assignedTo.type === 'iao');
  }  
  assignedToList?.forEach((group) => {
    const groupItem = (
      <MenuItem
        className={classes.group}
        key={group.id}
        value={`${group.name}|${group.name}`}
      >
        {group.name}
      </MenuItem>
    );
    menuItems.push(groupItem);

    const assigneeItems = group?.members.map((assignee) => (
      <MenuItem
        key={`${assignee.id}`}
        className={classes.item}
        value={`${group.name}|${assignee.username}|${assignee.firstname}|${assignee.lastname}`}
      >
        {getFullName(assignee.lastname, assignee.firstname, assignee.username)}
      </MenuItem>
    ));
    
    menuItems.push(assigneeItems);

  });

  return menuItems;
};

export const getHeaderText = ({requestDetails, ministryId, status}) => {
  if (window.location.href.includes(FOI_COMPONENT_CONSTANTS.ADDREQUEST)) {
    return FOI_COMPONENT_CONSTANTS.ADD_REQUEST;
  }
  
  if(status?.toLowerCase() === StateEnum.unopened.name.toLowerCase()){
    return FOI_COMPONENT_CONSTANTS.REVIEW_REQUEST;
  }

  if(requestDetails.axisRequestId)
    return requestDetails.axisRequestId;

  if (requestDetails.idNumber && ministryId) {
    return requestDetails.idNumber;
  }

  return FOI_COMPONENT_CONSTANTS.REVIEW_REQUEST;
};

export const getAssignedTo = (assigneeDetails) => {
  if (!assigneeDetails.assignedGroup || assigneeDetails.assignedTo === "Unassigned") {
    return "|Unassigned";
  }

  return assigneeDetails.assignedTo
    ? `${assigneeDetails.assignedGroup}|${assigneeDetails.assignedTo}|${assigneeDetails.assignedToFirstName}|${assigneeDetails.assignedToLastName}`
    : `${assigneeDetails.assignedGroup}|${assigneeDetails.assignedGroup}`;
};

export const getStatus = ({ headerValue, requestDetails }) => {
  if (headerValue) return headerValue;

  if (requestDetails.currentState) return requestDetails.currentState;

  return StateEnum.unopened.name;
};