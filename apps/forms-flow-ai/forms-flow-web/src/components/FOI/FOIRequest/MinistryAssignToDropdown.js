import React from 'react';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./ministryassigntodropdown.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useParams } from 'react-router-dom';

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
const MinistryAssignToDropdown  = React.memo(({requestDetails, handleMinistryAssignedToValue, createSaveRequestObject}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const classes = useStyles();
    const {ministryId} = useParams();
    const user = useSelector((state) => state.user.userDetail);

     //get the assignedTo master data
    const ministryAssignedToList = useSelector(state=> state.foiRequests.foiMinistryAssignedToList);
    
    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }
    
    //creates the grouped menu items for assignedTo combobox    
    const getMenuItems = () => {
        var menuItems = [];
        var i = 1;
        if (ministryAssignedToList && ministryAssignedToList.length > 0) {
            for (var group of ministryAssignedToList) {
                menuItems.push(<MenuItem className={classes.group} key={group.id} value={`${group.name}|${group.name}`}>{group.name}</MenuItem>);
                for (var assignee of group.members) {
                    menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={classes.item} value={`${group.name}|${assignee.username}`} disabled={assignee.username.toLowerCase().includes("unassigned")}>{getFullName(assignee.lastname, assignee.firstname, assignee.username)}</MenuItem>)
                }
            }
        }
        return menuItems;
    }

    //local state management for assignedTo
    const ministryAssignedToGroup = requestDetails.selectedMinistries && requestDetails.selectedMinistries[0].code ? requestDetails.selectedMinistries[0].code.toUpperCase()+" Ministry Team" : "Unassigned";
    //------- update this later when $567 is ready
    const ministryAssignedTo = requestDetails.selectedMinistries && requestDetails.selectedMinistries[0].code ? requestDetails.selectedMinistries[0].code.toUpperCase()+" Ministry Team" : "Unassigned";
    const ministryReadonly = !(user && user.groups.includes(`/${ministryAssignedToGroup}`));

    const [selectedMinistryAssignedTo, setMinistryAssignedTo] = React.useState(ministryAssignedTo);
   
    //handle onChange event for assigned To
    const handleMinistryAssignedToOnChange = (event) => {
        setMinistryAssignedTo(event.target.value);
        //event bubble up - to validate required fields
        handleMinistryAssignedToValue(event.target.value);
        //save ministry assignedTo to request - on hold
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.MINISTRY_ASSIGNED_TO, event.target.value, event.target.name);
        console.log(`handleMinstryAssignedToOnChange Header ${event.target.value}`)
    }

    return (
            <div className="foi-assigned-to-inner-container">
                <TextField
                    id="ministryAssignedTo"
                    label="Ministry Assigned To"
                    InputLabelProps={{ shrink: true, }}          
                    select
                    value={selectedMinistryAssignedTo}
                    onChange={handleMinistryAssignedToOnChange}
                    input={<Input />} 
                    variant="outlined"
                    fullWidth
                    required
                    // inputProps={
                    //     { readOnly: ministryReadonly, }
                    // }
                    disabled = {ministryReadonly}
                    error={ministryAssignedTo.toLowerCase().includes("unassigned")}                    
                >            
                    {getMenuItems()}
                </TextField> 
            </div>
    );
  });

export default MinistryAssignToDropdown;