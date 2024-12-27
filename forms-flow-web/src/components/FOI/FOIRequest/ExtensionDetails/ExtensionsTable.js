import React, { useContext, useState } from "react";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import MenuList from "@material-ui/core/MenuList";
import MenuItem from "@material-ui/core/MenuItem";
import { makeStyles } from "@material-ui/core/styles";
import { ActionContext } from "./ActionContext";
import Popover from "@material-ui/core/Popover";
import MoreHorizIcon from "@material-ui/icons/MoreHoriz";
import IconButton from "@material-ui/core/IconButton";
import { extensionStatusId } from "../../../../constants/FOI/enum";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    marginTop: theme.spacing(3),
    overflowX: "auto",
  },
  table: {
    minWidth: 700,
    border: "none",
  },
  columnLabel: {
    fontWeight: theme.typography.fontWeightBold,
  },
  labelRow: {
    borderBottom: "2px solid black",
  },
}));

const ExtensionsTable = ({ showActions = true }) => {
  const classes = useStyles();

  const {
    extensions,
    setSaveModalOpen,
    setDeleteModalOpen,
    setExtensionId,
    requestState
  } = useContext(ActionContext);

  const [popoverOpen, setPopoverOpen] = useState(false);
  const [anchorPosition, setAnchorPosition] = useState(null);

  const ConditionalTableBody = ({ empty, children }) => {
    if (empty) {
      return (
        <>
          <TableBody>
            <TableRow key={`extension-row-empty`}>
              <TableCell colSpan={5} align="center">
                No extensions taken.
              </TableCell>
            </TableRow>
          </TableBody>
        </>
      );
    }

    return (
      <>
        <TableBody>{children}</TableBody>
      </>
    );
  };

  const ConditionalTableCell = ({ condition, children, ...rest }) => {
    if (!condition) {
      return null;
    }

    return (
      <>
        <TableCell {...rest}>{children}</TableCell>
      </>
    );
  };

  const ActionsPopover = () => {
    return (
      <Popover
        anchorReference="anchorPosition"
        anchorPosition={
          anchorPosition && {
            top: anchorPosition.top,
            left: anchorPosition.left,
          }
        }
        open={popoverOpen}
        anchorOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        onClose={() => setPopoverOpen(false)}
      >
        <MenuList>
          <MenuItem
            onClick={() => {
              setSaveModalOpen(true);
              setPopoverOpen(false);
            }}
          >
            Edit
          </MenuItem>
          <MenuItem
            onClick={() => {
              setDeleteModalOpen(true);
              setPopoverOpen(false);
            }}
          >
            Delete
          </MenuItem>
        </MenuList>
      </Popover>
    );
  };

  return (
    <Paper className={classes.root} elevation={0}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow className={classes.labelRow}>
            <TableCell className={classes.columnLabel}>
              EXTENSION REASON
            </TableCell>
            <TableCell className={classes.columnLabel}>DAYS</TableCell>
            <TableCell className={classes.columnLabel}>NEW DUE DATE</TableCell>
            <TableCell className={classes.columnLabel}>STATUS</TableCell>
            <ConditionalTableCell className={classes.columnLabel}
              condition={showActions}
            >ACTIONS</ConditionalTableCell>
          </TableRow>
        </TableHead>
        <ConditionalTableBody empty={!extensions || extensions.length < 1}>
          {extensions.map((extension, index) => {
              return (
                <TableRow key={`extenstion-row-${index}`} hover>
                  <TableCell>{extension.extensionreson}</TableCell>
                  <TableCell>
                    {extension.extensionstatusid === extensionStatusId.approved
                      ? extension.approvednoofdays || extension.extendedduedays
                      : extension.extendedduedays}
                  </TableCell>
                  <TableCell>{extension.extendedduedate}</TableCell>
                  <TableCell>{extension.extensionstatus}</TableCell>
                  <ConditionalTableCell condition={showActions}>
                    <IconButton
                      aria-label= "actions"
                      id={`ellipse-icon-${index}`}
                      key={`ellipse-icon-${index}`}
                      color="primary"
                      onClick={(e) => {
                        setPopoverOpen(true);
                        setAnchorPosition(
                          e.currentTarget.getBoundingClientRect()
                        );
                        setExtensionId(extension.foirequestextensionid);
                      }}
                      disabled={
                        (index > 0 &&
                        extension.extensionstatus !== extensionStatusId.pending) || requestState?.toLowerCase() ===  StateEnum.onhold.name.toLowerCase() || 
                        requestState?.toLowerCase() ===  StateEnum.onholdother.name.toLowerCase() || requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase()
                      }
                    >
                      <MoreHorizIcon />
                    </IconButton>
                  </ConditionalTableCell>
                </TableRow>
              );
            })}
        </ConditionalTableBody>
      </Table>
      <ActionsPopover />
    </Paper>
  );
};

export default ExtensionsTable;
