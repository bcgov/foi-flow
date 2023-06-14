import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import Grid from "@mui/material/Grid";
import Queue from "./Queue";
import EventQueue from "../EventQueue"
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import Divider from "@mui/material/Divider";
import { ButtonBase } from "@mui/material";
import { getTableInfo } from "./columns";
import { getIAOEventQueueTableInfo } from "../EventQueueColumns"
import { setShowAdvancedSearch, setResumeDefaultSorting, setShowEventQueue } from "../../../../actions/FOI/foiRequestActions";

const useStyles = makeStyles(() => ({
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
  const user = useSelector((state) => state.user.userDetail);
  const tableInfo = getTableInfo(user.groups);
  const eventQueueTableInfo = getIAOEventQueueTableInfo();
  const classes = useStyles();
  const dispatch = useDispatch();

  const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch);
  const showEventQueue = useSelector((state) => state.foiRequests.showEventQueue);

  const addRequest = (_e) => {
    dispatch(push(`/foi/addrequest`));
  };

  React.useEffect(() => {
    if (showAdvancedSearch) {
      document.title = 'FOI Advanced Search'
    } else if (showEventQueue) {
      document.title = 'Event Queue'
    } else {
      document.title = 'FOI Request Queue'
    }
  }, [showAdvancedSearch, showEventQueue]);

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
            lg={8}
            xs={12}
            container
            direction="row"
            justifyContent="flex-start"
            alignItems="center"
          >
            <ButtonBase
              onClick={() => {
                dispatch(setShowAdvancedSearch(false));
                dispatch(setShowEventQueue(false));
                dispatch(setResumeDefaultSorting(true));
              }}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: showAdvancedSearch || showEventQueue,
                })}
              >
                Your FOI Request Queue
              </h3>
            </ButtonBase>
            <Divider
              sx={{
                mr: 2,
                ml: 2,
                borderRightWidth: 3,
                height: 28,
                borderColor: "black",
              }}
              flexItem
              orientation="vertical"
            />
            <ButtonBase
              onClick={() => {
                dispatch(setShowEventQueue(true));
                dispatch(setShowAdvancedSearch(false));
                //dispatch(setResumeDefaultSorting(true));
              }}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: !showEventQueue || showAdvancedSearch,
                })}
              >
                Event Queue
              </h3>
            </ButtonBase>
            <Divider
              sx={{
                mr: 2,
                ml: 2,
                borderRightWidth: 3,
                height: 28,
                borderColor: "black",
              }}
              flexItem
              orientation="vertical"
            />
            <ButtonBase
              onClick={() => {
                dispatch(setShowAdvancedSearch(true));
                dispatch(setShowEventQueue(false));
                dispatch(setResumeDefaultSorting(true));
              }}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: !showAdvancedSearch || showEventQueue,
                })}
              >
                Advanced Search
              </h3>
            </ButtonBase>
          </Grid>
          <Grid item container lg={4} xs={6} justifyContent="flex-end">
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
            [classes.hidden]: showAdvancedSearch || showEventQueue,
          })}
          sx={{
            marginTop: "2em",
          }}
        >
          <Queue userDetail={userDetail} tableInfo={tableInfo} />
        </Grid>

        <Grid
          container
          direction="row"
          spacing={2}
          sx={{
            marginTop: "2em",
          }}
          className={clsx({
            [classes.hidden]: !showEventQueue,
          })}
        >
          <EventQueue userDetail={userDetail} eventQueueTableInfo={eventQueueTableInfo} />
        </Grid>

        <Grid
          container
          direction="row"
          spacing={2}
          sx={{
            marginTop: "2em",
          }}
          className={clsx({
            [classes.hidden]: !showAdvancedSearch,
          })}
        >
          <AdvancedSearch userDetail={userDetail} />
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;
