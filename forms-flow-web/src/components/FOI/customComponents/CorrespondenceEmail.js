import React, { useState } from 'react';
import { useSelector, useDispatch } from "react-redux";
import OutlinedInput from '@material-ui/core/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Checkbox from '@material-ui/core/Checkbox';
import { makeStyles } from '@material-ui/core/styles';
import './CorrespondenceEmail.scss'
import { saveCorrespondenceEmail, fetchCorrespondenceEmailList } from "../../../apiManager/services/FOI/foiCorrespondenceEmailServices";
import _ from 'lodash';
import TextField from "@material-ui/core/TextField";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
     
    },
  },
};

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

export default function CorrespondenceEmail({
  ministryId,
  selectedEmails,
  setSelectedEmails
}) {    
    const classes = useStyles();
    const dispatch = useDispatch();
    const [newCorrespondenceEmail, setNewCorrespondenceEmail] = React.useState();
    const [requestemailList, setRequestemailList] = React.useState([]);    
    const [noOfSelectedEmails, setNoOfSelectedEmails] = React.useState(0);

    React.useEffect(() => {  
      dispatch(
        fetchCorrespondenceEmailList(ministryId, (_err, res) => {
          setRequestemailList(res);
 
        })
      );
    },[ministryId])

    const handleEmailSave = (e) => {
      dispatch(
        saveCorrespondenceEmail(ministryId, {"email": newCorrespondenceEmail}, (_err, res) => {
            setRequestemailList((oldArray) => [...oldArray, {"email": newCorrespondenceEmail}]);
            setNewCorrespondenceEmail(""); 
        })
      );      
    }

    const handleChange = (event) => {
      let currentemail = "";    
      if (event.nativeEvent.target.dataset.value) {
        currentemail = event.nativeEvent.target.dataset.value;
      }
      else if (event.nativeEvent.target.name) {
        currentemail = event.nativeEvent.target.name;
      }
      if (selectedEmails.includes(currentemail)) {
        let filteredArray = selectedEmails.filter(function(e) { return e !== currentemail })
        setSelectedEmails(filteredArray);        
      } else{
        setSelectedEmails((existingEmails) => [...existingEmails, currentemail]);
      }     
      
    };
    
    
    const handleNewCorrespondenceEmailChange = (e) => {
      setNewCorrespondenceEmail(e.target.value);       
    };
    //creates the grouped menu items for assignedTo combobox
    const getMenuItems = () => {
      let menuItems = [];
      let i=1;
      if (requestemailList && requestemailList.length > 0) {
        for (let email of requestemailList) {
              menuItems.push(<MenuItem className={`${classes.item} foi-watcher-menuitem`}  
                key={`${email.email}`}
                value={`${email.email}`}
                divider={i == requestemailList.length} >
                  <Checkbox id='email' inputProps={{'aria-labelledby': 'watcher'}}  
                  name={`${email.email}`} 
                  checked={selectedEmails.indexOf(`${email.email}`) > -1}/>
                   {email.email}
               </MenuItem>);
               i++;
            }
    }
    menuItems.push(<div style={{padding:'0.5em'}}>
    <TextField id="new-email" label="Add New Email Address" variant="outlined" fullWidth
    value={newCorrespondenceEmail}
    onChange={handleNewCorrespondenceEmailChange}
    />
    <div>
    <button className="btn-bottom btn-save" onClick={handleEmailSave}>
            Save
    </button>
    </div>
   </div>);
      return menuItems;
   }

   const renderValue = (_option) => {
    setNoOfSelectedEmails(selectedEmails.length);
    return <span>{noOfSelectedEmails}</span>;
  }

    return (
      <>
      <div>
            <div className="foi-watcher-all">
                <button className="foi-eye-container"> <i className="fa fa-envelope"></i> Email To</button>
                <div className="foi-watcher-select">
                    <i className="fa fa-user-o"></i>                    
                    <InputLabel id="foi-watcher-label">
                      Emails
                    </InputLabel>
                    <Select
                      id="foi-email"
                      className="foi-watcher" 
                      inputProps={{'aria-labelledby': 'foi-watcher-label'}}
                      input={<OutlinedInput label="Tag" />}
                      onChange={handleChange}
                      multiple
                      value={selectedEmails} 
                      renderValue={renderValue} 
                      MenuProps={MenuProps}                     
                    >
                      {getMenuItems()}
                        
                    </Select>  
                </div>
                
            </div>
            
      </div> 

      

      </>
    );
  }
