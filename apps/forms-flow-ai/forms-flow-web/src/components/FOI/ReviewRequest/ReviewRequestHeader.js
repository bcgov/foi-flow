import React from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import "./reviewrequestheader.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';


const ReviewRequestHeader = React.memo(({requestDetails, handleAssignedToInitialValue, handleAssignedToValue}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 

     //get the assignedTo master data
    const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);
    
    //handle default value for the validation of required fields
    React.useEffect(() => {
        const assignedTo = requestDetails.currentState !== "Unopened"? requestDetails.assignedTo:"Unassigned";  
        handleAssignedToInitialValue(assignedTo);
    },[requestDetails, handleAssignedToInitialValue])

    //creates the menu items for assignedTo combobox
    const menuItems = assignedToList.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("unassigned")}>{item.name}</MenuItem> )
     });
    
     //local state management for assignedTo
    const [selectedAssignedTo, setAssignedTo] = React.useState(requestDetails.currentState !== "Unopened"? requestDetails.assignedTo:"Unassigned");

    const preventDefault = (event) => event.preventDefault();
    
    //handle onChange event for assigned To
    const handleAssignedToOnChange = (event) => {
        setAssignedTo(event.target.value);
        //event bubble up - to validate required fields
        handleAssignedToValue(event.target.value);
    }

     return (
        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h3 className="foi-review-request-text">Review Request</h3>
                    </Link>
                    <h3 className="foi-period-text">  |  </h3>
                    <Link href="#" onClick={preventDefault}>
                    <h3 className="foi-correspondence-text"> Correspondence</h3>
                    </Link>
                </div>            
            <div className="foi-request-status">
                UnOpened
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