import React from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import InputLabel from "@mui/material/InputLabel";
import OutlinedInput from "@mui/material/OutlinedInput";
import "./divisionstages.scss";
import {
  calculateStageCounter,
  updateDivisions,
  updateDivisionsState,
  addDivisionalStage,
} from "./utils";
import clsx from "clsx";
import FOI_COMPONENT_CONSTANTS from "../../../../../constants/FOI/foiComponentConstants";

const DivisionalStages = React.memo(
  ({
    divisionalstages,
    existingDivStages,
    popSelectedDivStages,
    createMinistrySaveRequestObject,
  }) => {
    const [minDivStages, setMinDivStages] = React.useState(() =>
      calculateStageCounter(existingDivStages)
    );

    const handleDivisionChange = (e, id) => {
      updateDivisions(e, id, minDivStages, (newStages) => {
        setMinDivStages([...newStages]);
        appendStageIterator([...newStages]);
      });
      createMinistrySaveRequestObject(
        FOI_COMPONENT_CONSTANTS.DIVISION,
        e.target.value,
        e.target.name
      );
    };

    const handleDivisionStageChange = (e, id) => {
      updateDivisionsState(e, id, minDivStages, (newStages) => {
        setMinDivStages([...newStages]);
        appendStageIterator([...newStages]);
      });
      createMinistrySaveRequestObject(
        FOI_COMPONENT_CONSTANTS.DIVISION_STAGE,
        e.target.value,
        e.target.name
      );
    };

    popSelectedDivStages(minDivStages);

    const deleteMinistryDivision = (id) => {
      let existing = stageIterator;
      let updatedIterator = existing.filter((i) => i.id !== id);

      setMinDivStages([...updatedIterator]);
      appendStageIterator([...updatedIterator]);
      createMinistrySaveRequestObject(FOI_COMPONENT_CONSTANTS.DIVISION, "", "");
    };

    const [stageIterator, appendStageIterator] = React.useState(() =>
      calculateStageCounter(existingDivStages)
    );

    const handleAddDivisionalStage = (e) => {
      e.preventDefault();
      addDivisionalStage(stageIterator, divisionList, (newStages) => {
        setMinDivStages([...newStages]);
        appendStageIterator([...newStages]);
      });
      createMinistrySaveRequestObject(
        FOI_COMPONENT_CONSTANTS.DIVISION_STAGE,
        "",
        ""
      );
    };

    const divisionList = divisionalstages.divisions;

    const getdivisionMenuList = () => {
      let _divisionItems = [];
      _divisionItems.push(
        <MenuItem key={0} name="selectmenuitem" value={-1}>
          <em>None</em>
        </MenuItem>
      );

      const divisionItems =
        divisionList &&
        divisionList.map((item) => {
          let _mindivtem = minDivStages.filter(
            (d) => d.divisionid === item.divisionid
          );
          return (
            <MenuItem
              disabled={_mindivtem.length > 0}
              className="foi-division-menuitem"
              key={item.divisionid}
              value={item.divisionid}
            >
              <span
                className={`foi-menuitem-span ${item.name
                  .toLowerCase()
                  .replace(/\s/g, "")}`}
              ></span>
              {item.name}
            </MenuItem>
          );
        });
      _divisionItems.push(divisionItems);
      return _divisionItems;
    };

    const divisionstageList = divisionalstages.stages;

    const getDivisionalStages = () => {
      var divisionstagesItems = [];
      divisionstagesItems.push(
        <MenuItem key={0} name="selectmenuitem" value={-1}>
          <em>None</em>
        </MenuItem>
      );

      const divisionstageItems =
        divisionstageList &&
        divisionstageList.map((item) => {
          return (
            <MenuItem
              className="foi-divisionstage-menuitem"
              key={item.stageid}
              value={item.stageid}
            >
              <span
                className={`foi-menuitem-span ${item.name
                  .toLowerCase()
                  .replace(/\s/g, "")}`}
              ></span>
              {item.name}
            </MenuItem>
          );
        });

      divisionstagesItems.push(divisionstageItems);

      return divisionstagesItems;
    };

    const divisionalStagesRow = (row, index) => {
      let _id = row.id;

      return (
        <div className="row foi-details-row" id={`foi-division-row${_id}`}>
          <div className="col-lg-5 foi-details-col">
            <FormControl
              fullWidth
              error={row.divisionid === -1 && row.stageid !== -1}
            >
              <InputLabel id="foi-division-dropdown-label">
                Select Divison*
              </InputLabel>
              <Select
                labelId="foi-division-dropdown-label"
                className="foi-division-dropdown"
                id="foi-division-dropdown"
                value={row.divisionid || -1}
                input={<OutlinedInput label="Select Divison*" notched />}
                onChange={(e) => handleDivisionChange(e, _id)}
                fullWidth
                renderValue={(value) => {
                  if (value === -1) {
                    return "Select Devision";
                  }
                  return (
                    divisionList?.filter(
                      (division) => division.divisionid === value
                    )[0]?.name || "Select Devision"
                  );
                }}
              >
                {getdivisionMenuList()}
              </Select>
            </FormControl>
          </div>
          <div className="col-lg-5 foi-details-col">
            <FormControl
              fullWidth
              error={row.divisionid !== -1 && row.stageid === -1}
            >
              <InputLabel id="foi-divisionstage-dropdown-label">
                Select Divison Stage*
              </InputLabel>
              <Select
                labelId="foi-divisionstage-dropdown-label"
                className="foi-divisionstage-dropdown"
                id="foi-divisionstage-dropdown"
                value={row.stageid || -1}
                input={<OutlinedInput label="Select Divison Stage*" notched />}
                onChange={(e) => handleDivisionStageChange(e, _id)}
                fullWidth
                renderValue={(value) => {
                  if (value === -1) {
                    return "Select Devision Stage";
                  }
                  return (
                    divisionList?.filter(
                      (division) => division.stageid === value
                    )[0]?.name || "Select Devision Stage"
                  );
                }}
              >
                {getDivisionalStages()}
              </Select>
            </FormControl>
          </div>
          <div className="col-lg-2 foi-details-col">
            <i
              className={clsx("fa fa-trash fa-3 foi-bin", {
                hidebin: index === 0 && stageIterator.length === 1,
              })}
              aria-hidden="true"
              onClick={(e) => deleteMinistryDivision(_id)}
            ></i>
          </div>
        </div>
      );
    };

    return (
      <>
        <div id="divstages">
          {divisionList &&
            divisionstageList &&
            stageIterator.map((item, index) =>
              divisionalStagesRow(item, index)
            )}
        </div>
        {divisionList && divisionList.length > stageIterator.length ? (
          <div className="row foi-details-row">
            <div className="col-lg-7 foi-details-col">
              <i
                className="fa fa-plus-circle fa-3 foi-add"
                aria-hidden="true"
              ></i>
              <button
                className="btn btn-link foi-add-division"
                onClick={handleAddDivisionalStage}
              >
                Add division to track
              </button>
            </div>
          </div>
        ) : (
          <span />
        )}
      </>
    );
  }
);

export default DivisionalStages