import React, {useState} from "react";
import Button from "@material-ui/core/Button";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import {
  DOC_REVIEWER_WEB_URL
} from "../../../../constants/constants";
import Grid from "@mui/material/Grid";
import Tooltip from "@mui/material/Tooltip";
import AttachmentModal from "../Attachments/AttachmentModal";
import {makeStyles} from "@material-ui/core/styles";
import clsx from "clsx";

export default function RedactRecordsButton({records, groups, ministryrequestid}) {

  const useStyles = makeStyles((_theme) => ({
    createButton: {
      margin: 0,
      width: "100%",
      height: "50%",
      backgroundColor: "#38598A",
      color: "#FFFFFF",
      fontWeight: 700,
      fontFamily: "BCSans-Bold, sans-serif ",
      textTransform: "none",
      whiteSpace: "nowrap",

      "&:hover": {
        backgroundColor: "#38598A",
      },
      "&:active": {
        backgroundColor: "#38598A",
      },
    },
  }));

  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);
  const [openModal, setOpenModal] = useState(false);

  const isDisableRedactRecords = (allRecords = [], {strict = true} = {}) => {
    if (!Array.isArray(allRecords) || allRecords.length === 0) {
      return true;
    }

    if (!strict) {
      // Only block explicitly incompatible records
      return allRecords.some(
        r => r.attributes?.incompatible === true
      );
    }

    // Strict mode: require processing readiness
    return allRecords.some(r =>
      !r.isredactionready &&
      !r.selectedfileprocessversion &&
      !r.ocrfilepath
    );
  };

  const isThereAnyUngroupedRecord = (allRecords = []) => {
    if (!Array.isArray(allRecords) || allRecords.length === 0) {
      return false;
    }

    return allRecords.some(
      record =>
        record.groupdocumentsetid === null ||
        record.groupdocumentsetid === undefined
    );
  };

  const hasAnyGroupedRecord = (allRecords = []) => {
    if (!Array.isArray(allRecords) || allRecords.length === 0) {
      return false;
    }

    return allRecords.some(
      record => record.groupdocumentsetid != null
    );
  };

  const isDisableRedactSet = (recordGroup = []) => {
    if (!Array.isArray(recordGroup) || recordGroup.length === 0) {
      return true;
    }

    return recordGroup.some(r => {
      const isIncompatible = r.attributes?.incompatible === true;
      const isDuplicate = r.isduplicate === true;

      const isNotReady =
        !r.isredactionready &&
        !r.selectedfileprocessversion &&
        !r.ocrfilepath;

      return isIncompatible || isDuplicate || isNotReady;
    });
  };


  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
    if (isThereAnyUngroupedRecord(records)) {
      setOpenModal(true);
    }
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRedactAll = () => {
    if (hasAnyGroupedRecord(records)) {
      setOpenModal(true);
    } else {
      window.open(`${DOC_REVIEWER_WEB_URL}/foi/${ministryrequestid}`, "_blank");
    }
  };

  const handleRedactGroup = (set) => {
    window.open(
      `${DOC_REVIEWER_WEB_URL}/foi/${set.ministryId}?documentsetid=${set.id}`,
      "_blank"
    );
    handleMenuClose();
  };

  const handleModal = (value) => {
    setOpenModal(false);
    if (!value) {
      setAnchorEl(null);
    } else if (groups.length === 0) {
      window.open(`${DOC_REVIEWER_WEB_URL}/foi/${ministryrequestid}`, "_blank");
    }
  }

  return (
    <>
      {groups.length > 0 ? (
        <div>

          <Button
            variant="contained"
            color="primary"
            onClick={handleMenuOpen}
            className={clsx(
              "btn",
              classes.createButton
            )}


          >
            Redact Records ▾
          </Button>

          <Menu
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl) && !openModal}
            onClose={handleMenuClose}
            getContentAnchorEl={null}
            anchorOrigin={{vertical: "bottom", horizontal: "left"}}
            transformOrigin={{vertical: "top", horizontal: "left"}}
            PaperProps={{
              sx: {
                mt: 1, // small spacing below button
                borderRadius: "8px",
                boxShadow: "0px 4px 14px rgba(0,0,0,0.15)",
                minWidth: "200px",
                py: "4px",
              },
            }}
          >
            {groups.map((set) => {
              const disabled = isDisableRedactSet(set.items);
              const item = (
                <MenuItem
                  key={set.id}
                  disabled={disabled}
                  onClick={() => handleRedactGroup(set)}
                  sx={{
                    fontSize: "14px",
                    fontWeight: 800,
                    py: "8px",
                    px: "16px",
                    cursor: disabled ? "not-allowed" : "pointer",
                  }}
                >
                  {`Redact ${set.name}`}
                </MenuItem>
              );

              return disabled ? (
                <Tooltip
                  key={set.id}
                  title="Some files in this set are still processing or have errors."
                  placement="right"
                  componentsProps={{
                    tooltip: {
                      sx: {
                        fontSize: "12px",
                        padding: "10px 14px",
                        maxWidth: "350px",
                      },
                    },
                  }}
                >
                  <span>{item}</span>
                </Tooltip>
              ) : (
                item
              );
            })}
          </Menu>
        </div>
      ) : (
        <Grid item xs={1}>
          <Tooltip
            title={
              isDisableRedactRecords(records) ? (
                <div style={{fontSize: "11px"}}>
                  Some files are still processing or have errors.
                  Please ensure that all files are successfully processed.
                </div>
              ) : ""
            }
            disableHoverListener={!isDisableRedactRecords(records)}
          >
    <div style={{display: "flex", minWidth: "130px", width: "100%", justifyContent: "revert" , whiteSpace: "nowrap"}}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleRedactAll}
          disabled={isDisableRedactRecords(records)}
          className={clsx(
            "btn",
            classes.createButton
          )}
        >
          Redact Records
        </Button>
      </div>
          </Tooltip>
        </Grid>

      )}
      <AttachmentModal
        modalFor="ungrouped_records"
        openModal={openModal}
        handleModal={handleModal}
        multipleFiles={false}
        requestNumber={""}
        requestId={""}
        attachment={null}
        attachmentsArray={[]}
        handleRename={() => {
        }}
        handleReclassify={() => {
        }}
        handleChangeResponseDate={() => {
        }}
        isMinistryCoordinator={false}
        uploadFor="attachment"
        maxNoFiles={0}
        bcgovcode={""}
      />
    </>
  );
}
