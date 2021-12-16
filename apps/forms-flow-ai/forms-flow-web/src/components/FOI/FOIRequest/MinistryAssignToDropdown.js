import React from 'react';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./ministryassigntodropdown.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useParams } from 'react-router-dom';
import { StateEnum } from '../../../constants/FOI/statusEnum';

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
const MinistryAssignToDropdown  = React.memo(({requestDetails, ministryAssignedToList, handleMinistryAssignedToValue, createSaveRequestObject, isMinistryCoordinator}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const classes = useStyles();
    const {requestState} = useParams();

    //local state management for assignedTo
    //------- update this later when $567 is ready
    const minsitryAssignedToGroup = requestDetails.assignedministrygroup ? requestDetails.assignedministrygroup : "";
    const ministryAssignedTo = requestDetails.assignedministryperson ? `${minsitryAssignedToGroup}|${requestDetails.assignedministryperson}` : `|Unassigned`;
    const [selectedMinistryAssignedTo, setMinistryAssignedTo] = React.useState(ministryAssignedTo);
    
    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }
    
    //creates the grouped menu items for assignedTo combobox    
    const getMenuItems = () => {
        var menuItems = [];
        var i = 1;

        //add default value (unassigned)
        menuItems.push(<MenuItem className={classes.group} key={0} value={'|'} disabled={true} >{}</MenuItem>);
        menuItems.push(<MenuItem key={0} className={classes.item} value={'|Unassigned'} disabled={true} >{'Unassigned'}</MenuItem>)

        if (ministryAssignedToLis?.length > 0) {
            for (var group of ministryAssignedToList) {
                menuItems.push(<MenuItem className={classes.group} key={group.id} value={`${group.name}|${group.name}`} disabled={true} >{group.name}</MenuItem>);
                for (var assignee of group.members) {
                    menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={classes.item} value={`${group.name}|${assignee.username}`} disabled={assignee.username.toLowerCase().includes("unassigned")}>{getFullName(assignee.lastname, assignee.firstname, assignee.username)}</MenuItem>)
                }
            }
        }
        return menuItems;
    }

    //handle onChange event for assigned To
    const handleMinistryAssignedToOnChange = (event) => {
        setMinistryAssignedTo(event.target.value);
        handleMinistryAssignedToValue(event.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.MINISTRY_ASSIGNED_TO, event.target.value, event.target.name);
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
                    required = {isMinistryCoordinator && requestState.toLowerCase() == StateEnum.callforrecords.name.toLowerCase() }
                    disabled = {!isMinistryCoordinator || requestState.toLowerCase() != StateEnum.callforrecords.name.toLowerCase() }
                    error={isMinistryCoordinator && selectedMinistryAssignedTo.toLowerCase().includes("unassigned")  && requestState.toLowerCase() == StateEnum.callforrecords.name.toLowerCase() }                    
                >            
                    {getMenuItems()}
                </TextField> 
            </div>
    );
  });

export default MinistryAssignToDropdown;