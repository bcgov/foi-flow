import React, { useEffect } from "react";
import "./ministrieslist.scss";
import { makeStyles } from "@material-ui/core/styles";
import { useParams } from "react-router-dom";
import clsx from "clsx";
import {
  isValidMinistryCode,
  countOfMinistrySelected,
} from "../FOIRequest/utils";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";

const useStyles = makeStyles((_theme) => ({
  headingError: {
    color: "#9e2929",
  },
  headingNormal: {
    color: "000000",
  },
  hideValidation: {
    visibility: "hidden",
  },
  showValidation: {
    color: "#9e2929",
    marginTop: "12px",
  },
}));

const MinistriesList = React.memo(
  ({
    masterProgramAreaList,
    handleUpdatedMasterProgramAreaList,
    disableInput,
    isProactiveDisclosure = false,
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
        countOfMinistrySelected(programAreaList) === 0 ||
        !programAreaList?.some(
          (programArea) =>
            programArea.isChecked &&
            isValidMinistryCode(programArea.bcgovcode, masterProgramAreaList)
        )
      );
    }, [masterProgramAreaList, programAreaList]);

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

    const handleSelectAll = (event) => {
      const newProgramAreaList = [...programAreaList];
      newProgramAreaList.forEach((programArea) => {
        programArea.isChecked = event.target.checked;
      });
      setProgramAreaListItems(newProgramAreaList);
      handleUpdatedMasterProgramAreaList(newProgramAreaList);
    };

    const selectAll = programAreaList?.every((programArea) => programArea.isChecked);
    return (
      <div className="foi-ministries-container">
        {isProactiveDisclosure ? (
          <>
            <h5
              className={clsx({
                [classes.headingError]: isError,
                [classes.headingNormal]: !isError,
              })}
            >
              Select Ministry Client and Public Bodies*
            </h5>
            <h6 className={classes.headingNormal}>
              The ministries displayed have been compiled using data from prior
              proactive disclosures.
            </h6>
          </>
        ) : (
          <h4
            className={clsx({
              [classes.headingError]: isError,
              [classes.headingNormal]: !isError,
            })}
          >
            Select Ministry Client *
          </h4>
        )}
        <FormControlLabel
          control={
            <Checkbox
              checked={selectAll}
              onChange={handleSelectAll}
              className={classes.checkbox}
            />
          }
          label="Select all"
          className={classes.selectAllLabel}
        />
        <div className="foi-ministries-checkboxes">
          {programAreaList?.map((programArea, index) => (
            <label
              id={"lbl" + programArea.iaocode}
              key={index}
              className="check-item"
            >
              <input
                type="checkbox"
                className="checkmark"
                id={"selectchk" + programArea.iaocode}
                key={programArea.iaocode}
                data-programareaid={programArea.programareaid}
                onChange={handleOnChangeProgramArea}
                checked={programArea.isChecked}
                required
                disabled={!!ministryId || disableInput}
              />
              <span
                id={"selectspan" + programArea.iaocode}
                key={index + 1}
                className="checkmark"
              ></span>
              {programArea.iaocode}
            </label>
          ))}
        </div>
        {/* <h5
          className={clsx({
            [classes.showValidation]: countOfMinistry > 1,
            [classes.hideValidation]: countOfMinistry <= 1,
          })}
        >
          * Only Select 1 Ministry Client per request. Please deselect all
          expect 1 and open others as separate requests
        </h5> */}
      </div>
    );
  }
);

export default MinistriesList;
