import React, { useState } from "react";

import "../dashboard.scss";
import { useDispatch } from "react-redux";
import Grid from "@mui/material/Grid";
import { makeStyles } from "@material-ui/core/styles";
import Queue from "./Queue";
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import Divider from "@mui/material/Divider";
import { ButtonBase } from "@mui/material";

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
  //   const user = useSelector((state) => state.user.userDetail);
  //   const tableInfo = getTableInfo(user.groups);
  const dispatch = useDispatch();

  const classes = useStyles();

  const [filterModel, setFilterModel] = React.useState({
    fields: [
      "applicantcategory",
      "requestType",
      "idNumber",
      "currentState",
      "assignedministrypersonLastName",
      "assignedministrypersonFirstName",
    ],
    keyword: null,
  });
  const [requestFilter, setRequestFilter] = useState("All");

  const [advnacedSearchEnabled, setAdvancedSearchEnabled] = useState(false);

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
              onClick={() => setAdvancedSearchEnabled(false)}
              disableRipple
            >
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
              onClick={() => setAdvancedSearchEnabled(true)}
              disableRipple
            >
              <h3
                className={clsx("foi-request-queue-text", {
                  [classes.disabledTitle]: !advnacedSearchEnabled,
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

export default MinistryDashboard;
