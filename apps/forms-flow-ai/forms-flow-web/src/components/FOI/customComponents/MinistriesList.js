import React, {useEffect} from 'react';
import "./ministrieslist.scss";
import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';
import clsx from 'clsx'

const useStyles = makeStyles((_theme) => ({  
  headingError: {
    color: "#9e2929"    
  },
  headingNormal: {
    color: "000000"
  }
}));

const MinistriesList = React.memo(
  ({
    masterProgramAreaList,
    handleUpdatedMasterProgramAreaList,
    disableInput,
  }) => {
    const classes = useStyles();
    const { ministryId } = useParams();
    const [programAreaList, setProgramAreaListItems] = React.useState(
      masterProgramAreaList
    );
    //required field validation error object
    const [isError, setError] = React.useState(false);
    const [disable, setDisable]= React.useState(false);

    //sets the isError to true if no program area selected by default
    useEffect(() => {
      setProgramAreaListItems(masterProgramAreaList);
      setError(
        !programAreaList.some((programArea) => programArea.isChecked)
      );
    },[masterProgramAreaList, programAreaList])

    //handle onChange event of checkbox
    const handleOnChangeProgramArea = (e) => {
      e.preventDefault();
      console.log("e.target",e.target);
      console.log("e.target.dataset",e.target.dataset);
      const newProgramAreaList = [...programAreaList];
      newProgramAreaList.forEach((programArea) => {
        if (programArea.programareaid.toString() === e.target.dataset.programareaid) {
          programArea.isChecked = true;
        }
      });
      //sets the program area list with updated values
      setProgramAreaListItems(newProgramAreaList);
      //event bubble up - send the updated list to RequestDescriptionBox component
      handleUpdatedMasterProgramAreaList(newProgramAreaList);
      console.log("newProgramAreaList",newProgramAreaList);
    };

    // const disableCheckBox = (checked) => {
    //   console.log("checked",checked);
    //   setDisable(!!(!checked && Object.values(programAreaList).filter((element) => element.isChecked === true)?.length >= 1));
    // }


    return (
      <div className="foi-ministries-container">
        <h4
          className={clsx({
            [classes.headingError]: isError,
            [classes.headingNormal]: !isError,
          })}
        >
          Select Ministry Client *
        </h4>
        <div className="foi-ministries-checkboxes">
          {programAreaList.map((programArea, index) => (
            <label key={index} className="check-item">
              <input
                type="radio"
                className="checkmark"
                name="ministry-select"
                key={programArea.iaocode}
                data-programareaid={programArea.programareaid}
                onChange={handleOnChangeProgramArea}
                checked={programArea.isChecked}
                required
                disabled={!!ministryId || disableInput}
              />
              <span key={index + 1} className="checkmark"></span>
              {programArea.iaocode}
            </label>
          ))}
        </div>
      </div>
    );
  }
);

export default MinistriesList;