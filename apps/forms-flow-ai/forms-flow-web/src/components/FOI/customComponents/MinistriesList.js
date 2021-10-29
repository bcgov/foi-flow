import React, {useEffect} from 'react';
import "./ministrieslist.scss";
import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';

const useStyles = makeStyles((theme) => ({  
  headingError: {
    color: "#ff0000"    
  },
  headingNormal: {
    color: "000000"
  }
}));

const MinistriesList = React.memo(({masterProgramAreaList, handleUpdatedMasterProgramAreaList, disableInput}) => { 
    const classes = useStyles();
    const {ministryId} = useParams(); 
    const [programAreaList, setProgramAreaListItems] = React.useState(masterProgramAreaList);
    //required field validation error object
    const [isError, setError] = React.useState(false);
    
    //sets the isError to true if no program area selected by default
    useEffect(() => {
      setError(!programAreaList.some(programArea => programArea.isChecked));
    },[programAreaList])

    //handle onChange event of checkbox
    const handleOnChangeProgramArea = (e) => {      
      const newProgramAreaList = [...programAreaList];
      newProgramAreaList.map(programArea => programArea.programareaid.toString() === e.target.dataset.programareaid? programArea.isChecked = e.target.checked: programArea);      
      //sets the program area list with updated values
      setProgramAreaListItems(newProgramAreaList);
      //event bubble up - send the updated list to RequestDescriptionBox component
      handleUpdatedMasterProgramAreaList(newProgramAreaList);
      //updates the isError based on the selection
      setError(!newProgramAreaList.some(ministry => ministry.isChecked));     
    }    
     return (
        <div className="foi-ministries-container">
        <h4 className={isError ? classes.headingError : classes.headingNormal}>Select Ministry Client *</h4>
        <div className = "foi-ministries-checkboxes">
        {       
          programAreaList.map((programArea, index) => 
              
              <label key={index} className="check-item">                  
              <input
                type="checkbox"
                className="checkmark"
                key={programArea.iaocode}
                data-programareaid={programArea.programareaid}
                onChange={handleOnChangeProgramArea}
                checked={programArea.isChecked}
                required
                disabled={!!ministryId || disableInput}
              />
              <span key={index+1} className="checkmark"></span>
            {programArea.iaocode}</label>
          )
        }
        </div>
        </div>
    );
  });

export default MinistriesList;