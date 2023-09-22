import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
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

const CreateSectionModal = ({
  divisions,
  saveDivision,
  showModal,
  closeModal,
  filterParentDivisions,
}) => {
  const [section, setSection] = useState({
    name: "",
    programareaid: null,
    issection: true,
    parentid: null,
    specifictopersonalrequests: false,
  });
  const [parentDivisions, setParentDivisions] = useState(divisions);

  let programAreas = useSelector((state) => state.foiRequests.foiAdminProgramAreaList);

  //useEffect to manage filtering of dropdown for parent divisions
  useEffect(() => {
    setParentDivisions(filterParentDivisions(section, divisions, "CREATE"))
  }, [section])

  useEffect(() => {
    setSection({
      name: "",
      programareaid: null,
      issection: true,
      parentid: null,
      specifictopersonalrequests: false,
    });
  }, [showModal]);
  
  const handleSave = () => {
    saveDivision(section);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };

  return (
    <>
      <Dialog fullWidth maxWidth="xs" open={showModal} onClose={handleClose}>
        <DialogTitle>Create Section</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            required
            margin="dense"
            id="sectionName"
            label="Section Name"
            value={section.name}
            onChange={(event) =>
                setSection({ ...section, name: event.target.value })
            }
            fullWidth
          />
          <InputLabel required shrink id="create-divisions-areas-label">
            Program Area
          </InputLabel>
          <Select
            margin="dense"
            id="programareaid"
            labelId="create-divisions-areas-label"
            value={section.programareaid}
            onChange={(event) =>
                setSection({ ...section, programareaid: event.target.value })
            }
            fullWidth
          >
            {programAreas &&
              programAreas.map((area, index) => (
                <MenuItem key={index} value={area.programareaid}>
                  {area.name}
                </MenuItem>
              ))}
          </Select>
          <div style={{display: "flex", flexDirection: "row", justifyContent:"center", alignItems: "center"}}>
            <FormControlLabel id="create-divisions-areas-label" control={<Checkbox checked={section.specifictopersonalrequests} onChange={() => setSection({...section, specifictopersonalrequests: !section.specifictopersonalrequests, parentid: null})} />} label="Specific to Personal Request" />
          </div>
          <InputLabel shrink id="create-divisions-areas-label">
            Parent Division
          </InputLabel>
          <Select
            margin="dense"
            id="parentid"
            labelId="create-divisions-areas-label"
            value={section.parentid}
            onChange={(event) =>
              setSection({ ...section, parentid: event.target.value })
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

export default CreateSectionModal;