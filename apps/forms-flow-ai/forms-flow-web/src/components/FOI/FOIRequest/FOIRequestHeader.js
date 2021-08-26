import React from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./foirequestheader.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useParams } from 'react-router-dom';
import { calculateDaysRemaining } from "../../../helper/FOI/helper";

const useStyles = makeStyles((theme) => ({
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    item: {
        paddingLeft: theme.spacing(3),
    },
    group: {
        fontWeight: theme.typography.fontWeightBold,
        opacity: 1,
    },
  }));
const FOIRequestHeader  = React.memo(({headerValue, requestDetails, handleAssignedToInitialValue, handleAssignedToValue, createSaveRequestObject,handlestatusudpate}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const classes = useStyles();
    const {ministryId} = useParams();  
     //get the assignedTo master data
    const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);
    
    //handle default value for the validation of required fields
    React.useEffect(() => {
        let assignedTo = requestDetails.assignedTo ? (requestDetails.assignedGroup && requestDetails.assignedGroup !== "Unassigned" ? `${requestDetails.assignedGroup}|${requestDetails.assignedTo}` : "|Unassigned") : (requestDetails.assignedGroup ? `${requestDetails.assignedGroup}|${requestDetails.assignedGroup}`: "|Unassigned");
        assignedTo = assignedTo;
        handleAssignedToInitialValue(assignedTo);
        let _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);
        let _status = headerValue ? headerValue : (!!requestDetails.currentState ? requestDetails.currentState: "Unopened");
        handlestatusudpate(_daysRemaining,_status)

    },[requestDetails, handleAssignedToInitialValue, handlestatusudpate])

    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }
    
    //creates the grouped menu items for assignedTo combobox    
    const getMenuItems = () => {
        var menuItems = [];
        var i = 1;
        if (assignedToList && assignedToList.length > 0) {
            for (var group of assignedToList) {
                menuItems.push(<MenuItem className={classes.group} key={group.id} value={`${group.name}|${group.name}`}>{group.name}</MenuItem>);
                for (var assignee of group.members) {
                    menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={classes.item} value={`${group.name}|${assignee.username}`} disabled={assignee.username.toLowerCase().includes("unassigned")}>{getFullName(assignee.lastname, assignee.firstname, assignee.username)}</MenuItem>)
                }
            }
        }
        return menuItems;
    }
     //local state management for assignedTo
    const assignedTo = requestDetails.assignedTo ? (requestDetails.assignedGroup && requestDetails.assignedGroup !== "Unassigned" ? `${requestDetails.assignedGroup}|${requestDetails.assignedTo}` : "|Unassigned") : (requestDetails.assignedGroup ? `${requestDetails.assignedGroup}|${requestDetails.assignedGroup}`: "|Unassigned");
   
    const [selectedAssignedTo, setAssignedTo] = React.useState(assignedTo);
    const preventDefault = (event) => event.preventDefault();
    
    //handle onChange event for assigned To
    const handleAssignedToOnChange = (event) => {
        setAssignedTo(event.target.value);
        //event bubble up - to validate required fields
        handleAssignedToValue(event.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ASSIGNED_TO, event.target.value, event.target.name);
    }

    const hearderText = window.location.href.indexOf("createrequest") > -1 ? "Create Request" : (!!requestDetails.idNumber && ministryId ? requestDetails.idNumber : "Review Request");
    const daysRemaining = calculateDaysRemaining(requestDetails.dueDate);
    const hideDaysRemaining = ministryId && daysRemaining ? false: true;
    const status = headerValue ? headerValue : (!!requestDetails.currentState ? requestDetails.currentState: "Unopened");
    
     return (
        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h3 className="foi-review-request-text">{hearderText}</h3>
                    </Link>
                </div>           
            </div>
            
            <div className="foi-assigned-to-container">
                <div className="foi-assigned-to-inner-container">
                <TextField
                    id="assignedTo"
                    label="Assigned To"
                    InputLabelProps={{ shrink: true, }}          
                    select
                    value={selectedAssignedTo}
                    onChange={handleAssignedToOnChange}
                    input={<Input />} 
                    variant="outlined"
                    fullWidth
                    required
                    error={selectedAssignedTo.toLowerCase().includes("unassigned")}                    
                >            
                    {getMenuItems()}
                </TextField> 
                </div>
            </div>
        </div>
    );
  });

export default FOIRequestHeader;