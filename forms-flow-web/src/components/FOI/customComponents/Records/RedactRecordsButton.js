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

export default function RedactRecordsButton({records, groups, ministryrequestid}) {

  const [anchorEl, setAnchorEl] = useState(null);
  const [openModal, setOpenModal] = useState(false);

  const isDisableRedactRecords = (allRecords = [], { strict = true } = {}) => {
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

  const isDisableRedactSet = ( recordGroup = [],  { strict = true } = {} ) => {
    if (!Array.isArray(recordGroup) || recordGroup.length === 0) {
      return true;
    }

    if (!strict) {
      // Only block explicitly incompatible files
      return recordGroup.some(
        r => r.attributes?.incompatible === true
      );
    }

    // Strict mode (optional)
    return recordGroup.some(r =>
      !r.isredactionready &&
      !r.selectedfileprocessversion &&
      !r.ocrfilepath
    );
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
    if (isThereAnyUngroupedRecord(records)) {
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
        <>
          <Button
            variant="contained"
            color="primary"
            onClick={handleMenuOpen}
            style={{
              background: "#38598A",
              color: "white",
              textTransform: "none",
              padding: "8px 18px",
              borderRadius: "4px",
              fontWeight: 600
            }}
          >
            Redact Records ▾
          </Button>

          <Menu
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl) && !openModal}
            onClose={handleMenuClose}
            anchorOrigin={{vertical: "bottom", horizontal: "left"}}
            transformOrigin={{vertical: "top", horizontal: "left"}}
            PaperProps={{
              sx: {
                mt: 1,
                borderRadius: "8px",
                boxShadow: "0px 4px 14px rgba(0,0,0,0.15)",
                minWidth: "200px",
                paddingY: "4px"
              }
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
        </>
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
    <span>
        <Button
          variant="contained"
          color="primary"
          onClick={handleRedactAll}
          disabled={isDisableRedactRecords(records)}
          style={{
            background: "#38598A",
            textTransform: "none",
            padding: "8px 18px",
            borderRadius: "4px",
            fontWeight: 600,
            color: "#FFFFFF",
            fontFamily: " BCSans-Bold, sans-serif !important",
            cursor: isDisableRedactRecords(records) ? "not-allowed" : "pointer"

          }}
        >
          Redact Records
        </Button>
      </span>
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
        handleRename={() => {}}
        handleReclassify={() => {}}
        handleChangeResponseDate={() => {}}
        isMinistryCoordinator={false}
        uploadFor="attachment"
        maxNoFiles={0}
        bcgovcode={""}
      />
    </>
  );
}
