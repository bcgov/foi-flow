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
import {
  fetchRestrictedRequestCommentTagList
} from "../../../apiManager/services/FOI/foiRequestServices";
import { addToRestrictedRequestTagList } from "../../../helper/FOI/helper";
import _ from 'lodash';


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
  isIAORestrictedRequest,
  setIsLoaded,
  isMinistryRestrictedRequest,
  assigneeDetails,
  requestWatchers
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
    const isFirstRun = React.useRef(true);
    const getCountOfWatchers = (_watcherList) => {
      const watchedByList = requestWatcherList.map(watcher => watcher.watchedby);
      return new Set(watchedByList).size;
    }

    const getFullName = (lastName, firstName, username) => {
      return  firstName !== "" ? `${lastName}, ${firstName}` : username;
    }
    const [userFullName, setUserFullName] = React.useState(getFullName(userDetail.given_name, userDetail.family_name, userDetail.preferred_username));
    const [isrestricted, setIsrestricted] = React.useState(!!(isIAORestrictedRequest || isMinistryRestrictedRequest));
    React.useEffect(() => {
        const watchList = requestWatcherList.map(watcher => {
            return `${watcher.watchedbygroup}|${watcher.watchedby}`;
        });
        const watcherUsers = requestWatcherList.map(watcher => watcher.watchedby);        
        setPersonName(watchList.length > 0 ? watchList : ['Unassigned']);
        setNoOfWatchers(getCountOfWatchers(requestWatcherList));
        setUseraWatcher(!!watcherUsers.find(watcher => watcher === userDetail.preferred_username))
        if (isFirstRun.current)
          isFirstRun.current = false;
        else
          setIsLoaded(true);
        setUserFullName(getFullName(userDetail.given_name, userDetail.family_name, userDetail.preferred_username));
      },[requestWatcherList, userDetail])

    React.useEffect(() => {
      setIsrestricted(!!(isIAORestrictedRequest || isMinistryRestrictedRequest));
    },[isIAORestrictedRequest, isMinistryRestrictedRequest])

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

    const findWatcherFullname = (watcher) => {
      if(watcherFullList && watcherFullList.length > 0) {
        let group = watcherFullList?.find(_group => _group.name === watcher.watchedbygroup)?.members;
        if(group) {
          let member = group.find(_watcher => _watcher.username === watcher.watchedby);
          if(member) {
            return getFullName(member.lastname, member.firstname, member.username);
          }
        }
      }
      return watcher.watchedby;
    }

    const handleWatcherUpdate = (watcher) => {
      watcher.fullname = watcher.fullname ? watcher.fullname : findWatcherFullname(watcher);
      watcher.isrestricted = isrestricted;

      dispatch(saveWatcher(ministryId, watcher, (err, _res) => {
        if(!err) {
          setUpdateWatchList(!updateWatchList);
          if(isIAORestrictedRequest)
            dispatch(fetchRestrictedRequestCommentTagList(requestId, ministryId));
          else if(isMinistryRestrictedRequest)
            addToRestrictedRequestTagList(requestWatchers,assigneeDetails);
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
      if(newPersonName.length > personName.length && isrestricted) {
        let watcherObj = {
          "watchedbygroup": currentWatcher?.split('|')[0],
          "watchedby": currentWatcher?.split('|')[1]
        }
        let newWatcherFullName = findWatcherFullname(watcherObj)
        setModalForCheckBox(true);
        setNewWatcher(currentWatcher);
        setCurrentWatchers(event.target.value);
        setModalMessage(<span>Are you sure you want to assign <b>{newWatcherFullName}</b> as a watcher?</span>);
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
      watcher.fullname = userFullName;
      if (isUseraWatcher) { 
          watcher.isactive = false;
          setUseraWatcher(watcher.isactive);
          handleWatcherUpdate(watcher);
      }
      else {
        watcher.isactive = true;
        if(isrestricted) {
          setModalForCheckBox(false);
          setNewWatcherObj(watcher);
          setModalMessage(<span>Are you sure you want to assign <b>{userFullName}</b> as a watcher?</span>);
          setModalDescription(<span><i>This will allow them to have access to this restricted request content.</i></span>);
          setShowModal(true);
        }
        else {
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
