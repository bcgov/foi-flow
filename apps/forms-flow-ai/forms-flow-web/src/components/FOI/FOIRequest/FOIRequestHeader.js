import React from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import "./foirequestheader.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useParams } from 'react-router-dom';
import { calculateDaysRemaining } from "../../../helper/FOI/helper";

const ReviewRequestHeader = React.memo(({headerValue, requestDetails, handleAssignedToInitialValue, handleAssignedToValue, createSaveRequestObject}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const {ministryId} = useParams();  
     //get the assignedTo master data
    const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);
    
    //handle default value for the validation of required fields
    React.useEffect(() => {
        let assignedTo = requestDetails.assignedTo;
        assignedTo = assignedTo ? assignedTo: "Unassigned";
        handleAssignedToInitialValue(assignedTo);
    },[requestDetails, handleAssignedToInitialValue])

    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }

    //creates the menu items for assignedTo combobox
    const menuItems = assignedToList.map((item) => {    
        return ( <MenuItem key={item.id} value={item.username} name={getFullName(item.lastname,item.firstname,item.username)} disabled={item.username.toLowerCase().includes("unassigned")}>{getFullName(item.lastname,item.firstname,item.username)}</MenuItem> )
     });
    
     //local state management for assignedTo
    const [selectedAssignedTo, setAssignedTo] = React.useState(requestDetails.assignedTo ? requestDetails.assignedTo : "Unassigned");

    const preventDefault = (event) => event.preventDefault();
    
    //handle onChange event for assigned To
    const handleAssignedToOnChange = (event) => {
        setAssignedTo(event.target.value);
        //event bubble up - to validate required fields
        handleAssignedToValue(event.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ASSIGNED_TO, event.target.value, event.target.name);
    }

    const hearderText = window.location.href.indexOf("createrequest") > -1 ? "Create Request" : "Review Request";//(!!requestDetails.idNumber ? requestDetails.idNumber : "Review Request");
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
            <div className="foi-request-status">
                {status}
            </div>
            <div className="foi-request-daysremaining" hidden={hideDaysRemaining}>
                {`${daysRemaining} Days Remaining`}
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
                    {menuItems}
                </TextField> 
                </div>
            </div>
        </div>
    );
  });

export default ReviewRequestHeader;