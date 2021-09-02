import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import NativeSelect from '@material-ui/core/NativeSelect';
import './statedropdown.scss';

const useStyles = makeStyles((theme) => ({
    formControl: {
    //   margin: theme.spacing(1),
      minWidth: 120,
    },
    selectEmpty: {
      marginTop: theme.spacing(2),
    },
    unopened: {
        backgroundColor: '#048ba8',
        width: '20px',
        display: 'inline-block'
    }
  }));
export default function StateDropDown({}) {
    const classes = useStyles();
    const [status, setStatus] = React.useState('Unopened');

    const handleChange = (event) => {
        setStatus(event.target.value);
    };
    const stateList = ["Unopened","Intake in progress", "Open", "CFR", "Closed", "Redirect"];
    const menuItems = stateList.map((item) => {
        return (        
        <MenuItem className="foi-state-menuitem" key={item} value={item} disabled={item.toLowerCase().includes("unopened")}>
            <span className={`foi-menuitem-span ${item.toLowerCase().replace(/\s/g, '')}`}></span>
            {item}
        </MenuItem> 
        )
     });
    return (
        // <FormControl variant="outlined" className={classes.formControl}>            
            <Select
                className="foi-state-dropdown"
                labelId="demo-simple-select-outlined-label"
                id="demo-simple-select-outlined"
                value={status}
                onChange={handleChange}
                label="Age" 
                variant="outlined"
                fullWidth
                InputLabelProps={{shrink: false}}           
                >
                {menuItems}
            </Select>
        // </FormControl>
    );
  }