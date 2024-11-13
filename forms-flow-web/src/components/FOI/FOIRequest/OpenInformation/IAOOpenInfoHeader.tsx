import { TextField } from "@material-ui/core";
import { useState } from "react";

const IAOOpenInfoHeader = ({
  requestNumber,
  requestDetails,
  isOIUser,
  assignedToList,
}: any) => {
  const getGroupName = () => {
    if (requestDetails.assignedGroup) return requestDetails.assignedGroup;
    return "Unassigned";
  };
  const getAssignedTo = (groupName: any) => {
    if (requestDetails.assignedTo) return requestDetails.assignedTo;
    return groupName;
  };
  function getFullName() {
    const groupName = getGroupName();
    const assignedTo = getAssignedTo(groupName);
    if (assignedToList?.length > 0) {
      const assigneeGroup = assignedToList.find(
        (_assigneeGroup: any) => _assigneeGroup.name === groupName
      );
      const assignee = assigneeGroup?.members?.find(
        (_assignee: any) => _assignee.username === assignedTo
      );
      if (groupName === assignedTo) return groupName;
      return assignee !== undefined
        ? `${assignee.lastname}, ${assignee.firstname}`
        : "invalid user";
    }
    return groupName;
  }

  const menuItems = ["this", "that"]; // NEED TO ADJUST THIS FOR OI TEAM
  const [selectedAssignedTo, setAssignedTo] = useState(() => getFullName());

  return (
    <div className="oi-header">
      <h1 className="foi-review-request-text foi-ministry-requestheadertext">
        {requestNumber ? `Request #${requestNumber}` : ""}
      </h1>
      <div className="oi-assignment">
        <TextField
          id="assignedTo"
          label={"IAO Assigned To"}
          inputProps={{ "aria-labelledby": "assignedTo-label", readOnly: true }}
          InputLabelProps={{ shrink: true }}
          style={{ paddingBottom: "4%" }}
          value={selectedAssignedTo}
          variant="outlined"
          fullWidth
        ></TextField>
        <TextField
          id="oiAssignedTo"
          label={"OI Assigned To"}
          inputProps={{
            "aria-labelledby": "assignedTo-label",
            readOnly: !isOIUser,
          }}
          InputLabelProps={{ shrink: true }}
          select={isOIUser}
          // value={selectedAssignedTo}
          // onChange={handleAssigneeUpdate}
          // input={<Input />}
          variant="outlined"
          fullWidth
          required={isOIUser}
          // disabled={disableHeaderInput}
          error={selectedAssignedTo.toLowerCase().includes("unassigned")}
        >
          {menuItems}
        </TextField>
      </div>
    </div>
  );
};

export default IAOOpenInfoHeader;
