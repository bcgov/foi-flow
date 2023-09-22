import React, { useState, useEffect } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import TextField from "@material-ui/core/TextField";
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

const EditDivisionModal = ({
  initialDivision,
  divisions,
  saveDivision,
  showModal,
  closeModal,
  filterParentDivisions,
}) => {
  const [division, setDivision] = useState({
    name: "",
    programareaid: null,
    issection: false,
    parentid: null,
    specifictopersonalrequests: false,
  });
  const [parentDivisions, setParentDivisions] = useState(divisions);

  const handleSave = () => {
    saveDivision(division);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };
  
  useEffect(() => {
    setDivision(initialDivision || {
      name: "",
      programareaid: null,
      issection: false,
      parentid: null,
      specifictopersonalrequests: false,
    });
  }, [showModal]);

  //useEffect to manage filtering of dropdown for parent divisions
  useEffect(() => {
    setParentDivisions(filterParentDivisions(division, divisions, "EDIT"))
  }, [division])

  return (
    <>
      <Dialog fullWidth maxWidth="xs" open={showModal} onClose={handleClose}>
        <DialogTitle>{division.issection ? "Edit Section" : "Edit Division"}</DialogTitle>
        <DialogContent>
          <TextField
            required
            autoFocus
            margin="dense"
            id="divisionName"
            label="Division/Section Name"
            value={division.name}
            onChange={(event) =>
              setDivision({ ...division, name: event.target.value })
            }
            fullWidth
          />
          <InputLabel required shrink id="edit-divisions-areas-label">
            Program Area
          </InputLabel>
          <Select
            margin="dense"
            id="programareaid"
            labelId="edit-divisions-areas-label"
            value={division.programareaid}
            onChange={(event) =>
              setDivision({ ...division, programareaid: event.target.value })
            }
            fullWidth
          >
            {divisions &&
              [
                ...new Map(
                  divisions.map((item) => [item["programareaid"], item])
                ).values(),
              ].map((area, index) => (
                <MenuItem key={index} value={area.programareaid}>
                  {area.programarea}
                </MenuItem>
              ))}
          </Select>
          <div class="edit-sortorder-wrapper">
          <TextField
            autoFocus
            type="number"
            margin="dense"
            id="sortorder"
            label="Sort Order"
            value={division ? division.sortorder : 0}
            onChange={(event) =>
              setDivision({ ...division, sortorder: event.target.value })
            }
            fullWidth
            InputLabelProps={{
              shrink: true,
            }}
          />
          </div>
          <div style={{display: "flex", flexDirection: "row", justifyContent: "center"}}>
            <FormControlLabel required label="Is Section" id="edit-divisions-areas-label" control={
            <Checkbox 
              checked={division ? division.issection : false}
              onChange={() => setDivision({...division, issection: !division.issection, parentid: null})} 
            />} 
            />
            <FormControlLabel label="Specific to Personal Request" id="edit-divisions-areas-label" control={
            <Checkbox 
              checked={division ? division.specifictopersonalrequests : false}
              onChange={() => setDivision({...division, specifictopersonalrequests: !division.specifictopersonalrequests})} 
            />} 
            />
          </div>
          <InputLabel shrink id="edit-divisions-areas-label">
            Parent Division
          </InputLabel>
          <Select
            disabled={division ? !division.issection : false}
            margin="dense"
            id="parentid"
            labelId="edit-divisions-areas-label"
            value={division.parentid}
            onChange={(event) =>
              setDivision({ ...division, parentid: event.target.value })
            }
            fullWidth
          >
            {parentDivisions &&
              parentDivisions.map((item, index) => (
                <MenuItem key={index} value={item.divisionid}>
                  {item.name}
                </MenuItem>
              ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <button onClick={handleSave} className="btn-bottom btn-save">
            Save
          </button>
          <button onClick={handleClose} className="btn-bottom btn-cancel">
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EditDivisionModal;
