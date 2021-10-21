import React  from 'react';
import { useSelector, useDispatch } from "react-redux";
import OutlinedInput from '@material-ui/core/OutlinedInput';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Checkbox from '@material-ui/core/Checkbox';
import { makeStyles } from '@material-ui/core/styles';
import './Watcher.scss'
import { saveWatcher, fetchFOIWatcherList } from "../../../apiManager/services/FOI/foiRequestServices";

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

export default function Watcher({watcherFullList, requestId, ministryId, userDetail}) {    
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

    React.useEffect(() => {
        const watchList = requestWatcherList.map(watcher => {
            return `${watcher.watchedbygroup}|${watcher.watchedby}`;
        });
        const watcherUsers = requestWatcherList.map(watcher => watcher.watchedby);        
        setPersonName(watchList.length > 0 ? watchList : ['Unassigned']);
        setNoOfWatchers(watchList.length > 0 ? watchList.length : 0);        
        setUseraWatcher(!!watcherUsers.find(watcher => watcher === userDetail.preferred_username))
      },[requestWatcherList, userDetail])

      
    const getFullName = (lastName, firstName, username) => {
        return  firstName !== "" ? `${lastName}, ${firstName}` : username;
    }

   //creates the grouped menu items for assignedTo combobox
   const getMenuItems = () => {
       var menuItems = [];
       var i = 1;      
       if (watcherFullList && watcherFullList.length > 0) {
           for (var group of watcherFullList) {             
               menuItems.push(<MenuItem className={`${classes.item} foi-watcher-menuitem`} disabled={true} key={group.id} value={`${group.name}|${group.name}`}>
                   {group.name}
               </MenuItem>);
               for (var assignee of group.members) {               
                   menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={`${classes.item} foi-watcher-menuitem`} 
                   value={`${group.name}|${assignee.username}`} 
                   disabled={assignee.username.toLowerCase().includes("unassigned")}
                   name={`${group.name}|${assignee.username}`}               
                   >
                        <Checkbox checked={personName.indexOf(`${group.name}|${assignee.username}`) > -1} name={`${group.name}|${assignee.username}`} />
                        {getFullName(assignee.lastname, assignee.firstname, assignee.username)}
                    </MenuItem>)
               }
           }
       }
       return menuItems;
   }

  const handleWatcherUpdate = (watcher) => {
    dispatch(saveWatcher(ministryId, watcher, (err, res) => {
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

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    let count = value.length;    
    if (value.includes('Unassigned')) {
        count = count - 1;
    }
    setNoOfWatchers(count);
    setPersonName(
      typeof value === 'string' ? value.split(',') : value,
    );

    let currentWatcher = "";
   
    if (event.nativeEvent.target.dataset.value) {
      currentWatcher = event.nativeEvent.target.dataset.value;     
    }
    else if (event.nativeEvent.target.name) {
      currentWatcher = event.nativeEvent.target.name;
    }
    
    updateWatcher(currentWatcher, event.target.value);
  };

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
        }
        else {
            watcher.isactive = true;
        }
        setUseraWatcher(watcher.isactive);
        handleWatcherUpdate(watcher);
        event.preventDefault();
}

  const renderValue = (option) => {
    return <span>{noOfWatchers}</span>;
  }
    return (  
        
        <div>
              <div className="foi-watcher-all">
                   <button onClick={watcherOnChange} className="foi-eye-container"> <i className="fa fa-eye foi-eye"></i> {isUseraWatcher? "Unwatch" : "Watch" }</button>
                <div className="foi-watcher-select">
                    <i className="fa fa-user-o"></i>
                    <Select
                    labelId="demo-multiple-checkbox-label"
                    id="foi-watcher"
                    className="foi-watcher"
                    multiple
                    value={personName}
                    onChange={handleChange}
                    input={<OutlinedInput label="Tag" />}
                    renderValue={renderValue}                    
                    MenuProps={MenuProps}
                    >
                    {getMenuItems()}
                    </Select>
                </div>
            </div>
      </div> 
           
    );
  }
