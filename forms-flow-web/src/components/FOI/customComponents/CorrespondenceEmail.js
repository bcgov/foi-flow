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
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlusCircle } from '@fortawesome/free-solid-svg-icons';



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
  requestId,
  selectedEmails,
  setSelectedEmails,
  defaultEmail
}) {   
  
    
    const classes = useStyles();
    const dispatch = useDispatch();
    const [newCorrespondenceEmail, setNewCorrespondenceEmail] = React.useState();
    const [requestemailList, setRequestemailList] = React.useState([]);    
    const [noOfSelectedEmails, setNoOfSelectedEmails] = React.useState(0);
    const [showAddEmail, setShowAddEmail] = React.useState(false);

    React.useEffect(() => {  
      dispatch(
        fetchCorrespondenceEmailList(ministryId, requestId, (_err, res) => {
          setRequestemailList( [{"email": defaultEmail}, ...res]);
        })
      );  
    },[ministryId, defaultEmail, dispatch])

    const isEmailPresent = (email) => {
      let hasMatch =false;
      for (let requestemail of requestemailList) {      
        if(requestemail.email === email){
         hasMatch = true;
         break;
       }
      }
      return hasMatch;
    }

    const handleEmailSave = (e) => {
      if (newCorrespondenceEmail && !isEmailPresent(newCorrespondenceEmail)) {
      dispatch(
        saveCorrespondenceEmail(ministryId, requestId, {"email": newCorrespondenceEmail}, (_err, res) => {
            setRequestemailList((oldArray) => [...oldArray, {"email": newCorrespondenceEmail}]);
            setNewCorrespondenceEmail(""); 
        })
      );
      handleChange()
      }
    }

    const handleChange = (event) => {
      let currentemail = "";    
      if(!!event){
        if (event.nativeEvent.target.dataset.value) {
          currentemail = event.nativeEvent.target.dataset.value;
        }
        else if (event.nativeEvent.target.name) {
          currentemail = event.nativeEvent.target.name;
        }
      }
      else{
        //console.log("newCorrespondenceEmail:",newCorrespondenceEmail)
        currentemail = newCorrespondenceEmail
      }
      if (selectedEmails.includes(currentemail)) {
        let filteredArray = selectedEmails.filter(function(e) { return e !== currentemail })
        setSelectedEmails(filteredArray);        
      } else{
        setSelectedEmails((existingEmails) => {
          if (currentemail.length > 0) return [...existingEmails, currentemail]
          return [...existingEmails]
        });
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
    if (showAddEmail) {
      menuItems.push(<div style={{padding:'0.5em'}}>
        <TextField id="new-email" label="Add New Email Address" variant="outlined" fullWidth
        value={newCorrespondenceEmail} onChange={handleNewCorrespondenceEmailChange}
        onKeyDown={(e) => {e.stopPropagation();}} onKeyUp={(e) => {e.stopPropagation();}}
        />
        <div>
        <button className="btn-bottom btn-save" onClick={handleEmailSave} disabled={!newCorrespondenceEmail || isEmailPresent(newCorrespondenceEmail)}>
                Save
        </button>
        <button className="btn-cancel" onClick={() => setShowAddEmail(false)} >
                Cancel
        </button>
        </div>
       </div>);
    } else {
      menuItems.push(
        <MenuItem className={`${classes.item} foi-watcher-menuitem`}  
          key={`add-email`}
          value={`add-email`}
          onClick={() => setShowAddEmail(true)}>
          <span style={{padding: '0.3em'}}
          ><FontAwesomeIcon
            icon={faPlusCircle}
            size="2x"
            color='#385989'
          /></span>
          <span style={{color: "#385989", fontWeight: 'bolder', paddingLeft: '.2em'}}>Add Email Address</span>
        </MenuItem>
      )
    }
      return menuItems;
   }

   const renderValue = (_option) => {
    setNoOfSelectedEmails(selectedEmails.length);
    return <span>{noOfSelectedEmails}</span>;
  }

    return (
      <>
      <div>
            <div className="foi-email-all">
                <button className="foi-eye-container email-correspondence-button"> <i className="fa fa-envelope"></i> Email To</button>
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
