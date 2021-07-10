import React, {useEffect} from 'react';

import "./ministrieslist.scss";

const MinistriesList = React.memo(({ministries}) => { 
    const [checkboxItems, setCheckboxItems] = React.useState(ministries);
    useEffect(() => {
      setCheckboxItems(ministries);
    },[ministries])
     return (
        <div className="foi-ministries-container">
        <h4>Select Ministry Client *</h4>
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