import React, { useState } from "react";
import { useSelector } from "react-redux";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import InputLabel from "@mui/material/InputLabel";
import OutlinedInput from "@mui/material/OutlinedInput";
import Autocomplete from "@mui/material/Autocomplete";
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
import ConfirmModalDivision from "./ConfirmModalDivision";

const DivisionalStages = React.memo(
  ({
    divisionalstages,
    existingDivStages,
    popSelectedDivStages,
    createMinistrySaveRequestObject,
    requestStartDate,
    setHasReceivedDate
  }) => {

    const today = new Date();
    const [showModal, setShowModal] = useState(false);
    const [modalName, setmodalName] = useState(<></>); 
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);  

    let requestRecords = useSelector(
      (state) => state.foiRequests.foiRequestRecords
    );

    const [minDivStages, setMinDivStages] = React.useState(() =>
      calculateStageCounter(existingDivStages)
    );

    const handleDivisionChange = (newValue, id, divisionid) => {
      let ismatchfound = checkRecordAssociation(divisionid);
      if (ismatchfound === true) {
          setmodalName(<span>Changing Divisions</span>);
          setModalMessage(<span>You cannot change this division at this time.</span>);
          setModalDescription(<span><i>All associated records must be removed from the Records Log prior to you being able to change a division in order to ensure the Records Package is accurate.</i></span>);
          setShowModal(true);   
      } else {
          updateDivisions(newValue, id, minDivStages, (newStages) => {
            setMinDivStages([...newStages]);
            appendStageIterator([...newStages]);
          });
          createMinistrySaveRequestObject(
            FOI_COMPONENT_CONSTANTS.DIVISION,
            newValue.divisionid,
            newValue.label
          );
      }
    };


    const handleDivisionStageChange = (newValue, id, ) => {
        updateDivisionsState(newValue, id, minDivStages, (newStages) => {
          setMinDivStages([...newStages]);
          appendStageIterator([...newStages]);
          });
        createMinistrySaveRequestObject(
              FOI_COMPONENT_CONSTANTS.DIVISION_STAGE,
              newValue.stageid,
              newValue.label
            );
    };

    popSelectedDivStages(minDivStages);

    const deleteMinistryDivision = (id, divisionid) => {
      let existing = stageIterator;
      let ismatchfound = checkRecordAssociation(divisionid);      
      if (ismatchfound === true) {
          setmodalName(<span>Deleting Divisions</span>);
          setModalMessage(<span>You cannot delete this division at this time.</span>);
          setModalDescription(<span><i>All associated records must be removed from the Records Log prior to you being able to delete a division in order to ensure the Records Package is accurate.</i></span>);
          setShowModal(true);   
      }  else {
          let updatedIterator = existing.filter((i) => i.id !== id);
          setMinDivStages([...updatedIterator]);
          appendStageIterator([...updatedIterator]);
          createMinistrySaveRequestObject(FOI_COMPONENT_CONSTANTS.DIVISION, "", "");
      }    
    };

    const checkRecordAssociation = (divisionid) => {
      let ismatchfound = false;
      requestRecords.records.forEach(element => {
        element.attributes.divisions.forEach(division => {
            if(division.divisionid == divisionid) {
              if (ismatchfound === false) { ismatchfound = true;}                          
            }
        });
      }); 
      return ismatchfound
    };

    const resetModal = () => {
      setShowModal(false);
    }

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
    const divisionItems = [{label: "Select Division", divisionid: -1}].concat(divisionList.map(d=> ({label: d.name, divisionid: d.divisionid})))


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


    const divisionstageList = [{name: "Select Division Stage", label: "Select Division Stage", stageid: -1}].concat(divisionalstages.stages.map(d=> ({name: d.name, label: d.name, stageid: d.stageid})));

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
              <Autocomplete
                className="foi-division-dropdown"
                disableClearable
                onChange={(e, newValue) => handleDivisionChange(newValue, _id, row.divisionid)}
                value={row.divisionid > 0 ? {label: row.divisionname, divisionid: row.divisionid} : {label: "Select Division", divisionid: -1}}
                disablePortal
                options={divisionItems}
                getOptionDisabled={option => existingDivStages.findIndex(d => d.divisionid === option.divisionid) > -1 || option.divisionid === -1}
                isOptionEqualToValue={(option, value) => (option.divisionid === value.divisionid)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Division"
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    error={row.divisionid === -1 && row.stageid !== -1}
                    style={{color: "black"}}
                  />
                )}
              />
          </div>
          <div className="col-lg-3 foi-details-col">
            <Autocomplete
              className="foi-division-dropdown"
              disableClearable
              onChange={(e, newValue) => handleDivisionStageChange(newValue, _id, row.stageid)}
              value={row.stageid > 0 ? {name: row.stagename, label: row.stagename, stageid: row.stageid} : {name: "Select Division Stage", label: "Select Division Stage", stageid: -1}}
              disablePortal
              options={divisionstageList}
              getOptionDisabled={option => option.stageid === -1}
              isOptionEqualToValue={(option, value) => (option.stageid === value.stageid)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select Division Stage"
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  error={row.divisionid !== -1 && row.stageid === -1}
                  style={{color: "black"}}
                />
              )}
            />
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
                  max: formatDate(today),
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
              onClick={() => deleteMinistryDivision(_id, row.divisionid)}
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
        <ConfirmModalDivision 
        modalName= {modalName}
        modalMessage= {modalMessage}
        modalDescription= {modalDescription} 
        showModal={showModal}
        resetModal = {resetModal} /> 
      </>
    );
  }
);

export default DivisionalStages;
