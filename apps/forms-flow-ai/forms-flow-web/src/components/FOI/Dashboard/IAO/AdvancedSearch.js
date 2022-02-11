import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "../dashboard.scss";
import { useDispatch, useSelector } from "react-redux";

import Loading from "../../../../containers/Loading";
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
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import InputAdornment from "@mui/material/InputAdornment";

import OutlinedInput from "@mui/material/OutlinedInput";
import InputLabel from "@mui/material/InputLabel";
import FormControl from "@mui/material/FormControl";
import ListItemText from "@mui/material/ListItemText";
import Select from "@mui/material/Select";
import { publicBodiesNames } from "./constants";
import { SearchFilter } from "./enum";
import {
  ConditionalComponent,
  formatDate,
} from "../../../../helper/FOI/helper";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

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
  chip: {
    color: "#38598A",
    border: "1px solid #38598A",
    width: "100%",
  },
}));

const AdvancedSearch = ({ userDetail }) => {
  const classes = useStyles();

  const dispatch = useDispatch();

  const [searchText, setSearchText] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [searchFilterSelected, setSearchFilterSelected] = useState(
    SearchFilter.REQUEST_DESCRIPTION
  );
  const keywordsMode =
    searchFilterSelected === SearchFilter.REQUEST_DESCRIPTION;

  const intitialRequestStateCriteria = {
    unopenedRequests: false,
    openRequests: false,
    deduplicationRequests: false,
    cfrRequests: false,
    recordsReviewRequests: false,
    signoffRequests: false,
    closedRequests: false,
    overdueRequests: false,
  };
  const [requestStateCriteria, setRequestStateCriteria] = useState(
    intitialRequestStateCriteria
  );

  const initialRequestTypes = {
    personal: false,
    general: false,
  };
  const [requestTypes, setRequestTypes] = useState(initialRequestTypes);

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const [selectedPublicBodies, setSelectedPublicBodies] = useState([]);

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl) && Boolean(searchText);

  const handleKeywordAdd = () => {
    setAnchorEl(null);
    setKeywords([...keywords, searchText]);
    setSearchText("");
  };

  const handleSearchChange = (e) => {
    setAnchorEl(e.currentTarget);
    setSearchText(e.target.value);
  };

  const clickSearchFilter = (SearchFilterType) => {
    if (searchFilterSelected !== SearchFilterType) {
      setSearchFilterSelected(SearchFilterType);
    }
  };

  const handleRequestStateCriteriaChange = (event) => {
    setRequestStateCriteria({
      ...requestStateCriteria,
      [event.target.name]: event.target.checked,
    });
  };

  const handleRequestTypeChange = (event) => {
    setRequestTypes({
      ...requestTypes,
      [event.target.name]: event.target.checked,
    });
  };

  const handleSelectedPublicBodiesChange = (event) => {
    const {
      target: { value },
    } = event;
    setSelectedPublicBodies(
      // On autofill we get a stringified value.
      typeof value === "string" ? value.split(",") : value
    );
  };

  const ClickableChip = ({ clicked, ...rest }) => {
    if (!clicked) {
      return (
        <Chip
          sx={{
            color: "#38598A",
            border: "1px solid #38598A",
            width: "100%",
          }}
          variant="outlined"
          {...rest}
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

  if (false) {
    return (
      <Grid item xs={12} container alignItems="center">
        <Loading costumStyle={{ position: "relative", marginTop: "4em" }} />
      </Grid>
    );
  }
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
              <Grid item xs={keywordsMode ? 6 : 12}>
                <InputBase
                  placeholder="Search"
                  onChange={handleSearchChange}
                  value={searchText}
                  onKeyPress={(e) => {
                    if (keywordsMode && e.key === "Enter") {
                      handleKeywordAdd();
                    }
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <IconButton>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  }
                  fullWidth
                />
              </Grid>
              <ConditionalComponent condition={keywordsMode}>
                <Grid item container direction="row-reverse" xs={6}>
                  {keywords.map((keyword, index) => (
                    <Chip
                      key={`keyword-${index}`}
                      label={keyword}
                      onDelete={() => {
                        setKeywords(keywords.filter((kw, i) => index !== i));
                      }}
                      color="primary"
                      sx={{
                        backgroundColor: "#38598A",
                        marginRight: "1em",
                      }}
                    />
                  ))}
                </Grid>
              </ConditionalComponent>
            </Grid>
            <ConditionalComponent condition={keywordsMode}>
              <Grid>
                <Menu
                  id="basic-menu"
                  anchorEl={anchorEl}
                  open={open}
                  onClose={handleKeywordAdd}
                  disableAutoFocus={true}
                  autoFocus={false}
                >
                  <MenuItem
                    onClick={handleKeywordAdd}
                  >{`Add "${searchText}"`}</MenuItem>
                </Menu>
              </Grid>
            </ConditionalComponent>

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
                  onClick={() =>
                    clickSearchFilter(SearchFilter.REQUEST_DESCRIPTION)
                  }
                  clicked={
                    searchFilterSelected === SearchFilter.REQUEST_DESCRIPTION
                  }
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-raw-request`}
                  label={"RAW REQUEST #"}
                  color="primary"
                  onClick={() =>
                    clickSearchFilter(SearchFilter.RAW_REQUEST_NUM)
                  }
                  clicked={
                    searchFilterSelected === SearchFilter.RAW_REQUEST_NUM
                  }
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-axis-request`}
                  label={"AXIS REQUEST #"}
                  color="primary"
                  onClick={() =>
                    clickSearchFilter(SearchFilter.AXIS_REQUEST_NUM)
                  }
                  clicked={
                    searchFilterSelected === SearchFilter.AXIS_REQUEST_NUM
                  }
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-applicant-name`}
                  label={"APPLICANT NAME"}
                  color="primary"
                  onClick={() => clickSearchFilter(SearchFilter.APPLICANT_NAME)}
                  clicked={searchFilterSelected === SearchFilter.APPLICANT_NAME}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-assignee-name`}
                  label={"ASSIGNEE NAME"}
                  color="primary"
                  onClick={() => clickSearchFilter(SearchFilter.ASSIGNEE_NAME)}
                  clicked={searchFilterSelected === SearchFilter.ASSIGNEE_NAME}
                />
              </Grid>

              <Grid item xs={2}>
                <ClickableChip
                  key={`filter-search-filter`}
                  label={"SEARCH FILTER"}
                  color="primary"
                  onClick={() => clickSearchFilter(SearchFilter.SEARCH_FILTER)}
                  clicked={searchFilterSelected === SearchFilter.SEARCH_FILTER}
                />
              </Grid>

              <Grid item xs={3} container direction="row" spacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                      marginBottom: "2em",
                    }}
                  >
                    Request State Criteria
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="unopenedRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.unopenedRequests}
                        />
                      }
                      label="Unopened Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="openRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.openRequests}
                        />
                      }
                      label="Open Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="deduplicationRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.deduplicationRequests}
                        />
                      }
                      label="Deduplication Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="cfrRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.cfrRequests}
                        />
                      }
                      label="Call for Records Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="recordsReviewRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.recordsReviewRequests}
                        />
                      }
                      label="Records Review Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="signoffRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.signoffRequests}
                        />
                      }
                      label="Sign Off Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="closedRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.closedRequests}
                        />
                      }
                      label="Closed Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="overdueRequests"
                          onChange={handleRequestStateCriteriaChange}
                          checked={requestStateCriteria.overdueRequests}
                        />
                      }
                      label="Overdue Requests"
                    />
                  </FormGroup>
                </Grid>
              </Grid>

              <Grid item xs={3} container direction="row" spacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                  >
                    Request Type
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="personal"
                          onChange={handleRequestTypeChange}
                          checked={requestTypes.personal}
                        />
                      }
                      label="Personal Requests"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="general"
                          onChange={handleRequestTypeChange}
                          checked={requestTypes.general}
                        />
                      }
                      label="General Requests"
                    />
                  </FormGroup>
                </Grid>
              </Grid>

              <Grid item xs={6} container direction="row" spacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                  >
                    Search by Date Range
                  </Typography>
                </Grid>

                <Grid
                  container
                  item
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="center"
                  xs={12}
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
                      value={fromDate}
                      InputProps={{
                        inputProps: { max: toDate || formatDate(new Date()) },
                      }}
                      onChange={(e) => setFromDate(formatDate(e.target.value))}
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
                      InputProps={{
                        inputProps: {
                          min: fromDate,
                          max: formatDate(new Date()),
                        },
                      }}
                      value={toDate}
                      onChange={(e) => setToDate(formatDate(e.target.value))}
                      variant="outlined"
                      fullWidth
                    />
                  </Grid>
                </Grid>

                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                  >
                    Search by Public Body
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel id="demo-multiple-checkbox-label" shrink>
                      Public Body
                    </InputLabel>
                    <Select
                      labelId="demo-multiple-checkbox-label"
                      id="demo-multiple-checkbox"
                      multiple
                      displayEmpty
                      value={selectedPublicBodies}
                      onChange={handleSelectedPublicBodiesChange}
                      input={<OutlinedInput label="Public Body" notched />}
                      renderValue={(selected) => {
                        if (selected.length === 0) {
                          return <em>All</em>;
                        }

                        return selected.join(", ");
                      }}
                      MenuProps={MenuProps}
                    >
                      <MenuItem disabled value="">
                        <em>All</em>
                      </MenuItem>
                      {publicBodiesNames.map((publicBody) => (
                        <MenuItem key={publicBody} value={publicBody}>
                          <Checkbox
                            checked={
                              selectedPublicBodies.indexOf(publicBody) > -1
                            }
                          />
                          <ListItemText primary={publicBody} />
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Grid item xs={3}>
                <Button
                  color="primary"
                  sx={{
                    backgroundColor: "#38598A",
                    width: "100%",
                    color: "white",
                    fontWeight: "bold",
                  }}
                  fullWidth
                >
                  Apply Search
                </Button>
              </Grid>
              <Grid item xs={3}>
                <Button
                  variant="outlined"
                  sx={{
                    color: "#38598A",
                    border: "1px solid #38598A",
                    width: "100%",
                    fontWeight: "bold",
                  }}
                  fullWidth
                >
                  Outlined
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
};

export default AdvancedSearch;

// const SearchBar = ({keywords}) => {
//   return (
//     <>
//       <IconButton>
//         <SearchIcon />
//       </IconButton>
//       <InputBase
//         sx={{ ml: 1, flex: 1 }}
//         placeholder="Search"
//         onChange={handleSearchChange}
//         value={searchText}
//       />
//       {keywords.map((keyword, index) => (
//         <Grid item>
//           <Chip
//             key={`keyword-${index}`}
//             label={keyword}
//             onDelete={() => {}}
//             color="primary"
//             sx={{
//               backgroundColor: "#38598A",
//               marginRight: "1em",
//             }}
//           />
//         </Grid>
//       ))}
//     </>
//   );
// };
