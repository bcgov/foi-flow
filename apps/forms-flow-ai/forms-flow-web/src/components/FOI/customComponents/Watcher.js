import React  from 'react';
// import { useDispatch } from "react-redux";
import OutlinedInput from '@material-ui/core/OutlinedInput';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import ListItemText from '@material-ui/core/ListItemText';
import Select from '@material-ui/core/Select';
import Checkbox from '@material-ui/core/Checkbox';
import { makeStyles } from '@material-ui/core/styles';
import './Watcher.scss'

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

export default function Watcher({watcherFullList, requestWatcherList, requestId, ministryId, handleWatcherUpdate, userDetail}) {    
    const classes = useStyles();
   
    const [personName, setPersonName] = React.useState(['Unassigned']);
    const [noOfWatchers, setNoOfWatcers] = React.useState(0);
    const [isUseraWatcher, setUseraWatcher] = React.useState(false);

    React.useEffect(() => {
        const watchList = requestWatcherList.map(watcher => {
            return `${watcher.watchedbygroup}|${watcher.watchedby}`;
        });
        const watcherUsers = requestWatcherList.map(watcher => watcher.watchedby);        
        setPersonName(watchList.length > 0 ? watchList : ['Unassigned']);
        setNoOfWatcers(watchList.length > 0 ? watchList.length : 0);
        setUseraWatcher(!!watcherUsers.find(watcher => watcher === userDetail.preferred_username))
      },[requestWatcherList])

      
    const getFullName = (lastName, firstName, username) => {
        return  firstName !== "" ? `${lastName}, ${firstName}` : username;
   }  
   
   //creates the grouped menu items for assignedTo combobox
   const getMenuItems = () => {
       var menuItems = [];
       var i = 1;      
       if (watcherFullList && watcherFullList.length > 0) {
           for (var group of watcherFullList) {             
               menuItems.push(<MenuItem className={classes.item} disabled={true} key={group.id} value={`${group.name}|${group.name}`}>
                   {group.name}
               </MenuItem>);
               for (var assignee of group.members) {               
                   menuItems.push(<MenuItem key={`${assignee.id}${i++}`} className={classes.item} value={`${group.name}|${assignee.username}`} disabled={assignee.username.toLowerCase().includes("unassigned")}>
                        <Checkbox checked={personName.indexOf(`${group.name}|${assignee.username}`) > -1} name={`${group.name}|${assignee.username}`} onChange={updateWatcher} />
                        <ListItemText primary={getFullName(assignee.lastname, assignee.firstname, assignee.username)} />
                       </MenuItem>)
               }
           }
       }
       return menuItems;
   }

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    let count = value.length;

    if (value.includes('Unassigned')) {
        count = count - 1;
    }
    setNoOfWatcers(count);
    setPersonName(
      typeof value === 'string' ? value.split(',') : value,
    );
  };

  const updateWatcher = (event) => {    
    let watcher = {};
    if (ministryId) {
        watcher.ministryrequestid = ministryId;
    }
    else {
        watcher.requestid = requestId;
    }    
    if (event.target.name) {
        const watcherDetails = event.target.name.split('|');
        watcher.watchedbygroup = watcherDetails[0];
        watcher.watchedby = watcherDetails[1];
        watcher.isactive = event.target.checked;
    }
    else {
        watcher.watchedby = userDetail.preferred_username;
        if (isUseraWatcher) { 
            watcher.isactive = false;
        }
        else {
            watcher.isactive = true;
        }
        console.log(`watcher`);
        console.log(watcher);
    }
    handleWatcherUpdate(watcher);
}

  const renderValue = (option) => {    
    return <span>{noOfWatchers}</span>;
  }
    return (  
        
        <div>
        <FormControl>
              <div className="foi-watcher-all">
                {/* <div className="foi-eye-container"> */}
                   <button onClick={updateWatcher} className="foi-eye-container"> <i className="fa fa-eye foi-eye"> <b>{isUseraWatcher? "Unwatch" : "Watch" }</b></i></button>
                {/* </div> */}
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
        </FormControl>
      </div> 
           
    );
  }