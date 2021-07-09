import React from 'react';
import "./ministrieslist.scss";

const MinistriesList = React.memo((props) => { 
    const ministries = [
        {name: 'AED', shortName:'AED', isChecked: true},
        {name: 'AGR', shortName:'AGR', isChecked: false},
        {name: 'CFD', shortName:'CTZ', isChecked: false},
        {name: 'EDU', shortName:'EDU', isChecked: false},
        {name: 'EML', shortName:'EML', isChecked: false},
        {name: 'FIN', shortName:'FIN', isChecked: false},
        {name: 'FNR', shortName:'AED', isChecked: false},
        {name: 'HTH', shortName:'AED', isChecked: false},
        {name: 'IRR', shortName:'AED', isChecked: false},
        {name: 'JER', shortName:'AED', isChecked: false},
        {name: 'LBR', shortName:'AED', isChecked: false},
        {name: 'MAG', shortName:'AED', isChecked: false},
        {name: 'MHA', shortName:'AED', isChecked: false},
        {name: 'MMA', shortName:'AED', isChecked: false},
        {name: 'MOE', shortName:'AED', isChecked: false},
        {name: 'MSD', shortName:'AED', isChecked: false},
        {name: 'PSS', shortName:'AED', isChecked: false},
        {name: 'TAC', shortName:'AED', isChecked: false},
        {name: 'TRA', shortName:'AED', isChecked: false},

        {name: 'BRD', shortName:'AED', isChecked: false},
        {name: 'CLB', shortName:'AED', isChecked: false},
        {name: 'EMB', shortName:'AED', isChecked: false},
        {name: 'GCP', shortName:'AED', isChecked: false},
        {name: 'IIO', shortName:'AED', isChecked: false},
        {name: 'EAO', shortName:'AED', isChecked: false},
        {name: 'LBD', shortName:'AED', isChecked: false},
        {name: 'OCC', shortName:'AED', isChecked: false},
        {name: 'OOP', shortName:'AED', isChecked: false},
        {name: 'PSA', shortName:'AED', isChecked: false},
        {name: 'TIC', shortName:'AED', isChecked: false},   
    ]
    const [checkboxItems, setCheckboxItems] = React.useState(ministries);
    
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
                key={checkbox.name}
                onChange={e => {
                  const newCheckboxes = [...checkboxItems];                 
                  newCheckboxes[index].isChecked = !newCheckboxes[index].isChecked;                  
                  setCheckboxItems(newCheckboxes);
                }}
                checked={checkbox.isChecked}
              />
              <span key={index+1} className="checkmark"></span>
            {checkbox.name}</label>
          )
        }
        </div>
        </div>
    );
  });

export default MinistriesList;