import React, { useContext } from "react";
import PropTypes from "prop-types";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import { faEllipsisH } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { makeStyles } from "@material-ui/core/styles";
import CircularProgress from "@material-ui/core/CircularProgress";
import { ActionContext } from "./ActionContext";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    marginTop: theme.spacing.unit * 3,
    overflowX: "auto",
  },
  table: {
    minWidth: 700,
    border: "none"
  },
  columnLabel: {
      fontWeight: "bold"
  },
  labelRow: {
      borderBottom: "2px solid black"
  }
}))

const ExtensionsTable = () => {

const classes = useStyles()

const {
  extensions,
} = useContext(ActionContext);

const ConditionalTableBody = ({empty, children}) => {

    if (empty) {
        return (
          <>
          <TableBody>
            <TableRow key={`key-empty`}>
                <TableCell colSpan={5} align="center">
                    There are no extensions
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

  return (
    <Paper className={classes.root} elevation={0}>
      <Table className={classes.table}>
        <TableHead>
          <TableRow className={classes.labelRow}>
            <TableCell className={classes.columnLabel}>
              EXTENSION REASON
            </TableCell>
            <TableCell className={classes.columnLabel} numeric>
              DAYS
            </TableCell>
            <TableCell className={classes.columnLabel} numeric>
              NEW DUE DATE
            </TableCell>
            <TableCell className={classes.columnLabel} numeric>
              STATUS
            </TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <ConditionalTableBody empty={!extensions || extensions.length < 1}>
          {extensions.map((extension) => {
            return (
              <TableRow key={`key-${extension.extensionstatusid}`}>
                <TableCell numeric>{extension.extensionreson}</TableCell>
                <TableCell numeric>{extension.extendedduedays}</TableCell>
                <TableCell>{extension.extendedduedate}</TableCell>
                <TableCell>{extension.extensionstatus}</TableCell>
                <TableCell>
                  <button className="actionsBtn">
                    <FontAwesomeIcon
                      icon={faEllipsisH}
                      size="1x"
                      color="darkblue"
                    />
                  </button>
                </TableCell>
              </TableRow>
            );
          })}
        </ConditionalTableBody>
      </Table>
    </Paper>
  );
}

ExtensionsTable.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default ExtensionsTable;