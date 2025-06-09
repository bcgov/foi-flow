import React, {useEffect} from 'react';
import "./ministrieslist.scss";
import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';
import clsx from 'clsx'
import {isValidMinistryCode, countOfMinistrySelected} from '../FOIRequest/utils';

const useStyles = makeStyles((_theme) => ({  
  headingError: {
    color: "#9e2929"    
  },
  headingNormal: {
    color: "000000"
  },
  hideValidation: {
    visibility: 'hidden'
  },
  showValidation: {
    color: "#9e2929",
    marginTop: '12px'
  },
  showInternalConsultFieldValidation: {
    color: "#CE3E39 !important",
    fontStyle: "italic !important",
    marginTop: "5px",
    fontSize: "13px !important",
  },
  hideInternalConsultFieldValidation: {
    visibility: "hidden !important",
  },
}));

const MinistriesList = React.memo(
  ({
    masterProgramAreaList,
    handleUpdatedMasterProgramAreaList,
    disableInput,
    isMultiSelectMode = false,
    showOnlySelected = false,
    isInternalConsultValidationError = false,
  }) => {
    const classes = useStyles();
    const { ministryId } = useParams();
    const [programAreaList, setProgramAreaListItems] = React.useState(
      masterProgramAreaList
    );
    //required field validation error object
    const [isError, setError] = React.useState(false);
    const [recentlyUncheckedIds, setRecentlyUncheckedIds] = React.useState([]);
    
    //sets the isError to true if no program area selected by default
    useEffect(() => {
      setProgramAreaListItems(masterProgramAreaList);
      if (isMultiSelectMode) {
        // internal consultation mode
        setError(
          !programAreaList.some(
            (programArea) =>
              programArea.isChecked && isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList)
          )
        );
      } else {
      setError(
        countOfMinistrySelected(programAreaList) !== 1 || !programAreaList.some((programArea) => (programArea.isChecked && isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList)))
      );
    }
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

      if (isMultiSelectMode && showOnlySelected) {
        const programAreaId = e.target.dataset.programareaid;
        const checked = e.target.checked;
        if (!checked) {
          setRecentlyUncheckedIds((prev) => {
            if (!prev.includes(programAreaId)) {
              return [...prev, programAreaId];
            }
            return prev;
          });
        } else {
          setRecentlyUncheckedIds((prev) =>
            prev.filter((id) => id !== programAreaId)
          );
        }
      }

    };

    const countOfMinistry = countOfMinistrySelected(programAreaList);

      const visibleList = isMultiSelectMode && showOnlySelected
    ? programAreaList.filter(
        pa => pa.isChecked || recentlyUncheckedIds.includes(pa.programareaid.toString())
      )
    : programAreaList;


    const getHeadingText = (isMultiSelectMode, showOnlySelected) => {
      if (isMultiSelectMode && showOnlySelected) {
        return null;
      }
      if (isMultiSelectMode) {
        return "Select Ministry Client(s)*";
      }
      return "Select Ministry Client *";
    };
    return (
      <div className="foi-ministries-container">
        <h4
          className={clsx({
            [classes.headingError]: isError,
            [classes.headingNormal]: !isError,
            "heading-bold": isMultiSelectMode,
            "heading-normal": !isMultiSelectMode, 
          })}
        >
          {getHeadingText(isMultiSelectMode, showOnlySelected)}
        </h4>
        {isMultiSelectMode && !showOnlySelected && (
        <h5
            className={clsx({
              [classes.showInternalConsultFieldValidation]: isInternalConsultValidationError,
              [classes.hideInternalConsultFieldValidation]: !isInternalConsultValidationError,
            })}
        >
          This information is required
        </h5>
        )}
        
        {isMultiSelectMode ? (
        <div className="foi-ministries-checkboxes">
          {visibleList.map((programArea, index) => (
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
                disabled={!isMultiSelectMode && (!!ministryId || disableInput)}
              />
              <span id={"selectspan"+programArea.iaocode} key={index + 1} className={clsx("checkmark", { "multi-select-mode": isMultiSelectMode })}></span>
              {programArea.iaocode}
            </label>
          ))}
        </div>
        ) : (
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
              <span id={"selectspan"+programArea.iaocode} key={index + 1} className={clsx("checkmark", { "multi-select-mode": isMultiSelectMode })}></span>
              {programArea.iaocode}
            </label>
          ))}
        </div>
        )}
        {!isMultiSelectMode && (
        <h5
          className={clsx({
            [classes.showValidation]: countOfMinistry > 1,
            [classes.hideValidation]: countOfMinistry <= 1,
          })}
        >
          * Only Select 1 Ministry Client per request. Please deselect all expect 1 and open others as separate requests
        </h5>
        )}
      </div>
    );
  }
);

export default MinistriesList;