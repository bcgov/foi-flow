import React, {useEffect} from 'react';
import "./multiministrieslist.scss";
import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';
import clsx from 'clsx'
import {isValidMinistryCode, countOfMinistrySelected} from '../FOIRequest/utils';

const useStyles = makeStyles((_theme) => ({  
  headingError: {
    color: "#9e2929"    
  },
  headingNormal: {
    color: "var(--typography-color-primary, #2D2D2D)",
    fontFamily: "BC Sans", 
    fontSize: "16px",
    fontStyle: "normal", 
    fontWeight: 700, 
    lineHeight: "27.008px",
  },
  hideValidation: {
    visibility: 'hidden'
  },
  showValidation: {
    color: "#9e2929",
    marginTop: '12px',
    fontFamily: "BC Sans",
    fontSize: "12px",
    fontStyle: "italic",
    fontWeight: 400,
    lineHeight: "18px",
  }
}));

const MultiMinistrySelector = React.memo(
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

    //sets the isError to true if no program area selected by default
    useEffect(() => {
      setProgramAreaListItems(masterProgramAreaList);
      setError(
        countOfMinistrySelected(programAreaList) !== 1 || !programAreaList.some((programArea) => (programArea.isChecked && isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList)))
      );
    },[masterProgramAreaList, programAreaList])

    //handle onChange event of checkbox
    const handleOnChangeProgramArea = (e) => {
      const newProgramAreaList = [...programAreaList];
      newProgramAreaList.forEach((programArea) => {
        if (
          programArea.programareaid.toString() ===
          e.target.dataset.programareaid
        ) {
          programArea.isChecked = e.target.checked;
        }
      });
      //sets the program area list with updated values
      setProgramAreaListItems(newProgramAreaList);
      //event bubble up - send the updated list to RequestDescriptionBox component
      handleUpdatedMasterProgramAreaList(newProgramAreaList);
    };

    const countOfMinistry = countOfMinistrySelected(programAreaList);
    return (
      <div className="foi-multi-ministries-container">
        <h5
          className={clsx({
            [classes.headingError]: isError,
            [classes.headingNormal]: !isError,
          })}
        >
          Select Ministry Client(s)*
        </h5>
        <h5
          className={clsx({
            [classes.showValidation]: countOfMinistry > 1,
            [classes.hideValidation]: countOfMinistry <= 1,
          })}
        >
          This information is required
        </h5>
        <div className="foi-ministries-checkboxes">
          {programAreaList.map((programArea, index) => (
            <label  id={"lbl"+programArea.iaocode}  key={index} className="check-item">
              <input
                type="checkbox"
                className="checkmark"
                id={"selectchk"+programArea.iaocode}
                key={programArea.iaocode}
                data-programareaid={programArea.programareaid}
                onChange={handleOnChangeProgramArea}
                checked={programArea.isChecked}
                required
                disabled={!!ministryId || disableInput}
              />
              <span id={"selectspan"+programArea.iaocode} key={index + 1} className="checkmark"></span>
              {programArea.iaocode}
            </label>
          ))}
        </div>
      </div>
    );
  }
);

export default MultiMinistrySelector;