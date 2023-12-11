import React, { useState, useContext, useEffect } from "react";
import "../../dashboard.scss";
import { useSelector } from "react-redux";

import Loading from "../../../../../containers/Loading";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
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
import { SearchFilter, DateRangeTypes } from "./enum";
import {
  ConditionalComponent,
  formatDate,
} from "../../../../../helper/FOI/helper";
import { ActionContext } from "./ActionContext";
import { StateEnum } from "../../../../../constants/FOI/statusEnum";

import Tooltip from '../../../customComponents/Tooltip/Tooltip';

import {
  addYears
} from "../../utils";

const DEFAULT_PAGE_SIZE = 100;

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
  MenuListProps: {
    autoFocusItem: false,
  },
};

const useStyles = makeStyles((_theme) => ({
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
  paper: {
    backgroundColor: "#F9FBFD",
  },
  checkboxLabel: {
    marginBottom: 0,
  },
}));

const AdvancedSearch = ({ userDetail }) => {
  const classes = useStyles();

  const {
    handleUpdateSearchFilter,
    searchLoading,
    defaultSortModel,
    advancedSearchComponentLoading,
    setAdvancedSearchComponentLoading,
    setSearchLoading,
    advancedSearchParams,
  } = useContext(ActionContext);

  const programAreaList = useSelector(
    (state) => state.foiRequests.foiProgramAreaList
  );

  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const tooltipContentRight = {
    "title": "Advanced Search",
    "content": "To conduct an Advanced Search using one of the seven filter buttons, you must also enter one or more key words."
  };

  const tooltipContentLeft = {
    "title": "Advanced Search",
    "content": "Use one or more fields from the following sections on their own or to narrow your search: Request State/Status/Type/Flags, Date Range, or Public Body."
  };

  const [searchFilterSelected, setSearchFilterSelected] = useState(advancedSearchParams?.search || null);
  const keywordsMode = searchFilterSelected === SearchFilter.REQUEST_DESCRIPTION;

  const [searchText, setSearchText] = useState(() => {
    if (!keywordsMode && Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.keywords.length > 0) {
      return advancedSearchParams.keywords[0]
    } else {
      return "";
    }
  });
  const [keywords, setKeywords] = useState(() => {
    if (keywordsMode && Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.keywords.length > 0) {
      return advancedSearchParams.keywords;
    } else {
      return [];
    }
  });

  const intitialRequestState = {
    [StateEnum.callforrecords.id]: false,
    [StateEnum.review.id]: false,
    [StateEnum.signoff.id]: false,
    [StateEnum.closed.id]: false,
    [StateEnum.callforrecordsoverdue.id]: false
  };

  const [requestState, setRequestState] = useState(() => {
    if (Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.requestState.length > 0) {
      let savedRequestState = {...intitialRequestState}
      advancedSearchParams.requestState.forEach(state => {
        savedRequestState[state] = true;
      });
      return savedRequestState;
    } else {
      return intitialRequestState;
    }
  });

  const intitialRequestStatus = {
    overdue: false,
    ontime: false,
  };
  
  const [requestStatus, setRequestStatus] = useState(() => {
    if (Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.requestStatus.length > 0) {
      let savedRequestStatus = { ...intitialRequestStatus }
      advancedSearchParams.requestStatus.forEach(status => {
        savedRequestStatus[status] = true;
      });
      return savedRequestStatus;
    } else {
      return intitialRequestStatus;
    }
  });

  const initialRequestTypes = {
    personal: false,
    general: false,
    generaldisabled: false,
  };

  const [requestTypes, setRequestTypes] = useState(() => {
    if (Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.requestType.length > 0) {
      let savedRequestType = {...initialRequestTypes}
      advancedSearchParams.requestType.forEach(type => {
        savedRequestType[type] = true;
      });
      if (advancedSearchParams.search === SearchFilter.APPLICANT_NAME) {
        savedRequestType.generaldisabled = true;
      }
      return savedRequestType;
    } else {
      return initialRequestTypes;
    }
  });

  const initialRequestFlags = {
      restricted: false,
      oipc: false,
      phased: false
    };
  const [requestFlags, setRequestFlags] = useState(() => {
    if (Object.keys(advancedSearchParams).length > 0 && advancedSearchParams.requestFlags.length > 0) {
      let savedRequestFlags = {...initialRequestFlags}
      advancedSearchParams.requestFlags.forEach(type => {
        savedRequestFlags[type] = true;
      });
      return savedRequestFlags;
    } else {
      return initialRequestFlags;
    }
  });
  const [selectedDateRangeType, setSelectedDateRangeType] = useState(advancedSearchParams?.dateRangeType || "");
  const [fromDate, setFromDate] = useState(advancedSearchParams?.fromDate || "");
  const [toDate, setToDate] = useState(advancedSearchParams?.toDate || "");
  const oneYearFromNow = formatDate(addYears(1));
  //default max fromDate - now
  const [maxFromDate, setMaxFromDate] = useState(formatDate(new Date()));
  //default max toDate - 1 year from now
  const [maxToDate, setMaxToDate] = useState(oneYearFromNow);
  const resetDateFields = () => {
    setFromDate("");
    setToDate("");
  }
  const resetMaxFromDate = (dateRangeType) => {
    if(dateRangeType == 'receivedDate' || dateRangeType == 'closedate') {
      setMaxFromDate(formatDate(new Date()));
    }else{
      setMaxFromDate(oneYearFromNow);
    }
  }
  const resetMaxToDate = (dateRangeType) => {
    if(dateRangeType == 'receivedDate' || dateRangeType == 'closedate') {
      setMaxToDate(formatDate(new Date()));
    }else{
      setMaxToDate(oneYearFromNow);
    }
  }

  const [selectedPublicBodies, setSelectedPublicBodies] = useState(advancedSearchParams?.publicBodies || []);

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl) && Boolean(searchText);

  const getTrueKeysFromCheckboxObject = (checkboxObject) => {
    return Object.entries(checkboxObject)
      .map(([key, value]) => {
        if (key !== 'generaldisabled') {
          return value ? key : null;
        }
      })
      .filter((value) => value);
  };
  const handleApplySearchFilters = () => {
    if (!advancedSearchComponentLoading) {
      setAdvancedSearchComponentLoading(true);
    }
    setSearchLoading(true);
    handleUpdateSearchFilter({
      search: searchFilterSelected,
      keywords: keywordsMode ? keywords : [searchText.trim()],
      requestState: getTrueKeysFromCheckboxObject(requestState),
      requestType: getTrueKeysFromCheckboxObject(requestTypes),
      requestFlags: getTrueKeysFromCheckboxObject(requestFlags),
      requestStatus: getTrueKeysFromCheckboxObject(requestStatus),
      dateRangeType: selectedDateRangeType || null,
      fromDate: fromDate || null,
      toDate: toDate || null,
      publicBodies: selectedPublicBodies,
      page: 1,
      size: advancedSearchParams?.size || DEFAULT_PAGE_SIZE,
      sort: defaultSortModel,
      userId: userDetail.preferred_username,
    });
  };

  useEffect(() => {
    if (Object.keys(advancedSearchParams).length > 0) {
        if (!advancedSearchComponentLoading) {
          setAdvancedSearchComponentLoading(true);
        }
        setSearchLoading(true);
        handleUpdateSearchFilter(advancedSearchParams)
      } 
  }, []);

  const noSearchCriteria = () => {
    let selectedRequestStates = getTrueKeysFromCheckboxObject(requestState);
    let selectedRequestTypes = getTrueKeysFromCheckboxObject(requestTypes);
    let selectedRequestFlags = getTrueKeysFromCheckboxObject(requestFlags);
    let selectedRequestStatus = getTrueKeysFromCheckboxObject(requestStatus);
    return ((keywords.length===0 && keywordsMode) || (!searchText && !keywordsMode))
              && !fromDate
              && !toDate
              && selectedPublicBodies.length===0
              && selectedRequestStates.length===0
              && selectedRequestTypes.length===0
              && selectedRequestFlags.length===0
              && selectedRequestStatus.length===0;
  };

  const handleResetSearchFilters = () => {
    setSearchText("");
    setSelectedDateRangeType("");
    setKeywords([]);
    setSearchFilterSelected();
    setRequestState(intitialRequestState);
    setRequestTypes(initialRequestTypes);
    setRequestFlags(initialRequestFlags);
    setRequestStatus(intitialRequestStatus);
    setFromDate("");
    setToDate("");
    setSelectedPublicBodies([]);
  };

  const handleKeywordAdd = () => {
    if (!searchText) {
      return;
    }
    setAnchorEl(null);
    setKeywords([...keywords, searchText.trim()]);
    setSearchText("");
  };

  const handleSearchChange = (e) => {
    setAnchorEl(e.currentTarget);
    setSearchText(e.target.value);
  };

  const clickSearchFilter = (SearchFilterType) => {
    if (SearchFilterType === SearchFilter.APPLICANT_NAME) {
      setRequestTypes({
        personal:true,
        general:false,
        generaldisabled: true
      });
    }
    else {
      setRequestTypes({
        ...requestTypes,
        generaldisabled: false
      });
    }
    if (searchFilterSelected !== SearchFilterType) {
      setSearchFilterSelected(SearchFilterType);
    }
  };

  const handleRequestStateChange = (event) => {
    setRequestState({
      ...requestState,
      [event.target.parentElement.getAttribute('stateid')]: event.target.checked
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

  const handleRequestFlagsChange = (event) => {
    setRequestFlags({
      ...requestFlags,
      [event.target.name]: event.target.checked,
    });
  };

  const handleSelectedDateRangeTypeChange = (event) => {
    const type = event.target.value;
    setSelectedDateRangeType(type);
    resetMaxFromDate(type);
    resetMaxToDate(type);
    resetDateFields();
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
          sx={[
            {
              color: "#38598A",
              border: "1px solid #38598A",
              width: "100%",
            },
          ]}
          variant="outlined"
          {...rest}
        />
      );
    }

    return (
      <Chip
        sx={[
          {
            backgroundColor: "#38598A",
            width: "100%",
          },
          {
            "&:hover": {
              backgroundColor: "#38598A",
            },
          },
        ]}
        {...rest}
      />
    );
  };

  if (isLoading) {
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
              backgroundColor: "#F9FBFD",
              border: "1px solid #38598A",
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
                <label className="hideContent" for="advancedSearch">Search</label>
                <InputBase
                  id="advancedSearch"
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
                      <IconButton sx={{ color: "#38598A" }}>
                        <span className="hideContent">Search</span>
                        <SearchIcon />
                      </IconButton>
                    </InputAdornment>
                  }
                  sx={{
                    color: "#38598A",
                  }}
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
                        setKeywords(keywords.filter((_kw, i) => index !== i));
                      }}
                      color="primary"
                      sx={{
                        backgroundColor: "#38598A",
                        margin: "1px",
                      }}
                      size="small"
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
                  variant="h6"
                >
                  Filter by
                </Typography>
              </Grid>
              <Grid container xs={12}>
                <Grid item xs>
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

                <Grid item xs>
                  <ClickableChip
                    key={`filter-raw-request`}
                    label={"ID NUMBER"}
                    color="primary"
                    onClick={() => clickSearchFilter(SearchFilter.ID_NUM)}
                    clicked={searchFilterSelected === SearchFilter.ID_NUM}
                  />
                </Grid>

                <Grid item xs>
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

                <Grid item xs>
                  <ClickableChip
                    key={`filter-applicant-name`}
                    label={"APPLICANT NAME"}
                    color="primary"
                    onClick={() => clickSearchFilter(SearchFilter.APPLICANT_NAME)}
                    clicked={searchFilterSelected === SearchFilter.APPLICANT_NAME}
                  />
                </Grid>

                <Grid item xs>
                  <ClickableChip
                    key={`filter-assignee-name`}
                    label={"ASSIGNEE NAME"}
                    color="primary"
                    onClick={() => clickSearchFilter(SearchFilter.ASSIGNEE_NAME)}
                    clicked={searchFilterSelected === SearchFilter.ASSIGNEE_NAME}
                  />
                </Grid>

                <Grid item xs>
                  <ClickableChip
                    key={`filter-search-filter`}
                    label={"SUBJECT CODE"}
                    color="primary"
                    onClick={() => clickSearchFilter(SearchFilter.SUBJECT_CODE)}
                    clicked={searchFilterSelected === SearchFilter.SUBJECT_CODE}
                  />
                </Grid>
                
                <Grid item xs>
                  <ClickableChip
                    key={`filter-oipc-number`}
                    label={"OIPC NUMBER"}
                    color="primary"
                    onClick={() => clickSearchFilter(SearchFilter.OIPC_NUMBER)}
                    clicked={searchFilterSelected === SearchFilter.OIPC_NUMBER}
                  />
                </Grid>
              </Grid>

              <Grid item xs={2} container direction="row" rowSpacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                    variant="h6"
                  >
                    Request State
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="callforrecords"
                          stateid={StateEnum.callforrecords.id}
                          onChange={handleRequestStateChange}
                          checked={requestState[StateEnum.callforrecords.id]}
                          color="success"
                        />
                      }
                      label="Call for Records"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="review"
                          stateid={StateEnum.review.id}
                          onChange={handleRequestStateChange}
                          checked={requestState[StateEnum.review.id]}
                          color="success"
                        />
                      }
                      label="Records Review"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="signoff"
                          stateid={StateEnum.signoff.id}
                          onChange={handleRequestStateChange}
                          checked={requestState[StateEnum.signoff.id]}
                          color="success"
                        />
                      }
                      label="Ministry Sign Off"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="closed"
                          stateid={StateEnum.closed.id}
                          onChange={handleRequestStateChange}
                          checked={requestState[StateEnum.closed.id]}
                          color="success"
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
                    }}
                    variant="h6"
                  >
                    Request Status
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="overdue"
                          onChange={handleRequestStatusChange}
                          checked={requestStatus.overdue}
                          color="success"
                        />
                      }
                      label="Overdue"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="ontime"
                          onChange={handleRequestStatusChange}
                          checked={requestStatus.ontime}
                          color="success"
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
                    variant="h6"
                  >
                    Request Type
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="personal"
                          onChange={handleRequestTypeChange}
                          checked={requestTypes.personal}
                          color="success"
                          disabled={requestTypes.generaldisabled}
                        />
                      }
                      label="Personal"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="general"
                          onChange={handleRequestTypeChange}
                          checked={requestTypes.general}
                          color="success"
                          disabled={requestTypes.generaldisabled}
                        />
                      }
                      label={<div style={{display: "flex"}}>General {requestTypes.generaldisabled ? <p style={{color: "#ff0000",fontSize: "0.8rem",lineHeight: "1.6"}}> * </p>: ""}</div>}                      
                    />
                  </FormGroup>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                    variant="h6"
                  >
                    Request Flags
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormGroup>
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="restricted"
                          onChange={handleRequestFlagsChange}
                          checked={requestFlags.restricted}
                          color="success"
                        />
                      }
                      label="Restricted"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="oipc"
                          onChange={handleRequestFlagsChange}
                          checked={requestFlags.oipc}
                          color="success"
                        />
                      }
                      label="OIPC"
                    />
                    <FormControlLabel
                      className={classes.checkboxLabel}
                      control={
                        <Checkbox
                          size="small"
                          name="phased"
                          onChange={handleRequestFlagsChange}
                          checked={requestFlags.phased}
                          color="success"
                        />
                      }
                      label="Phased"
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
                    variant="h6"
                  >
                    Search by Date Range
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel id="date-type-label" shrink>
                      Type of Date Range
                    </InputLabel>
                    <Select
                      labelId="date-type-label"
                      id="date-type"
                      displayEmpty
                      value={selectedDateRangeType}
                      onChange={handleSelectedDateRangeTypeChange}
                      inputProps={{ "aria-labelledby": "date-type-label"}}
                      input={<OutlinedInput label="Type of Date Range" notched />}
                    >
                      <MenuItem disabled value="" key="date-range-type-default">
                        <em>Select Type of Date Range</em>
                      </MenuItem>
                      {DateRangeTypes.map((dateRangeType) => (
                        <MenuItem
                          key={`date-range-type-${dateRangeType.name}`}
                          value={dateRangeType.name}
                        >
                          {dateRangeType.value}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid
                  container
                  item
                  direction="row"
                  justifyContent="flex-start"
                  alignItems="center"
                  xs={12}
                  sx={{
                    mb: "1em",
                  }}
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
                      value={fromDate || ""}
                      InputProps={{
                        inputProps: {
                          max: formatDate(toDate) || maxFromDate,
                        },
                      }}
                      onChange={(e) => setFromDate(formatDate(e.target.value))}
                      disabled={!selectedDateRangeType}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={2}>
                    <Typography
                      align="center"
                      sx={{
                        fontWeight: "bold",
                      }}
                      variant="h6"
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
                          min: formatDate(fromDate),
                          max: maxToDate
                        },
                      }}
                      value={toDate || ""}
                      onChange={(e) => setToDate(formatDate(e.target.value))}
                      disabled={!selectedDateRangeType}
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
                    variant="h6"
                  >
                    Search by Public Body
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel id="public-body-label" shrink>
                      Public Body
                    </InputLabel>
                    <Select
                      labelId="public-body-label"
                      id="public-body-checkbox"
                      multiple
                      displayEmpty
                      value={selectedPublicBodies}
                      onChange={handleSelectedPublicBodiesChange}
                      inputProps={{ "aria-labelledby": "public-body-label"}}
                      input={<OutlinedInput label="Public Body" notched />}
                      renderValue={(selected) => {
                        if (programAreaList?.length === 1) {
                          return programAreaList[0].bcgovcode;
                        }
                        if (selected.length === 0) {
                          return <em>All</em>;
                        }

                        return selected.join(", ");
                      }}
                      MenuProps={MenuProps}
                      disabled={programAreaList.length === 1}
                    >
                      <MenuItem disabled value="" key="program-area-all">
                        <em>All</em>
                      </MenuItem>
                      {programAreaList.map((programArea) => (
                        <MenuItem
                          key={`program-area-${programArea.programareaid}`}
                          value={programArea.bcgovcode}
                        >
                          <Checkbox
                            checked={
                              selectedPublicBodies.indexOf(
                                programArea.bcgovcode
                              ) > -1
                            }
                            color="success"
                          />
                          <ListItemText
                            primary={programArea.name}
                            key={`program-area-label-${programArea.programareaid}`}
                          />
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Typography
                      sx={{
                        color: "#ff0000",
                        fontSize: "0.8rem",
                        lineHeight: "1.6",
                      }}
                      visibility={!requestTypes.generaldisabled ? "hidden" : "visible"}
                    >
                      * You are unable to search General Requests with Applicant Name Selected. <br/>
                      Deselect Applicant Name Search Filter if you wish to search General Requests.
                    </Typography>
                </Grid>
              </Grid>

              <Grid item xs={12} container direction="row" columnSpacing={1}>
                <Grid item>
                  <Button
                    color="primary"
                    sx={{
                      backgroundColor: "#38598A",
                      color: "white",
                      fontWeight: "bold",
                      textTransform: "none",
                    }}
                    variant="contained"
                    onClick={handleApplySearchFilters}
                    disabled={searchLoading || noSearchCriteria() || ((searchText || keywords.length>0) && !searchFilterSelected ) }
                    disableElevation
                  >
                    Apply Search
                  </Button>
                </Grid>
                <Grid item>
                  <Button
                    variant="outlined"
                    sx={{
                      color: "#38598A",
                      border: "1px solid #38598A",
                      fontWeight: "bold",
                      textTransform: "none",
                    }}
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
      <Grid className="floatAboveEverythingLeft">
        <Tooltip content={tooltipContentLeft} position={"bottom right"}/>
        <p className="hideContent" id="popup-6">Information1</p>
      </Grid>
      <Grid className="floatAboveEverything">
        <Tooltip content={tooltipContentRight} />
        <p className="hideContent" id="popup-6">Information</p>
      </Grid>
    </>
  );
};

export default AdvancedSearch;
