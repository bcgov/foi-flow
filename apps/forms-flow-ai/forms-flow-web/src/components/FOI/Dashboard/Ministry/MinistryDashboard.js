import React from "react";
import { useDispatch, useSelector } from "react-redux";

import "../dashboard.scss";
import Grid from "@mui/material/Grid";
import { makeStyles } from "@material-ui/core/styles";
import Queue from "./Queue";
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import Divider from "@mui/material/Divider";
import { ButtonBase } from "@mui/material";
import { setShowAdvancedSearch, setResumeDefaultSorting } from "../../../../actions/FOI/foiRequestActions";

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
  const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch)
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
    } else {
      document.title = 'FOI Request Queue'
    }
  }, [showAdvancedSearch]);

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
            <ButtonBase
              onClick={() => {
                dispatch(setShowAdvancedSearch(false));
                dispatch(setResumeDefaultSorting(true));
              }}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: showAdvancedSearch,
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
                dispatch(setShowAdvancedSearch(true));
                dispatch(setResumeDefaultSorting(true));
              }}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: !showAdvancedSearch,
                })}
              >
                Advanced Search
              </h3>
            </ButtonBase>
          </Grid>
        </Grid>
        <Grid
          container
          direction="row"
          spacing={1}
          className={clsx({
            [classes.hidden]: showAdvancedSearch,
          })}
          sx={{
            marginTop: "2em",
          }}
        >
          <Queue userDetail={userDetail} tableInfo={tableInfo}/>
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

export default MinistryDashboard;
