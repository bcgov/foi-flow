import React from "react";
import { useDispatch, useSelector } from "react-redux";

import "../dashboard.scss";
import Grid from "@mui/material/Grid";
import { makeStyles } from "@material-ui/core/styles";
import Queue from "./Queue";
import EventQueue from "../EventQueue"
import { getMinistryEventQueueTableInfo } from "../EventQueueColumns"
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import Divider from "@mui/material/Divider";
import { ButtonBase } from "@mui/material";
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

const MinistryDashboard = ({ userDetail }) => {
  const classes = useStyles();
  const eventQueueTableInfo = getMinistryEventQueueTableInfo();
  const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch)
  const showEventQueue = useSelector((state) => state.foiRequests.showEventQueue);
  const tableInfo = {
    sort: [
      { field: "ministrySorting", sort: "asc" },
      // { field: "cfrduedate", sort: "asc" }
    ]
  };
  const dispatch = useDispatch();

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
        </Grid>
        { (!showAdvancedSearch && !showEventQueue) &&
        <Grid
          container
          direction="row"
          spacing={1}
          // className={clsx({
          //   [classes.hidden]: showAdvancedSearch || showEventQueue,
          // })}
          sx={{
            marginTop: "2em",
          }}
        >
          <Queue userDetail={userDetail} tableInfo={tableInfo}/>
        </Grid>
        }
        { showEventQueue &&
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
        }
        { showAdvancedSearch &&
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
        }
      </Grid>
    </div>
  );
};

export default MinistryDashboard;
