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

const OpenInfoHeader = ({
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

  if(username != 'OI Team'){
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
        isOIUser,
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
}

const [menuItems, setMenuItems] = useState<any>([]);
const [selectedOIAssignedTo, setOIAssignedTo] = useState("Unassigned");

useEffect(() => {
  // Find OI Team from the assignedToList
  const oiTeam = iaoassignedToList?.find((team: any) => team.name === 'OI Team');

  // Find specific member if request is assigned to individual
  const member = oiTeam?.members?.find(
    (member: any) => member.username === foiOITransactionData?.oiassignedto
  );

  if(isOIUser){
    /* For OI users, Mapping for assignee display values:
     - 'OI Team': When assigned to entire OI Team
     - 'member': When assigned to specific OI Team member
     - 'default': When unassigned */
    const assigneeMap = {
      'OI Team': 'OI Team|OI Team',
      'member': member && `${oiTeam.name}|${member.username}|${member.firstname}|${member.lastname}`,
      'default': 'OI Team|OI Team'
    };

    const currentAssignee = assigneeMap[foiOITransactionData?.oiassignedto === null ? 'OI Team' : member ? 'member' : 'default'];
    setOIAssignedTo(currentAssignee);

    // Generate menu items for the dropdown with OI Team members only
    setMenuItems(
      getMenuItems({ 
        classes, 
        assignedToList: iaoassignedToList?.filter((team: any) => team.name === 'OI Team'), 
        selectedAssignedTo: currentAssignee,
        isIAORestrictedRequest: false 
      })
    );
  } else {
      // For non-OI users, just set the formatted name
      const displayMap = {
        'OI Team': 'OI Team',
        'member': member && `${member.lastname}, ${member.firstname}`,
        'default': 'OI Team'
      };
  
      setOIAssignedTo(displayMap[foiOITransactionData?.oiassignedto === null ? 'OI Team' : member ? 'member' : 'default']);
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
          label={"FOI Ops Assigned To"}
          inputProps={{ "aria-labelledby": "assignedTo-label", readOnly: true }}
          InputLabelProps={{ shrink: true }}
          style={{ paddingBottom: "4%" }}
          value={selectedAssignedTo}
          variant="outlined"
          fullWidth
          disabled={isOIUser}
        ></TextField>
        <TextField
          id="oiAssignedTo"
          label={"OI Assigned To"}
          inputProps={{
            "aria-labelledby": "assignedTo-label"
          }}
          InputLabelProps={{ shrink: true }}
          value={selectedOIAssignedTo}
          onChange={handleOIAssigneeUpdate}
          variant="outlined"
          fullWidth
          select={isOIUser}
          required={isOIUser}
          disabled={!isOIUser}
          error={isOIUser && selectedOIAssignedTo.toLowerCase().includes("unassigned")}
        >
          {menuItems}
        </TextField>
      </div>
    </div>
  );
};

export default OpenInfoHeader;
