import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import Grid from "@material-ui/core/Grid";
import Queue from "./Queue";
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  displayed: {
    display: "flex",
    marginTop: "2em",
  },
  hidden: {
    display: "none",
  },
}));

const AdvancedDashboard = ({ userDetail }) => {
  const classes = useStyles();
  const dispatch = useDispatch();

  const addRequest = (e) => {
    dispatch(push(`/foi/addrequest`));
  };

  return (
    <div className="container foi-container">
      <Grid
        container
        direction="row"
        className="foi-grid-container"
        spacing={1}
      >
        <Grid
          item
          container
          direction="row"
          alignItems="center"
          xs={12}
          className="foi-dashboard-row2"
        >
          <Grid item lg={6} xs={12}>
            <h3 className="foi-request-queue-text">Your FOI Request Queue</h3>
          </Grid>
          <Grid item container lg={6} xs={12} justifyContent="flex-end">
            <button
              type="button"
              className="btn foi-btn-create"
              onClick={addRequest}
            >
              {FOI_COMPONENT_CONSTANTS.ADD_REQUEST}
            </button>
          </Grid>
        </Grid>
        <Grid
          container
          direction="row"
          spacing={1}
          className={clsx({
            [classes.hidden]: !false,
            [classes.displayed]: !true,
          })}
          sx={{
            marginTop: "2em",
          }}
        >
          <Queue userDetail={userDetail} />
        </Grid>

        <Grid
          container
          direction="row"
          spacing={1}
          className={clsx({
            [classes.hidden]: false,
            [classes.displayed]: true,
          })}
        >
          <AdvancedSearch userDetail={userDetail} />
        </Grid>
      </Grid>
    </div>
  );
};

export default AdvancedDashboard;
