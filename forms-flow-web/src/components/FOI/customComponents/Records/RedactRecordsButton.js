import React, { useState } from "react";
import Button from "@material-ui/core/Button";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import {
  DOC_REVIEWER_WEB_URL
} from "../../../../constants/constants";

export default function RedactRecordsButton({ records, groups, ministryrequestid }) {

  const [anchorEl, setAnchorEl] = useState(null);

  const isDisableRedactRecords = (allRecords) => {

    if (groups.length > 0) {
      return false;
    }

    const isInvalid = (record) =>
      !record.isredactionready &&
      !record.attributes?.incompatible &&
      !record.selectedfileprocessversion &&
      !record.ocrfilepath;

    const isInvalidAttachment = (record) =>
      !record.isredactionready &&
      !record.attributes?.incompatible

    return allRecords.some(record => {
      if (isInvalid(record)) return true;

      if (Array.isArray(record.attachments)) {
        return record.attachments.some(isInvalidAttachment);
      }
      return false;
    });
  }

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const parseGroupName = (raw) => {
    if (!raw) return "Document Set";
    const match = raw.match(/^documentSet(\d+)$/i);
    return match ? `Document Set ${match[1]}` : raw;
  };

  const handleRedactAll = () => {
    window.open(`${DOC_REVIEWER_WEB_URL}/foi/${ministryrequestid}`, "_blank");
  };

  const handleRedactGroup = (set) => {
    window.open(
      `${DOC_REVIEWER_WEB_URL}/foi/${set.ministryId}?documentsetid=${set.id}`,
      "_blank"
    );
    handleMenuClose();
  };

  return (
    <>
      {groups.length > 0 ? (
        <>
          <Button
            variant="contained"
            color="primary"
            onClick={handleMenuOpen}
            disabled={isDisableRedactRecords(records)}
            style={{
              background: "#153A6F",
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
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
            transformOrigin={{ vertical: "top", horizontal: "left" }}
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
            {groups.map((set, index) => (
              <MenuItem
                key={set.id}
                onClick={() => handleRedactGroup(set)}
                sx={{
                  fontSize: "14px",
                  fontWeight: 800,
                  color: "#333",
                  paddingY: "8px",
                  paddingX: "16px",
                  "&:hover": { backgroundColor: "#F4F6F8" }
                }}
              >
                {`Redact ${parseGroupName(
                  set.groupname || `Document Set ${index + 1}`
                )}`}
              </MenuItem>
            ))}
          </Menu>
        </>
      ) : (
        <Button
          variant="contained"
          color="primary"
          disabled={isDisableRedactRecords(records)}
          onClick={handleRedactAll}
          style={{
            background: "#153A6F",
            color: "white",
            textTransform: "none",
            padding: "8px 18px",
            borderRadius: "4px",
            fontWeight: 600
          }}
        >
          Redact Records
        </Button>
      )}
    </>
  );
}

