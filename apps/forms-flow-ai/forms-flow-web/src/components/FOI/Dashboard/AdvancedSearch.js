import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "./dashboard.scss";
import { useDispatch, useSelector } from "react-redux";

import Loading from "../../../containers/Loading";
import Grid from "@material-ui/core/Grid";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Chip from "@mui/material/Chip";
import SearchIcon from "@mui/icons-material/Search";
import { makeStyles } from "@material-ui/core/styles";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";

const useStyles = makeStyles((theme) => ({
  search: {
    borderBottom: "1px solid #38598A",
    backgroundColor: "rgba(56,89,138,0.1)",
  },
  searchBody: {
    padding: "2em",
  },
  label: {
    marginBottom: "1em",
  },
}));

const AdvancedSearch = ({ userDetail }) => {
  const classes = useStyles();

  const dispatch = useDispatch();

  const [keywords, setKeywords] = useState(["keyword1", "keyword2"]);

  if (false) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }
  const ClickableChip = ({ clicked = false, ...rest }) => {
    if (!clicked) {
      return (
        <Chip
          sx={{
            color: "#38598A",
            border: "1px solid #38598A",
            width: "100%",
          }}
          {...rest}
          variant="outlined"
        />
      );
    }

    return (
      <Chip
        sx={{
          backgroundColor: "#38598A",
          width: "100%",
        }}
        {...rest}
      />
    );
  };

  return (
    <>
      <Grid item container xs={12}>
        <Grid item xs={12}>
          <Paper
            component={Grid}
            sx={{
              display: "flex",
              width: "100%",
            }}
            alignItems="flex-start"
            direction="row"
            container
          >
            <Grid
              item
              container
              alignItems="center"
              direction="row"
              xs={12}
              className={classes.search}
            >
              <IconButton>
                <SearchIcon />
              </IconButton>
              <InputBase sx={{ ml: 1, flex: 1 }} placeholder="Search" />
              {keywords.map((keyword, index) => (
                <Grid item>
                  <Chip
                    key={`keyword-${index}`}
                    label={keyword}
                    onDelete={() => {}}
                    color="primary"
                    sx={{
                      backgroundColor: "#38598A",
                      marginRight: "1em",
                    }}
                  />
                </Grid>
              ))}
            </Grid>

            <Grid
              item
              container
              alignItems="flex-start"
              justifyContent="flex-start"
              direction="row"
              xs={12}
              className={classes.searchBody}
              spacing={2}
            >
              <Grid item xs={12}>
                <Typography
                  sx={{
                    fontWeight: "bold",
                  }}
                >
                  Advanced Search
                </Typography>
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"REQUEST DESCRIPTION"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"RAW REQUEST #"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"AXIS REQUEST #"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"APPLICANT NAME"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"IAO ANALYST NAME"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-request-description`}
                  label={"SEARCH FILTER"}
                  color="primary"
                  onClick={() => {}}
                />
              </Grid>

              <Grid item xs={4}>
                <Typography
                  sx={{
                    fontWeight: "bold",
                    marginBottom: "2em",
                  }}
                >
                  Request State Criteria
                </Typography>

                <FormGroup>
                  <FormControlLabel
                    control={<Checkbox size="small" />}
                    label="Unopened Requests"
                  />
                  <FormControlLabel
                    control={<Checkbox size="small" />}
                    label="Open Requests"
                  />
                  <FormControlLabel
                    control={<Checkbox size="small" />}
                    label="On Hold Requests"
                  />
                  <FormControlLabel
                    control={<Checkbox size="small" />}
                    label="Closed Requests"
                  />
                </FormGroup>
              </Grid>

              <Grid item xs={6}>
                <Typography
                  sx={{
                    fontWeight: "bold",
                    marginBottom: "2em",
                  }}
                >
                  Search by Date Range
                </Typography>

                <Grid
                  container
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="center"
                >
                  <Grid item xs={5}>
                    <TextField
                      id="from-date"
                      label="From"
                      type="date"
                      InputLabelProps={{
                        shrink: true,
                      }}
                      variant="outlined"
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={2}>
                    <Typography
                      align="center"
                      sx={{
                        fontWeight: "bold",
                      }}
                    >
                      to
                    </Typography>
                  </Grid>

                  <Grid item xs={5}>
                    <TextField
                      id="to-date"
                      label="To"
                      type="date"
                      InputLabelProps={{
                        shrink: true,
                      }}
                      variant="outlined"
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
};

export default AdvancedSearch;
