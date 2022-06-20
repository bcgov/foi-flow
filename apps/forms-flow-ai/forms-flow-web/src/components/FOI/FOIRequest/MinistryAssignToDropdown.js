import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import "./ministryassigntodropdown.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { StateEnum } from '../../../constants/FOI/statusEnum';
import { createAssignedToDetailsObject } from './MinistryReview/utils';
import {
  saveAssignee
} from "../../../apiManager/services/FOI/foiAssigneeServices";
import { toast } from "react-toastify";
import { useDispatch } from "react-redux";
import _ from 'lodash';

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
const MinistryAssignToDropdown  = React.memo(({requestState, requestDetails, ministryAssignedToList, handleMinistryAssignedToValue, isMinistryCoordinator, requestId, ministryId, setSaveMinistryRequestObject}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const classes = useStyles();
    const dispatch = useDispatch();
    var assigneeDetails = _.pick(requestDetails, ['assignedGroup', 'assignedTo','assignedToFirstName','assignedToLastName',
    'assignedministrygroup','assignedministryperson','assignedministrypersonFirstName','assignedministrypersonLastName']);

    //local state management for assignedTo
    //------- update this later when $567 is ready
    const minsitryAssignedToGroup = assigneeDetails.assignedministrygroup ? assigneeDetails.assignedministrygroup : "";
    const ministryAssignedTo = assigneeDetails.assignedministryperson ? `${minsitryAssignedToGroup}|${assigneeDetails.assignedministryperson}|${assigneeDetails.assignedministrypersonFirstName}|${assigneeDetails.assignedministrypersonLastName}` : `|Unassigned`;
    const [selectedMinistryAssignedTo, setMinistryAssignedTo] = React.useState(ministryAssignedTo);

    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }
    
    //creates the grouped menu items for assignedTo combobox    
    const getMenuItems = () => {
      var menuItems = [];
      menuItems.push(
        <MenuItem className={classes.group} key={0} value={"|"} disabled={true}>
          {}
        </MenuItem>
      );
      menuItems.push(
        <MenuItem
          key={0}
          className={classes.item}
          value={"|Unassigned"}
          disabled={true}
        >
          {"Unassigned"}
        </MenuItem>
      );

      if (ministryAssignedToList && ministryAssignedToList.length < 1) {
        return menuItems;
      }

      ministryAssignedToList.forEach((group) => {
        const groupItem = (
          <MenuItem
            className={classes.group}
            key={group.id}
            value={`${group.name}|${group.name}`}
            disabled={true}
          >
            {group.name}
          </MenuItem>
        );
        menuItems.push(groupItem);

        const assigneeItems = group.members.map((assignee) => (
          <MenuItem
            key={`${assignee.id}`}
            className={classes.item}
            value={`${group.name}|${assignee.username}|${assignee.firstname}|${assignee.lastname}`}
            disabled={assignee.username.toLowerCase().includes("unassigned")}
          >
            {getFullName(
              assignee.lastname,
              assignee.firstname,
              assignee.username
            )}
          </MenuItem>
        ));

        menuItems.push(assigneeItems);
      });

      return menuItems;
    };

    const saveAssigneeDetails = (event) => {
      setMinistryAssignedTo(event.target.value);
      assigneeDetails = createAssignedToDetailsObject(event.target.value);
      dispatch(
        saveAssignee(assigneeDetails, requestId, ministryId, isMinistryCoordinator, (err, _res) => {
          if(!err) {
            toast.success("Assignee has been saved successfully.", {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
            //event bubble up - to validate required fields
            handleMinistryAssignedToValue(event.target.value);
            let reqObj= updateAssigneeInRequestDetails(requestDetails);
            setSaveMinistryRequestObject(reqObj);
          }
          else {
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
      )
    }

    const updateAssigneeInRequestDetails = (requestObject) => {
        requestObject.assignedministrygroup = assigneeDetails.assignedministrygroup;
        requestObject.assignedministrypersonFirstName = assigneeDetails.assignedministrypersonFirstName;
        requestObject.assignedministrypersonLastName = assigneeDetails.assignedministrypersonLastName;
        requestObject.assignedministryperson = assigneeDetails.assignedministryperson
        return requestObject;
    }
      
    

    return (
            <div className="foi-assigned-to-inner-container">
                <TextField
                    id="ministryAssignedTo"
                    label="Ministry Assigned To"
                    InputLabelProps={{ shrink: true, }}          
                    inputProps={{ "aria-labelledby": "ministryAssignedTo-label"}}
                    select
                    value={selectedMinistryAssignedTo}
                    onChange={saveAssigneeDetails}
                    input={<Input />} 
                    variant="outlined"
                    fullWidth
                    required = {isMinistryCoordinator && requestState.toLowerCase() == StateEnum.callforrecords.name.toLowerCase() }
                    disabled = {!isMinistryCoordinator || (requestState.toLowerCase() == StateEnum.closed.name.toLowerCase())}
                    error={isMinistryCoordinator && selectedMinistryAssignedTo.toLowerCase().includes("unassigned") }                    
                >            
                    {getMenuItems()}
                </TextField> 
            </div>
    );
  });

export default MinistryAssignToDropdown;