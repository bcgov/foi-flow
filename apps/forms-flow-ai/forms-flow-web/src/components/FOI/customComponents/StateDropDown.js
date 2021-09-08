import React, { useEffect } from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';
import { stateList } from '../../../helper/FOI/statusEnum';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

export default function StateDropDown({requestStatus}) {

    const [status, setStatus] = React.useState(requestStatus);
    useEffect (() => {
        setStatus(requestStatus.toLowerCase().includes("days")? "Open": requestStatus);
    },[requestStatus])
    const handleChange = (event) => {
        setStatus(event.target.value);       
    };

    const getStatusList = (_status) => {        
        _status = _status.toLowerCase().includes("days")? "Open": _status;
        switch(_status) {
            case FOI_COMPONENT_CONSTANTS.UNOPENED: 
                return stateList.unopened;
            case FOI_COMPONENT_CONSTANTS.INTAKEINPROGRESS:
                return stateList.intakeinprogress;
            case FOI_COMPONENT_CONSTANTS.OPEN:
                return stateList.open;
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
        // <FormControl variant="outlined" className={classes.formControl}>
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
        // </FormControl>
    );
  }