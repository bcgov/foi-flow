import React, {useEffect} from 'react';

import "./ministrieslist.scss";
import { makeStyles } from '@material-ui/core/styles';
const useStyles = makeStyles((theme) => ({  
  headingError: {
    color: "#ff0000"    
  },
  headingNormal: {
    color: "000000"
  }
}));
const MinistriesList = React.memo(({ministries}) => { 
    const classes = useStyles();
    const [checkboxItems, setCheckboxItems] = React.useState(ministries);
    const [isError, setError] = React.useState(false);
    useEffect(() => {
      setCheckboxItems(ministries);
      var isMatch = ministries.some((checkbox) => {
        return checkbox.isChecked === true;
      });
      setError(!isMatch);
    },[ministries])
    
    const checkSelected = () => {
      var isMatch = checkboxItems.some((checkbox) => {
        return checkbox.isChecked === true;
      });
      setError(!isMatch)
    }
     return (
        <div className="foi-ministries-container">
        <h4 className={isError ? classes.headingError : classes.headingNormal}>Select Ministry Client *</h4>
        <div className = "foi-ministries-checkboxes">
        {       
          checkboxItems.map((checkbox, index) => 
                
              <label key={index} className="check-item">                  
              <input
                type={"checkbox"}
                className="checkmark"
                key={checkbox.iaocode}
                onChange={e => {
                  const newCheckboxes = [...checkboxItems];                 
                  newCheckboxes[index].isChecked = !newCheckboxes[index].isChecked;                  
                  setCheckboxItems(newCheckboxes);
                  checkSelected();
                }}
                checked={checkbox.isChecked}
                required
              />
              <span key={index+1} className="checkmark"></span>
            {checkbox.iaocode}</label>
          )
        }
        </div>
        </div>
    );
  });

export default MinistriesList;