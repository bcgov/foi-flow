import React, { useState, useEffect } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import TextField from "@material-ui/core/TextField";

const EditDivisionModal = ({
  initialDivision,
  divisions,
  saveDivision,
  showModal,
  closeModal,
}) => {
  const [division, setDivision] = useState(initialDivision);

  const handleSave = () => {
    saveDivision(division);
    closeModal();
  };

  const handleClose = () => {
    closeModal();
  };

  useEffect(() => {
    setDivision(initialDivision);
  }, [initialDivision, showModal]);

  return (
    <>
      <Dialog fullWidth maxWidth="xs" open={showModal} onClose={handleClose}>
        <DialogTitle>Edit Division</DialogTitle>
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
          <InputLabel shrink id="edit-divisions-areas-label">
            Program Area
          </InputLabel>
          <Select
            margin="dense"
            id="programareaid"
            labelId="edit-divisions-areas-label"
            value={division ? division.programareaid : ""}
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
