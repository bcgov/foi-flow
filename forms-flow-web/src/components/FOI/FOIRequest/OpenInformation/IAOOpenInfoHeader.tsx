// import TextField from '@material-ui/core/TextField';
import { TextField } from "@material-ui/core";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { makeStyles, Theme } from '@material-ui/core/styles';
import { getMenuItems } from "../FOIRequestHeader/utils";
import { saveFOIOpenInfoRequest } from "../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { useDispatch } from "react-redux";
import "./openinfo.scss";

const OIAssignedToStyles = makeStyles((theme: Theme) => ({
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    item: {
        paddingLeft: theme.spacing(3),
    },
    group: {
        fontWeight: theme.typography.fontWeightBold as any,
        opacity: 1,
    },
    blankrow: {
      padding: 25
    }
  }));

const IAOOpenInfoHeader = ({
  requestNumber,
  requestDetails,
  isOIUser,
  assignedToList,
  foiministryrequestid,
  foirequestid,
  toast,
}: any) => {
  const dispatch = useDispatch();
  const classes = OIAssignedToStyles();
  let foiOITransactionData = useSelector(
    (state: any) => state.foiRequests.foiOpenInfoRequest
  ); 

  let iaoassignedToList = useSelector(
    (state : any) => state.foiRequests.foiAssignedToList
  );

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

  const [selectedAssignedTo, setAssignedTo] = useState(() => getFullName());

const handleOIAssigneeUpdate = async (event: any) => {
  const assigneeValue = event?.target?.value;
  const [groupName, username, firstName, lastName] = assigneeValue.split('|');
  const fullName = firstName !== "" ? `${lastName}, ${firstName}` : username;;

  // Update the selected assignee in the dropdown
  setOIAssignedTo(assigneeValue);
  
  const assigneeDetails = {
    assignedGroup: groupName,
    assignedTo: username,
    assignedToFirstName: firstName,
    assignedToLastName: lastName,
    assignedToName: fullName
  };

  const updatedOpenInfoRequest = {
    ...foiOITransactionData,  
    oiassignedto: username,
    assigneeDetails:assigneeDetails,
    publicationdate: foiOITransactionData.publicationdate ? 
    new Date(foiOITransactionData.publicationdate).toISOString().split('T')[0] : 
    null
  };

  dispatch(
    saveFOIOpenInfoRequest(
      foiministryrequestid, 
      foirequestid, 
      updatedOpenInfoRequest, 
      requestDetails,
      (err: any, res: any) => {
      if (!err) {
        toast.success("Assignee has been saved successfully.", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });  
      } else {
        toast.error(
          "Temporarily unable to save the assignee. Please try again in a few minutes.",
          {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
          }
        );
      }
    })
  );
}

const [menuItems, setMenuItems] = useState<any>([]);
const [selectedOIAssignedTo, setOIAssignedTo] = useState("Unassigned");

useEffect(() => {
  const oiTeam = iaoassignedToList?.find((team: any) => team.name === 'OI Team');
  const member = oiTeam?.members?.find(
    (member: any) => member.username === foiOITransactionData?.oiassignedto
  );

  if(isOIUser){
    const currentAssignee = member 
      ? `${oiTeam.name}|${member.username}|${member.firstname}|${member.lastname}`
      : "Unassigned";
    setOIAssignedTo(currentAssignee);

    const oiTeamOnly = iaoassignedToList?.filter((team: any) => team.name === 'OI Team');

    // Generate menu items for the dropdown with OI Team members only
    setMenuItems(
      getMenuItems({ 
        classes, 
        assignedToList: oiTeamOnly, 
        selectedAssignedTo: currentAssignee,
        isIAORestrictedRequest: false 
      })
    );
  } else {
      // For non-OI users, just set the formatted name
      const displayName = member 
        ? `${member.lastname}, ${member.firstname}`
        : "Unassigned";
      setOIAssignedTo(displayName);
  }
}, [iaoassignedToList, foiOITransactionData, isOIUser]);

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
          value={selectedOIAssignedTo}
          onChange={handleOIAssigneeUpdate}
          //input={<Input />}
          variant="outlined"
          fullWidth
          required={isOIUser}
          // disabled={disableHeaderInput}
          error={selectedOIAssignedTo.toLowerCase().includes("unassigned")}
        >
          {menuItems}
        </TextField>
      </div>
    </div>
  );
};

export default IAOOpenInfoHeader;
