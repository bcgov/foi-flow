import React, { useState } from 'react';
import { useSelector, useDispatch } from "react-redux";
import OutlinedInput from '@material-ui/core/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Checkbox from '@material-ui/core/Checkbox';
import { makeStyles } from '@material-ui/core/styles';
import './Watcher.scss'
import { saveWatcher, fetchFOIWatcherList } from "../../../apiManager/services/FOI/foiWatcherServices";
import ConfirmModalWatcher from "./ConfirmModalWatcher";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
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

export default function Watcher({
  watcherFullList,
  requestId,
  ministryId,
  userDetail,
  disableInput,
  isIAORestrictedRequest
}) {    
    const classes = useStyles();
    const dispatch = useDispatch();

    const [updateWatchList, setUpdateWatchList] = React.useState(false);
    const [isUseraWatcher, setUseraWatcher] = React.useState(false);

    React.useEffect(() => {
        dispatch(fetchFOIWatcherList(requestId,ministryId));
    },[dispatch, updateWatchList, requestId, ministryId] )

    const [personName, setPersonName] = React.useState(['Unassigned']);
    const [noOfWatchers, setNoOfWatchers] = React.useState(0);
    const requestWatcherList = useSelector((state) => state.foiRequests.foiWatcherList);

    const getCountOfWatchers = (_watcherList) => {
      const watchedByList = requestWatcherList.map(watcher => watcher.watchedby);
      return new Set(watchedByList).size;
    }
    React.useEffect(() => {
        const watchList = requestWatcherList.map(watcher => {
            return `${watcher.watchedbygroup}|${watcher.watchedby}`;
        });
        const watcherUsers = requestWatcherList.map(watcher => watcher.watchedby);        
        setPersonName(watchList.length > 0 ? watchList : ['Unassigned']);
        setNoOfWatchers(getCountOfWatchers(requestWatcherList));
        setUseraWatcher(!!watcherUsers.find(watcher => watcher === userDetail.preferred_username))
      },[requestWatcherList, userDetail])

      
    const getFullName = (lastName, firstName, username) => {
        return  firstName !== "" ? `${lastName}, ${firstName}` : username;
    }

    //creates the grouped menu items for assignedTo combobox
    const getMenuItems = () => {
       let menuItems = [];
       let i = 1;      
       if (watcherFullList && watcherFullList.length > 0) {
           for (let group of watcherFullList) {             
               menuItems.push(<MenuItem className={`${classes.item} foi-watcher-menuitem`} disabled={true} key={group.id} value={`${group.name}|${group.name}`}>
                   {group.name}
               </MenuItem>);
               for (let assignee of group.members) {               
                   menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={`${classes.item} foi-watcher-menuitem`} 
                   value={`${group.name}|${assignee.username}`} 
                   disabled={assignee.username.toLowerCase().includes("unassigned")}
                   name={`${group.name}|${assignee.username}`}               
                   >
                        <Checkbox id='watcher' inputProps={{'aria-labelledby': 'watcher'}} checked={personName.indexOf(`${group.name}|${assignee.username}`) > -1} name={`${group.name}|${assignee.username}`} />
                        {getFullName(assignee.lastname, assignee.firstname, assignee.username)}
                    </MenuItem>)
               }
           }
       }
       return menuItems;
    }

    const handleWatcherUpdate = (watcher) => {
      dispatch(saveWatcher(ministryId, watcher, (err, _res) => {
        if(!err) {
          setUpdateWatchList(!updateWatchList);
        }
      }));
    }
   
    const updateWatcher = (currentWatcher, watchers) => {
      let watcher = {};
      if (ministryId) {
        watcher.ministryrequestid = ministryId;
      }
      else {
        watcher.requestid = requestId;
      }
      const watcherDetails = currentWatcher.split('|');
      watcher.watchedbygroup = watcherDetails[0];
      watcher.watchedby = watcherDetails[1];
      const isActive = watchers? !!watchers.find(_watcher => _watcher === currentWatcher): false;
      watcher.isactive = isActive;
      if (watcher.watchedby === userDetail.preferred_username) {
        setUseraWatcher(watcher.isactive);
      }
      handleWatcherUpdate(watcher);
    }

    // watcher modal
    const [modalForCheckBox, setModalForCheckBox] = React.useState(true);
    const [newWatcherObj, setNewWatcherObj] = React.useState({});
    const [showModal, setShowModal] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);
    const [newWatcher, setNewWatcher] = React.useState("");
    const [currentWatchers, setCurrentWatchers] = React.useState(['Unassigned']);
    const resetModal = () => {
      setShowModal(false);
    }

    // watcher list checkboxes
    const handleChange = (event) => {
      const {
        target: { value },
      } = event;
      
      let newPersonName = typeof value === 'string' ? value.split(',') : value;

      let currentWatcher = "";
    
      if (event.nativeEvent.target.dataset.value) {
        currentWatcher = event.nativeEvent.target.dataset.value;
      }
      else if (event.nativeEvent.target.name) {
        currentWatcher = event.nativeEvent.target.name;
      }

      if(newPersonName.length > personName.length && isIAORestrictedRequest) {
        setModalForCheckBox(true);
        setNewWatcher(currentWatcher);
        setCurrentWatchers(event.target.value);
        setModalMessage(<span>Are you sure you want to assign <b>{currentWatcher}</b> as a watcher?</span>);
        setModalDescription(<span><i>This will allow them to have access to this restricted request content.</i></span>);
        setShowModal(true);

      } else {
        setPersonName(
          newPersonName
        );
  
        updateWatcher(currentWatcher, event.target.value);
      }
    };

    const saveChangeCheckbox = (newPersonName, currentWatcher, currentWatchers) => {
      setShowModal(false);
      setPersonName(newPersonName);
      updateWatcher(currentWatcher, currentWatchers);
    }

    // watcher toggle
    const watcherOnChange = (event) => {
      let watcher = {};
      if (ministryId) {
          watcher.ministryrequestid = ministryId;
      }
      else {
          watcher.requestid = requestId;
      }
      watcher.watchedby = userDetail.preferred_username;
      if (isUseraWatcher) { 
          watcher.isactive = false;
          setUseraWatcher(watcher.isactive);
          handleWatcherUpdate(watcher);
      }
      else {
        if(isIAORestrictedRequest) {
          setModalForCheckBox(false);
          setNewWatcherObj(watcher);
          setModalMessage(<span>Are you sure you want to assign <b>{userDetail.preferred_username}</b> as a watcher?</span>);
          setModalDescription(<span><i>This will allow them to have access to this restricted request content.</i></span>);
          setShowModal(true);
        }
        else {
          watcher.isactive = true;
          setUseraWatcher(watcher.isactive);
          handleWatcherUpdate(watcher);
        }
      }

      event.preventDefault();
    }

    const saveChangeButton = (watcher) => {
      setShowModal(false);
      setUseraWatcher(true);
      handleWatcherUpdate(watcher);
    }

    const renderValue = (_option) => {
      return <span>{noOfWatchers}</span>;
    }

    return (
      <>
      <div>
            <div className="foi-watcher-all">
                <button onClick={watcherOnChange} className="foi-eye-container" disabled = {disableInput} > <i className="fa fa-eye foi-eye"></i> {isUseraWatcher? "Unwatch" : "Watch" }</button>
                <div className="foi-watcher-select">
                    <i className="fa fa-user-o"></i>                    
                    <InputLabel id="foi-watcher-label">
                      Watchers
                    </InputLabel>
                    <Select
                    id="foi-watcher"
                    className="foi-watcher"
                    multiple
                    value={personName}
                    onChange={handleChange}
                    inputProps={{'aria-labelledby': 'foi-watcher-label'}}
                    input={<OutlinedInput label="Tag" />}
                    renderValue={renderValue}                    
                    MenuProps={MenuProps}
                    disabled = {disableInput}
                    >
                    {getMenuItems()}
                    </Select>
                </div>
            </div>
      </div> 

      <ConfirmModalWatcher
        modalForCheckBox = {modalForCheckBox}
        modalMessage= {modalMessage}
        modalDescription= {modalDescription} 
        showModal={showModal}
        saveChangeButton = {saveChangeButton}
        saveChangeCheckbox = {saveChangeCheckbox}
        watcherObj={newWatcherObj}
        watcherList ={personName}
        resetModal = {resetModal}
        newWatcher = {newWatcher}
        currentWatchers = {currentWatchers}
         />

      </>
    );
  }
