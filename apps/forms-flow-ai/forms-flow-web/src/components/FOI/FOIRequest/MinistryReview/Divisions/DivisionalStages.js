import React from "react";
import MenuItem from "@material-ui/core/MenuItem";
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
  updateEApproval,
  updateDivisonDate,
  stageForReceivedDateExists,
  stageForDueDateExists
} from "./utils";
import clsx from "clsx";
import FOI_COMPONENT_CONSTANTS from "../../../../../constants/FOI/foiComponentConstants";
import TextField from '@material-ui/core/TextField';
import { formatDate } from "../../../../../helper/FOI/helper";

const DivisionalStages = React.memo(
  ({
    divisionalstages,
    existingDivStages,
    popSelectedDivStages,
    createMinistrySaveRequestObject,
    requestStartDate,
    setHasReceivedDate
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

    const handleEApprovalChange = (e,id) => {
      updateEApproval(e, id, minDivStages, (newStages) => {
        setMinDivStages([...newStages]);
        appendStageIterator([...newStages]);
      });
      createMinistrySaveRequestObject(
        FOI_COMPONENT_CONSTANTS.EAPPROVAL,
        e.target.value,
        e.target.name
      );
    };

    const handleDivisionDateChange = (e,id, dateType) => {
      if(dateType.toLowerCase() == "receiveddate")
        setHasReceivedDate(true);

      updateDivisonDate(e, id, dateType, minDivStages, (newStages) => {
        setMinDivStages([...newStages]);
        appendStageIterator([...newStages]);
      });
      createMinistrySaveRequestObject();
    };


    const getdivisionMenuList = () => {
      let _divisionItems = [];
      _divisionItems.push(
        <MenuItem key={0} name="selectmenuitem" value={-1}>
          <em>Select Division</em>
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

    const isReceivedDateEmpty = () => {
      if(minDivStages?.length > 0){
        const divWithoutReceivedDate = minDivStages?.filter(
          (element) => (stageForReceivedDateExists(divisionstageList, element.stageid) && !element.divisionReceivedDate)
        );
        return divWithoutReceivedDate.length > 0;
      }
      return false;
    }

    const renderMenuItem = (value, menuList, key, emptyMenuItem) => {
      if (value === -1) {
        return emptyMenuItem;
      }
      return menuList?.filter((division) => division[key] === value)[0]?.name;
    };

    const getDivisionalStages = () => {
      var divisionstagesItems = [];
      divisionstagesItems.push(
        <MenuItem key={0} name="selectmenuitem" value={-1}>
          <em>Select Division Stage</em>
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
      if(isReceivedDateEmpty())
        setHasReceivedDate(false);
      else
        setHasReceivedDate(true);
        
      return (
        <div className="row foi-details-row" id={`foi-division-row${_id}`}>
          <div className="col-lg-3 foi-details-col">
            <FormControl
              fullWidth
              error={row.divisionid === -1 && row.stageid !== -1}>
              <InputLabel id="foi-division-dropdown-label">
                Select Divison
              </InputLabel>
              <Select
                labelId="foi-division-dropdown-label"
                className="foi-division-dropdown"
                id="foi-division-dropdown"
                value={row.divisionid || -1}
                inputProps={{ "aria-labelledby": "foi-division-dropdown-label"}}
                input={<OutlinedInput  label="Select Divison" notched />}
                onChange={(e) => handleDivisionChange(e, _id)}
                fullWidth
                renderValue={(value) => {
                  return renderMenuItem(
                    value,
                    divisionList,
                    "divisionid",
                    "Select Division"
                  );
                }}
              >
                {getdivisionMenuList()}
              </Select>
            </FormControl>
          </div>
          <div className="col-lg-3 foi-details-col">
            <FormControl
              fullWidth
              error={row.divisionid !== -1 && row.stageid === -1}>
              <InputLabel id="foi-divisionstage-dropdown-label">
                Select Divison Stage
              </InputLabel>
              <Select
                labelId="foi-divisionstage-dropdown-label"
                className="foi-divisionstage-dropdown"
                id="foi-divisionstage-dropdown"
                value={row.stageid || -1}
                inputProps={{ "aria-labelledby": "foi-divisionstage-dropdown-label"}}
                input={<OutlinedInput label="Select Divison Stage" notched />}
                onChange={(e) => handleDivisionStageChange(e, _id)}
                fullWidth
                renderValue={(value) => {
                  return renderMenuItem(
                    value,
                    divisionstageList,
                    "stageid",
                    "Select Division Stage"
                  );
                }}
              >
                {getDivisionalStages()}
              </Select>
            </FormControl>
          </div>
          {stageForDueDateExists(divisionstageList, row.stageid) && 
            <>
            <div className="col-lg-2 foi-details-col due-date-field">
              <TextField
                style={{marginTop: '0px'}}
                label="E-Apps/Other"
                id="eapps"
                value={row.eApproval}
                onChange={(e) => handleEApprovalChange(e, _id)}
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                fullWidth
                inputProps={{maxLength :12, "aria-label": "eapps-label"}}
              />
            </div>
            <div className="col-lg-3 foi-details-col foi-request-dates due-date-field">
              <TextField  
                  style={{marginTop: '0px'}}
                  id="divisionDueDate"              
                  label="Division Due Date"
                  value={row.divisionDueDate}
                  onChange={(e) => handleDivisionDateChange(e, _id, "dueDate")}
                  type="date"
                  InputLabelProps={{
                  shrink: true,
                  }} 
                  InputProps={{inputProps: { min: formatDate(new Date()), "aria-label": "Division Due Date" } }}
                  variant="outlined"
                  fullWidth
              />  
            </div>
            </>
          }
          {stageForReceivedDateExists(divisionstageList, row.stageid) && 
          <>
          <div className="col-lg-3 foi-details-col foi-request-dates due-date-field">
            <TextField  
                style={{marginTop: '0px'}}
                id="divisionReceivedDate"              
                label="Received Date"
                value={row.divisionReceivedDate}
                onChange={(e) => handleDivisionDateChange(e, _id, "receivedDate")}
                type="date"
                InputLabelProps={{
                shrink: true,
                }} 
                InputProps={{inputProps: { 
                  min: formatDate(requestStartDate), 
                  max: formatDate(new Date()),
                  "aria-label": "Division Received Date" } }}
                variant="outlined"
                fullWidth
                required
                error={row.divisionReceivedDate === undefined || row.divisionReceivedDate === "" || row.divisionReceivedDate === null}
            />  
          </div>
          </>
          }
          <div className="col-lg-1 foi-details-col">
            <i
              className={clsx("fa fa-trash fa-3 foi-bin", {
                hidebin: index === 0 && stageIterator.length === 1,
              })}
              aria-hidden="true"
              onClick={() => deleteMinistryDivision(_id)}
            ></i>
          </div>
        </div>
      );
    };

    return (
      <>
        <div id="divstages" className="divstages">
          {divisionList &&
            divisionstageList &&
            stageIterator.map((item, index) =>
              divisionalStagesRow(item, index)
            )}
        </div>
        {divisionList && divisionList.length > stageIterator.length && (
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
        )}
      </>
    );
  }
);

export default DivisionalStages;
