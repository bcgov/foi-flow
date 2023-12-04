import { useEffect, useState } from "react";
import "./requestflag.scss";
import OutlinedInput from "@material-ui/core/OutlinedInput";
import MenuItem from "@material-ui/core/MenuItem";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFlag } from "@fortawesome/free-regular-svg-icons";
import { faFlag as faSolidFlag } from "@fortawesome/free-solid-svg-icons";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import CloseIcon from "@material-ui/icons/Close";
import IconButton from "@material-ui/core/IconButton";
import TextField from "@mui/material/TextField";

//Types are:
//oipcreview
//phasedrelease
const RequestFlag = ({ isActive, type, handleSelect, showFlag = true }) => {
  const [isSelected, setIsSelected] = useState(isActive || false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalHeading, setModalHeading] = useState("");
  const [modalMessage, setModalMessage] = useState("");
  const [modalDescription, setModalDescription] = useState("");
  
  useEffect(() => {
    if (isActive == null) {
      setIsSelected(false);
    } else {
    setIsSelected(isActive);
    }
  }, [isActive])

  // These need to be set for each type
  let options;
  let id;
  let modalHeadingActive = "";
  let modalHeadingInactive = "";
  let modalMessageActive = "";
  let modalMessageInactive = "";
  let modalDescriptionActive = "";
  let modalDescriptionInactive = "";

  // css
  let iconClass;
  let isSelectedBgClass;
  let bgClass;

  switch (type) {
    //Need to change heading, message, description for modals as well
    case "oipcreview":
      options = [
        {
          value: true,
          label: "OIPC Review",
          disabled: false,
        },
        {
          value: false,
          label: "No Review",
          disabled: false,
        },
      ];

      id = "oipc-review-flag";
      iconClass = "oipc-review-icon";
      isSelectedBgClass =
        "linear-gradient(to right, rgba(250,124,22,0.32) 80%, #fa7c16 0%)";
      bgClass = "linear-gradient(to right, #fff 80%, #fa7c16 0%)";

      //when setting to active
      modalHeadingActive = "OIPC Review";
      modalMessageActive =
        "Are you sure you want to flag this request as OIPC review?";
      modalDescriptionActive = (
        <span>
          This will create a new <b>OIPC review</b> section on this request.
        </span>
      );

      //when setting to inactive
      modalHeadingActive = "OIPC Review";
      modalMessageInactive =
        "Are you sure you want to remove the OIPC review flag from this request?";
      modalDescriptionInactive = (
        <span>
          This will remove the <b>OIPC review</b> section from this request.
        </span>
      );
      break;

    case "phasedrelease":
      options = [
        {
          value: true,
          label: "Phased Release",
          disabled: false,
        },
        {
          value: false,
          label: "Single Release",
          disabled: false,
        },
      ];

      id = "phased-release-flag";
      iconClass = "phased-release-icon";
      isSelectedBgClass =
        "linear-gradient(to right, rgba(146, 7, 183, 0.32) 80%, #9207b7 0%)";
      bgClass = "linear-gradient(to right, #fff 80%, #9207b7 0%)";

      //when setting to active
      modalHeadingActive = "Phased Release";
      modalMessageActive =
        "Are you sure you want to flag this request as a Phased Release?";
      modalDescriptionActive = (
        <span>This will tag the request as Phased Release.</span>
      );

      //when setting to inactive
      modalHeadingInactive = "Single Release";
      modalMessageInactive =
        "Are you sure you want to change this request to Single Release?";
      modalDescriptionInactive = (
        <span>This will tag the request as Single Release.</span>
      );
      break;
  }

  const handleValueChange = (e) => {
    setIsSelected(e.target.value);
    if (type == "oipcreview" && !isActive) {
        handleSelect(e.target.value)
    } else {
        setModalOpen(true);
    }

    if (e.target.value == true) {
      setModalHeading(modalHeadingActive);
      setModalMessage(modalMessageActive);
      setModalDescription(modalDescriptionActive);
    } else {
      setModalHeading(modalHeadingInactive);
      setModalMessage(modalMessageInactive);
      setModalDescription(modalDescriptionInactive);
    }
  };

  const handleClose = () => {
    setModalOpen(false);
    setIsSelected(isActive);
  };

  const handleSave = (e) => {
    setModalOpen(false);
    handleSelect(isSelected);
  };

  if (!showFlag) return <></>;
  return (
    <>
      <div className="request-flag">
        <div className="request-flag-dropdown-all">
          <div
            className="request-flag-select"
            style={{ background: isSelected ? isSelectedBgClass : bgClass }}
          >
            {isSelected ? (
              <FontAwesomeIcon
                icon={faSolidFlag}
                size="2x"
                className={iconClass}
              />
            ) : (
              <FontAwesomeIcon icon={faFlag} size="2x" className={iconClass} />
            )}
            {/* <InputLabel id="restrict-dropdown-label">
                    Unrestricted
                    </InputLabel> */}
            <TextField
              id="request-flag-dropdown"
              className="request-flag-dropdown"
              select
              value={isSelected}
              onChange={handleValueChange}
              inputProps={{ "aria-labelledby": "restrict-dropdown-label" }}
              input={<OutlinedInput label="Tag" />}
              disabled={false}
            >
              {options.map((option) => (
                <MenuItem
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                >
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </div>
        </div>
      </div>
      <div className="state-change-dialog">
        <Dialog
          open={modalOpen}
          onClose={() => {
            console.log("onClose");
          }}
          aria-labelledby="state-change-dialog-title"
          aria-describedby="restricted-modal-text"
          maxWidth={"md"}
          fullWidth={true}
          // id="state-change-dialog"
        >
          <DialogTitle disableTypography id="state-change-dialog-title">
            <h2 className="state-change-header">{modalHeading}</h2>
            <IconButton className="title-col3" onClick={handleClose}>
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="restricted-modal-text" component={"span"}>
              <div className="modal-msg">
                <div className="confirmation-message">{modalMessage}</div>
                <div className="modal-msg-description">
                  <i>{modalDescription}</i>
                </div>
              </div>
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <button
              className={`btn-bottom btn-save btn`}
              onClick={handleSave}
              disabled={false}
            >
              Save Change
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    </>
  );
};

export default RequestFlag;
