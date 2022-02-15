import React, { useEffect, useState, useContext } from "react";
import { DataGrid } from "@mui/x-data-grid";
import "../../dashboard.scss";
import { useDispatch, useSelector } from "react-redux";

import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
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
} from "../../../../../helper/FOI/helper";
import { ActionContext } from "./ActionContext";
import { StateEnum } from "../../../../../constants/FOI/statusEnum";

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

  const { handleUpdateSearchFilter, searchLoading, setSearchLoading } =
    useContext(ActionContext);

  const programAreaList = useSelector(
    (state) => state.foiRequests.foiProgramAreaList
  );

  const isLoading = useSelector((state) => state.foiRequests.isLoading);
  const isAssignedToListLoading = useSelector(
    (state) => state.foiRequests.isAssignedToListLoading
  );

  const [searchText, setSearchText] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [searchFilterSelected, setSearchFilterSelected] = useState(
    SearchFilter.REQUEST_DESCRIPTION
  );
  const keywordsMode =
    searchFilterSelected === SearchFilter.REQUEST_DESCRIPTION;

  const intitialRequestState = {
    unopened: {
      checked: false,
      id: StateEnum.unopened.id,
    },
    open: {
      checked: false,
      id: StateEnum.open.id,
    },
    callforrecords: {
      checked: false,
      id: StateEnum.callforrecords.id,
    },
    review: {
      checked: false,
      id: StateEnum.review.id,
    },
    signoff: {
      checked: false,
      id: StateEnum.signoff.id,
    },
    closed: {
      checked: false,
      id: StateEnum.closed.id,
    },
    callforrecordsoverdue: {
      checked: false,
      id: StateEnum.callforrecordsoverdue.id,
    },
  };
  const [requestState, setRequestState] = useState(intitialRequestState);

  const intitialRequestStatus = {
    overdue: false,
    onTime: false,
  };
  const [requestStatus, setRequestStatus] = useState(intitialRequestStatus);

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

  const getTrueKeysFromCheckboxObject = (checkboxObject) => {
    return Object.entries(checkboxObject)
      .map(([key, value]) => {
        if (value instanceof Object) {
          return value.checked ? value.id : null;
        }
        return value ? key.toLowerCase() : null;
      })
      .filter((value) => value);
  };
  const handleApplySearchFilters = () => {
    setSearchLoading(true);
    handleUpdateSearchFilter({
      search: searchFilterSelected.replace("_", "").toLowerCase(),
      keywords: keywordsMode ? keywords : [searchText],
      requestState: getTrueKeysFromCheckboxObject(requestState),
      requestType: getTrueKeysFromCheckboxObject(requestTypes),
      requestStatus: getTrueKeysFromCheckboxObject(requestStatus),
      fromDate: fromDate,
      toDate: toDate,
      publicBodies: selectedPublicBodies,
    });
  };

  const handleResetSearchFilters = () => {
    setSearchText("");
    setKeywords([]);
    setSearchFilterSelected(SearchFilter.REQUEST_DESCRIPTION);
    setRequestState(intitialRequestState);
    setRequestTypes(initialRequestTypes);
    setFromDate("");
    setToDate("");
    setSelectedPublicBodies([]);
  };

  const handleKeywordAdd = () => {
    if (!searchText) {
      return;
    }
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

  const handleRequestStateChange = (event) => {
    setRequestState({
      ...requestState,
      [event.target.name]: {
        ...requestState[event.target.name],
        checked: event.target.checked,
      },
    });
  };

  const handleRequestStatusChange = (event) => {
    setRequestStatus({
      ...requestStatus,
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

  if (isLoading || isAssignedToListLoading) {
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
              rowSpacing={2}
              columnSpacing={1}
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
                  label={"SUBJECT CODE"}
                  color="primary"
                  onClick={() => clickSearchFilter(SearchFilter.SUBJECT_CODE)}
                  clicked={searchFilterSelected === SearchFilter.SUBJECT_CODE}
                />
              </Grid>

              <Grid item xs={2} container direction="row" rowSpacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                      marginBottom: "2em",
                    }}
                  >
                    Request State
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="unopened"
                          onChange={handleRequestStateChange}
                          checked={requestState.unopened.checked}
                        />
                      }
                      label="Unopened"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="callforrecords"
                          onChange={handleRequestStateChange}
                          checked={requestState.callforrecords.checked}
                        />
                      }
                      label="Call for Records"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="review"
                          onChange={handleRequestStateChange}
                          checked={requestState.review.checked}
                        />
                      }
                      label="Records Review"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="signoff"
                          onChange={handleRequestStateChange}
                          checked={requestState.signoff.checked}
                        />
                      }
                      label="Ministry Sign Off"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="closed"
                          onChange={handleRequestStateChange}
                          checked={requestState.closed.checked}
                        />
                      }
                      label="Closed"
                    />
                  </FormGroup>
                </Grid>
              </Grid>

              <Grid item xs={2} container direction="row" rowSpacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                      marginBottom: "2em",
                    }}
                  >
                    Request Status
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="overdue"
                          onChange={handleRequestStatusChange}
                          checked={requestStatus.overdue}
                        />
                      }
                      label="Overdue"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          name="onTime"
                          onChange={handleRequestStatusChange}
                          checked={requestStatus.onTime}
                        />
                      }
                      label="On Time"
                    />
                  </FormGroup>
                </Grid>
              </Grid>

              <Grid item xs={2} container direction="row" rowSpacing={2}>
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
                      label="Personal"
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
                      label="General"
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
                      {programAreaList.map((programArea) => (
                        <MenuItem
                          key={programArea.programareaid}
                          value={programArea.bcgovcode}
                        >
                          <Checkbox
                            checked={
                              selectedPublicBodies.indexOf(
                                programArea.bcgovcode
                              ) > -1
                            }
                          />
                          <ListItemText primary={programArea.name} />
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Grid item xs={12} container direction="row" columnSpacing={2}>
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
                    variant="contained"
                    onClick={handleApplySearchFilters}
                    disabled={searchLoading}
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
                    onClick={handleResetSearchFilters}
                  >
                    Clear All Filters
                  </Button>
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
