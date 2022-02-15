import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import Grid from "@mui/material/Grid";
import Queue from "./Queue";
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import Divider from "@mui/material/Divider";
import { Typography, ButtonBase } from "@mui/material";

const useStyles = makeStyles((theme) => ({
  displayed: {
    display: "flex",
    marginTop: "2em",
  },
  hidden: {
    display: "none !important",
  },
  disabledTitle: {
    opacity: "0.3",
  },
}));

const Dashboard = ({ userDetail }) => {
  const classes = useStyles();
  const dispatch = useDispatch();

  const [advnacedSearchEnabled, setAdvancedSearchEnabled] = useState(false);

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
          <Grid
            item
            lg={6}
            xs={12}
            container
            direction="row"
            justifyContent="flex-start"
            alignItems="center"
          >
            <ButtonBase onClick={() => setAdvancedSearchEnabled(false)}>
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: advnacedSearchEnabled,
                })}
              >
                Your FOI Request Queue
              </h3>
            </ButtonBase>
            <Divider
              sx={{
                m: 1,
                borderRightWidth: 3,
                height: 28,
                borderColor: "black",
              }}
              flexItem
              orientation="vertical"
            />
            <ButtonBase onClick={() => setAdvancedSearchEnabled(true)}>
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: !advnacedSearchEnabled,
                })}
              >
                Advanced Search
              </h3>
            </ButtonBase>
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
            [classes.hidden]: advnacedSearchEnabled,
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
          spacing={2}
          sx={{
            marginTop: "2em",
          }}
          className={clsx({
            [classes.hidden]: !advnacedSearchEnabled,
          })}
        >
          <AdvancedSearch userDetail={userDetail} />
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;
