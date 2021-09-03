import React from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './statedropdown.scss';

export default function StateDropDown({}) {
    const [status, setStatus] = React.useState('Unopened');
    const handleChange = (event) => {
        setStatus(event.target.value);       
    };
    const stateList = ["Unopened","Intake in progress", "Open", "CFR", "Closed", "Redirect"];
    const menuItems = stateList.map((item) => {
        return (        
        <MenuItem className="foi-state-menuitem" key={item} value={item} disabled={item.toLowerCase().includes("unopened")}>
            <span className={`foi-menuitem-span ${item.toLowerCase().replace(/\s/g, '')}`} ></span>
            {item}
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