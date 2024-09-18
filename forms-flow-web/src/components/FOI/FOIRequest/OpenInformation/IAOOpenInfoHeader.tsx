import { Grid, TextField, Typography } from "@material-ui/core";
import { useState } from "react";
import { getAssignedTo } from "../FOIRequestHeader/utils.js";
import _ from "lodash";

const IAOOpenInfoHeader = ({ requestNumber, requestDetails }: any) => {
  let assigneeDetails = _.pick(requestDetails, [
    "assignedGroup",
    "assignedTo",
    "assignedToFirstName",
    "assignedToLastName",
    "assignedministrygroup",
    "assignedministryperson",
    "assignedministrypersonFirstName",
    "assignedministrypersonLastName",
  ]);
  const menuItems = ["this", "that"];
  const [selectedAssignedTo, setAssignedTo] = useState(() =>
    getAssignedTo(assigneeDetails)
  );

  return (
    <div className="oi-header">
      <h1 className="foi-review-request-text foi-ministry-requestheadertext">
        {requestNumber ? `Request #${requestNumber}` : ""}
      </h1>
      <div className="oi-assignment">
        <TextField
          id="assignedTo"
          label={"IAO Assigned To"}
          inputProps={{ "aria-labelledby": "assignedTo-label" }}
          InputLabelProps={{ shrink: true }}
          style={{ paddingBottom: "4%" }}
          select
          value={selectedAssignedTo}
          // onChange={handleAssigneeUpdate}
          // input={<Input />}
          variant="outlined"
          fullWidth
          required
          // disabled={disableHeaderInput}
          error={selectedAssignedTo.toLowerCase().includes("unassigned")}
        >
          {menuItems}
        </TextField>
        <TextField
          id="oiAssignedTo"
          label={"OI Assigned To"}
          inputProps={{ "aria-labelledby": "assignedTo-label" }}
          InputLabelProps={{ shrink: true }}
          select
          value={selectedAssignedTo}
          // onChange={handleAssigneeUpdate}
          // input={<Input />}
          variant="outlined"
          fullWidth
          required
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
