import React, { useEffect } from 'react';
import OutlinedInput from '@material-ui/core/OutlinedInput';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import ListItemText from '@material-ui/core/ListItemText';
import Select from '@material-ui/core/Select';
import Checkbox from '@material-ui/core/Checkbox';
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

export default function Watcher({}) {
    
       
    const names = [
        'Oliver Hansen',
        'Van Henry',
        'April Tucker',
        'Ralph Hubbard',
        'Omar Alexander',
        'Carlos Abbott',
        'Miriam Wagner',
        'Bradley Wilkerson',
        'Virginia Andrews',
        'Kelly Snyder',
      ];
      const [personName, setPersonName] = React.useState([]);
      const [noOfWatchers, setNoOfWatcers] = React.useState(0);

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    console.log(event);
    setNoOfWatcers(value.length)
    // setNoOfWatcers(value.length)
    setPersonName(        
      // On autofill we get a the stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
  };

  const renderValue = (option) => {
    // With more selections, render "N items selected".
    // Other than the first one are hidden in CSS.
    return <span>{noOfWatchers}</span>;
  }
    return (  
        
        <div>
        <FormControl>
          {/* <InputLabel id="demo-multiple-name-label">Name</InputLabel> */}         
          {/* <div className="foi-watcher-container"> */}
              <div className="foi-watcher-all">
                <div className="foi-eye-container">
                    <i className="fa fa-eye foi-eye"> <b>Watcher</b></i>
                </div>
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
                    {names.map((name) => (
                        <MenuItem key={name} value={name}>
                        <Checkbox checked={personName.indexOf(name) > -1} />
                        <ListItemText primary={name} />
                        </MenuItem>
                    ))}
                    </Select>
                </div>
            </div>
        {/* </div> */}
        </FormControl>
      </div> 
           
    );
  }