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
import {
  extensionStatusId
} from "../../../../constants/FOI/enum";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    marginTop: theme.spacing(3),
    overflowX: "auto",
  },
  table: {
    minWidth: 700,
    border: "none"
  },
  columnLabel: {
      fontWeight: theme.typography.fontWeightBold
  },
  labelRow: {
      borderBottom: "2px solid black"
  }
}))

const ExtensionsTable = ({showActions = true}) => {

const classes = useStyles()

const { extensions, setModalOpen, setExtensionId, pendingExtensionExists, errorToast } = useContext(ActionContext);

const [popoverOpen, setPopoverOpen] = useState(false)
const [selectedIndex, setSelectedIndex] = useState(null)
const [anchorPosition, setAnchorPosition] = useState(null)
const [selectedExtension, setSelectedExtension] = useState(null)

const ConditionalTableBody = ({empty, children}) => {

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
}

const handleRowClick = () => {
  if(selectedExtension.extensionstatusid !== extensionStatusId.pending && pendingExtensionExists) {
    errorToast(
      "Changes to approved/denied extensions can not be made when there is a pending extension"
    );
    return;
  }

  if (selectedIndex > 0) {
    return;
  }

  setExtensionId(selectedExtension.foirequestextensionid);
  setModalOpen(true)
}

const ConditionalTableCell = ({condition, children, ...rest}) => {
  if(!condition) {
    return null;
  }

  return <>
    <TableCell {...rest}>
      {children}
    </TableCell>
  </>
}

const ActionsPopover = () => {

  return (
    <Popover
      anchorReference="anchorPosition"
      anchorPosition={anchorPosition && {
        top: anchorPosition.top,
        left: anchorPosition.left,
      }}
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
            handleRowClick();
            setPopoverOpen(false);
          }}
        >
          Edit
        </MenuItem>
        <MenuItem
          disabled={true}
        >
          Delete
        </MenuItem>
      </MenuList>
    </Popover>
  );
}

  return (
    <Paper className={classes.root} elevation={0}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow className={classes.labelRow}>
            <TableCell className={classes.columnLabel}>
              EXTENSION REASON
            </TableCell>
            <TableCell className={classes.columnLabel}>
              DAYS
            </TableCell>
            <TableCell className={classes.columnLabel}>
              NEW DUE DATE
            </TableCell>
            <TableCell className={classes.columnLabel}>
              STATUS
            </TableCell>
            <ConditionalTableCell
              condition={showActions}
            ></ConditionalTableCell>
          </TableRow>
        </TableHead>
        <ConditionalTableBody empty={!extensions || extensions.length < 1}>
          {extensions
            .sort((extensionA, extensionB) => {
              if (!extensionA.extendedduedate || !extensionB.extendedduedate) {
                return 0;
              } else {
                return (
                  new Date(extensionB.extendedduedate) -
                  new Date(extensionA.extendedduedate)
                );
              }
            })
            .map((extension, index) => {
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
                      id={`ellipse-icon-${index}`}
                      key={`ellipse-icon-${index}`}
                      color="primary"
                      onClick={(e) => {
                        setPopoverOpen(true);
                        setSelectedIndex(index);
                        setAnchorPosition(
                          e.currentTarget.getBoundingClientRect()
                        );
                        setSelectedExtension(extension);
                      }}
                      disabled={
                        index > 0 &&
                        extension.extensionstatus !== extensionStatusId.pending
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
      <ActionsPopover/>
    </Paper>
  );
}

export default ExtensionsTable;