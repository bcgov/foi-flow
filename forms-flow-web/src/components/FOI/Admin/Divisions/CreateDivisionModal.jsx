import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import TextField from "@material-ui/core/TextField";


const CreateDivisionModal = ({
  divisions,
  saveDivision,
  showModal,
  closeModal,
}) => {
  const [division, setDivision] = useState(null);
  let programAreas = useSelector((state) => state.foiRequests.foiAdminProgramAreaList);

  const handleSave = () => {
    saveDivision(division);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };

  useEffect(() => {
    setDivision(null);
  }, [showModal]);

  return (
    <>
      <Dialog fullWidth maxWidth="xs" open={showModal} onClose={handleClose}>
        <DialogTitle>Create Division</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="divisionName"
            label="Division Name"
            value={division ? division.name : ""}
            onChange={(event) =>
              setDivision({ ...division, name: event.target.value })
            }
            fullWidth
          />
          <InputLabel shrink id="create-divisions-areas-label">
            Program Area
          </InputLabel>
          <Select
            margin="dense"
            id="programareaid"
            labelId="create-divisions-areas-label"
            value={division ? division.programareaid : ""}
            onChange={(event) =>
              setDivision({ ...division, programareaid: event.target.value })
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

export default CreateDivisionModal;
