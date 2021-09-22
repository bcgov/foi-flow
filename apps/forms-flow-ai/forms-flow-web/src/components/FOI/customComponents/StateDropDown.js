import React, { useEffect } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';
import { stateList } from '../../../helper/FOI/statusEnum';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

export default function StateDropDown({requestStatus, handleStateChange}) {

    const [status, setStatus] = React.useState(requestStatus);
    useEffect (() => {
        setStatus(requestStatus.toLowerCase().includes("days")? "Open": requestStatus);
    },[requestStatus])
    
    const handleChange = (event) => {
         setStatus(event.target.value);
        handleStateChange(event.target.value); 
    };

    const getStatusList = (_status) => {        
        let  _state =  requestStatus.toLowerCase().includes("days")? "Open": requestStatus;              
        switch(_state.toLowerCase()) {
            case FOI_COMPONENT_CONSTANTS.UNOPENED.toLowerCase(): 
                return stateList.unopened;
            case FOI_COMPONENT_CONSTANTS.INTAKEINPROGRESS.toLowerCase():
                return stateList.intakeinprogress;
            case FOI_COMPONENT_CONSTANTS.OPEN.toLowerCase():
                return stateList.open;
            case FOI_COMPONENT_CONSTANTS.CLOSED.toLowerCase():
                    return stateList.closed; 
            case FOI_COMPONENT_CONSTANTS.REDIRECT.toLowerCase():
                    return stateList.redirect; 
            case FOI_COMPONENT_CONSTANTS.CallFORRECORDS.toLowerCase():
                    return stateList.callforrecords;                    
            default:
                return [];
        }
    }
    
    const statusList = getStatusList(status);    
    const menuItems = statusList.length > 0 && statusList.map((item) => {
        return (        
        <MenuItem className="foi-state-menuitem" key={item.status} value={item.status} disabled={item.status.toLowerCase().includes("unopened")}>
            <span className={`foi-menuitem-span ${item.status.toLowerCase().replace(/\s/g, '')}`} ></span>
            {item.status}
        </MenuItem> 
        )
     });
    return (       
            <TextField
                id="foi-status-dropdown"
                className="foi-state-dropdown"
                InputLabelProps={{ shrink: false, }}          
                select
                value={status}
                onChange={handleChange}
                input={<Input />} 
                variant="outlined"
                fullWidth
            >                
            
                {menuItems}
            </TextField>        
    );
  }