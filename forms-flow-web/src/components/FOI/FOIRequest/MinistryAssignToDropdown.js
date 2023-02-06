import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import "./ministryassigntodropdown.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { StateEnum } from '../../../constants/FOI/statusEnum';
import { createAssignedToDetailsObject } from './MinistryReview/utils';
import { isRequestMinistryRestricted } from '../../../helper/FOI/helper';
import {
  saveAssignee
} from "../../../apiManager/services/FOI/foiAssigneeServices";
import { toast } from "react-toastify";
import { useDispatch } from "react-redux";
import _ from 'lodash';
import ConfirmModal from "../customComponents/ConfirmModal";


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
const MinistryAssignToDropdown  = React.memo(({
  requestState,
  requestDetails,
  ministryAssignedToList,
  handleMinistryAssignedToValue,
  isMinistryCoordinator,
  requestId,
  ministryId,
  setSaveMinistryRequestObject,
  disableInput
}) => {
   
     /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */ 
    const classes = useStyles();
    const dispatch = useDispatch();
    let assigneeDetails = _.pick(requestDetails, ['assignedGroup', 'assignedTo','assignedToFirstName','assignedToLastName',
    'assignedministrygroup','assignedministryperson','assignedministrypersonFirstName','assignedministrypersonLastName']);

    //local state management for assignedTo
    //------- update this later when $567 is ready
    const minsitryAssignedToGroup = assigneeDetails.assignedministrygroup ? assigneeDetails.assignedministrygroup : "";
    const ministryAssignedTo = assigneeDetails.assignedministryperson ? `${minsitryAssignedToGroup}|${assigneeDetails.assignedministryperson}|${assigneeDetails.assignedministrypersonFirstName}|${assigneeDetails.assignedministrypersonLastName}` : `|Unassigned`;
    const [selectedMinistryAssignedTo, setMinistryAssignedTo] = React.useState(ministryAssignedTo);
    const [showModal, setShowModal] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);
    const [assigneeVal, setAssigneeVal]= useState("");
    const [assigneeName,setAssigneeName] = useState("");

    const getFullName = (lastName, firstName, username) => {
         return  firstName !== "" ? `${lastName}, ${firstName}` : username;         
    }
    
    //creates the grouped menu items for assignedTo combobox    
    const getMenuItems = () => {
      let menuItems = [];
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

    const handleAssigneeUpdate = (event) => {
      let AssigneeValue = event?.target?.value;
      let [groupName, username, firstName, lastName] = AssigneeValue.split('|');
      let fullName = firstName !== "" ? `${lastName}, ${firstName}` : username;
      setAssigneeVal(AssigneeValue);
      setAssigneeName(fullName);

      if(isRequestMinistryRestricted(requestDetails)){
        setModalMessage(<span>Are you sure you want to assign <b>{fullName}</b> to this request?</span>);
        setModalDescription(<span><i>This will allow them to have access to this restricted request content.</i></span>);
        setShowModal(true);
      }
      else
        saveAssigneeDetails(AssigneeValue);
    }
    
    const resetModal = () => {
      setShowModal(false);
    }

    const saveAssigneeDetails = (assigneeVal) => {
      //setMinistryAssignedTo(event.target.value);
      setMinistryAssignedTo(assigneeVal);
      assigneeDetails = createAssignedToDetailsObject(assigneeVal);
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
            handleMinistryAssignedToValue(assigneeVal);
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
      <>
            <div className="foi-assigned-to-inner-container">
                <TextField
                    id="ministryAssignedTo"
                    label="Ministry Assigned To"
                    InputLabelProps={{ shrink: true, }}          
                    inputProps={{ "aria-labelledby": "ministryAssignedTo-label"}}
                    select
                    value={selectedMinistryAssignedTo}
                    onChange={handleAssigneeUpdate}
                    input={<Input />} 
                    variant="outlined"
                    fullWidth
                    required = {isMinistryCoordinator && requestState.toLowerCase() == StateEnum.callforrecords.name.toLowerCase() }
                    disabled = {!isMinistryCoordinator || (requestState.toLowerCase() == StateEnum.closed.name.toLowerCase()) || disableInput}
                    error={isMinistryCoordinator && selectedMinistryAssignedTo.toLowerCase().includes("unassigned") }                    
                >            
                    {getMenuItems()}
                </TextField> 
            </div>

            <ConfirmModal 
              modalMessage= {modalMessage}
              modalDescription= {modalDescription} 
              showModal={showModal}
              saveAssigneeDetails = {saveAssigneeDetails}
              assigneeVal={assigneeVal}
              assigneeName ={assigneeName}
              resetModal = {resetModal} />
      </>
    );
  });

export default MinistryAssignToDropdown;