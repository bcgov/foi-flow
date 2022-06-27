import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { push } from "connected-react-router";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import Grid from "@mui/material/Grid";
import Queue from "./Queue";
import AdvancedSearch from "./AdvancedSearch";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import Divider from "@mui/material/Divider";
import { ButtonBase } from "@mui/material";
import { getTableInfo } from "./columns";
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

const Dashboard = ({ userDetail }) => {
  const user = useSelector((state) => state.user.userDetail);
  const tableInfo = getTableInfo(user.groups);
  const classes = useStyles();
  const dispatch = useDispatch();

  const showAdvancedSearch = useSelector((state) => state.foiRequests.showAdvancedSearch);

  const addRequest = (_e) => {
    dispatch(push(`/foi/addrequest`));
  };

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
            [classes.hidden]: showAdvancedSearch,
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
