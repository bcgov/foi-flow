import React, { useState } from "react";
import {
  faSpinner,
  faExclamationCircle,
  faCheckCircle,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import Tooltip from "@mui/material/Tooltip";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { makeStyles } from "@material-ui/core/styles";

const PhaseMenu = ({
  item,
  index,
  phasedRedlineDownloadStatuses,
  handlePhasePackageDownload,
  getPhasePackageDatetime
}) => {
  // PhasePackage submenu state
  const [anchorEl, setAnchorEl] = useState(null);
  const openMenu = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const useStyles = makeStyles((_theme) => ({
    statusIcons: {
      height: "20px",
      paddingRight: "10px",
    },
  }));
  const classes = useStyles();
  
  return (
    <>
      <MenuItem
        onClick={handleClick}
        // disabled={phasedRedlineDownloadStatuses.length <= 0}
        className="download-menu-item"
        key={item.id}
        value={index}
        aria-haspopup="true"
      >
        <span>{item.label}</span>
        <FontAwesomeIcon
          icon={faChevronRight}
          size="2x"
          className={classes.statusIcons}
          style={{ marginLeft: "50px", marginTop: "1px" }}
        />
      </MenuItem>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={openMenu}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        anchorOrigin={{
          vertical: "center",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
      >
        {phasedRedlineDownloadStatuses?.map((phasedRedline, index) => {
          return (
            <MenuItem
              className="download-menu-item"
              key={phasedRedline.category}
              onClick={() => {handlePhasePackageDownload(phasedRedline.category)}}
              value={phasedRedline.category}
              sx={{ display: "flex" }}
            >
              {phasedRedline.downloadReady ? (
                <FontAwesomeIcon
                  icon={faCheckCircle}
                  size="2x"
                  color="#1B8103"
                  className={classes.statusIcons}
                />
              ) : phasedRedline.downloadFailed? (
                <FontAwesomeIcon
                  icon={faExclamationCircle}
                  size="2x"
                  color="#A0192F"
                  className={classes.statusIcons}
                />
              ) : phasedRedline.downloadWIP ? (
                <FontAwesomeIcon
                  icon={faSpinner}
                  size="2x"
                  color="#FAA915"
                  className={classes.statusIcons}
                />
              ) : null}
              <Tooltip enterDelay={500} title={`Created On: ${getPhasePackageDatetime(phasedRedline.category) ? getPhasePackageDatetime(phasedRedline.category) : "N/A"}`}>
              <span>Phase {phasedRedline.category.slice(-1)}</span>
              </Tooltip>
            </MenuItem>
          );
        })}
      </Menu>
    </>
  );
};

export default PhaseMenu;
