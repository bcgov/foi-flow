import React, { useEffect, useState, useContext } from "react";
import "../../dashboard.scss";
import { useSelector,useDispatch } from "react-redux";

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
import Box from "@mui/material/Box";
import InputAdornment from "@mui/material/InputAdornment";

import OutlinedInput from "@mui/material/OutlinedInput";
import InputLabel from "@mui/material/InputLabel";
import FormControl from "@mui/material/FormControl";
import ListItemText from "@mui/material/ListItemText";
import Select from "@mui/material/Select";
import {
  ConditionalComponent,
  formatDate,
} from "../../../../../helper/FOI/helper";
import { ActionContext } from "./ActionContext";
import Tooltip from '../../../customComponents/Tooltip/Tooltip';

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
    backgroundColor: "#95c3ffc7",
    margin: "1px",
    height: "22px",
    fontSize: "13px",
    "& .MuiChip-deleteIcon": {
      fontSize: "16px", // Adjust icon size
    },
  },
  paper: {
    backgroundColor: "#F9FBFD",
  },
  checkboxLabel: {
    marginBottom: 0,
  },
}));

const KeywordSearch = ({ userDetail }) => {
  const classes = useStyles();

  const {
    handleUpdateSearchFilter,
    searchLoading,
    setKeywordSearchLoading,
    defaultSortModel,
    keywordSearchComponentLoading,
    setKeywordSearchComponentLoading,
    keywordSearchParams,
  } = useContext(ActionContext);

  const programAreaList = useSelector(
    (state) => state.foiRequests.foiProgramAreaList
  );

  const isLoading = useSelector((state) => state.foiRequests.isLoading);

  const tooltipContentLeft = {
    "title": "Keyword Search",
    "content": "Use one or more fields from the following sections on their own or to narrow your search: Received Date Range, or Public Body."
  };

  const [fromDate, setFromDate] = useState(keywordSearchParams?.fromDate || "");
  const [toDate, setToDate] = useState(keywordSearchParams?.toDate || "");
  //default max fromDate - now
  const [maxFromDate, setMaxFromDate] = useState(formatDate(new Date()));
  const [maxToDate, setMaxToDate] = useState(formatDate(new Date()));
  const [selectedPublicBodies, setSelectedPublicBodies] = useState(keywordSearchParams?.publicBodies || []);

  console.log("keywordSearchParams:",keywordSearchParams)
  const [keywords, setKeywords] = useState(() => {
    if (keywordSearchParams != null && keywordSearchParams != undefined && Object.keys(keywordSearchParams).length > 0 && keywordSearchParams.keywords.length > 0) {
      return keywordSearchParams.keywords;
    } else {
      return [];
    }
  });

  const [searchText, setSearchText] = useState(() => {
    if (keywordSearchParams != null && keywordSearchParams != undefined && Object.keys(keywordSearchParams).length > 0 && 
      keywordSearchParams.keywords.length > 0 && keywords.length <=0) {
      return keywordSearchParams.keywords[0]
    } else {
      return "";
    }
  });


  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl) && Boolean(searchText);
  const [error, setError] = useState(false);


  // const resetDateFields = () => {
  //   setFromDate("");
  //   setToDate("");
  // }
  // const resetMaxFromDate = () => {
  //   setMaxFromDate(formatDate(new Date()));
  // }
  // const resetMaxToDate = () => {
  //   setMaxToDate(formatDate(new Date()));
  // }

  const getTrueKeysFromCheckboxObject = (checkboxObject) => {
    return Object.entries(checkboxObject)
      .map(([key, value]) => {
        if (value instanceof Object) {
          return value.checked ? value.id : null;
        }
        return value ? key : null;
      })
      .filter((value) => value);
  };

  const handleApplySearchFilters = () => {
    if (!keywordSearchComponentLoading) {
      setKeywordSearchComponentLoading(true);
    }
    setKeywordSearchLoading(true);
    handleUpdateSearchFilter({
      //search: searchFilterSelected,
      keywords: keywords, //keywordsMode ? keywords : [searchText.trim()],
      fromDate: fromDate || null,
      toDate: toDate || null,
      publicBodies: selectedPublicBodies,
      page: 1,
      size: keywordSearchParams?.size || DEFAULT_PAGE_SIZE,
      sort: defaultSortModel,
      userId: userDetail.preferred_username,
    });    
  };

 
  const handleSearch = () =>{
    // getCrossTextSearchAuth({
    //   callback: (data) => {
    //   console.log("!!!!",data)
    // },
    // errorCallback: (error) => {
    //   console.log("!!!!",error)
    // },
    // dispatch,})
    //NEEDED
    handleApplySearchFilters();
  }

  useEffect(() => {
    if (keywordSearchParams != null && keywordSearchParams != undefined && Object.keys(keywordSearchParams).length > 0) {
        if (!keywordSearchComponentLoading) {
          setKeywordSearchComponentLoading(true);
        }
        setKeywordSearchLoading(true);
        handleUpdateSearchFilter(keywordSearchParams)
    } 
  }, []);

  // const noSearchCriteria = () => {
  //   return (keywords.length===0  || !searchText)
  //             && !fromDate
  //             && !toDate
  //             && selectedPublicBodies.length===0
  // };

  const handleResetSearchFilters = () => {
    setSearchText("");
    setKeywords([]);
    setFromDate("");
    setToDate("");
    setSelectedPublicBodies([]);
  };

  const handleKeywordAdd = () => {
    if (!searchText) {
      return;
    }
    if (keywords.length >= 10) {
      setError(true); // Show error message and turn bar red
      return;
    }
    if (searchText.trim() && !keywords.includes(searchText.trim())) {
      setKeywords([...keywords, searchText.trim()]);
    }
    setAnchorEl(null);
    setKeywords([...keywords, searchText.trim()]);
    setSearchText("");
    setError(false); // Reset error if it was active
  };

  const handleSearchChange = (e) => {
    setAnchorEl(e.currentTarget);
    setSearchText(e.target.value);
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


  //Remove a keyword bubble
  const handleKeywordDelete = (keywordToDelete) => {
    let updatedKeywordList= keywords.filter((keyword) => keyword !== keywordToDelete)
    setKeywords(updatedKeywordList);
    if (updatedKeywordList.length >= 10)
      setError(true);
    else
      setError(false);
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
    {error && (
        <Typography
          sx={{
            color: "red",
            margin: "0px 20px 8px" ,
            fontSize: "12px",
          }}
        >
          You can only search up to 10 keywords at a time
        </Typography>
      )}
      <Grid item container xs={12} 
        sx={{
              paddingTop:"0px !important"
        }}>
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
              <Grid item xs={12}>
                <label className="hideContent" for="keywordSearch">
                  Search keywords...
                </label>
                <Box sx={{ position: "relative", width: "100%" }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      flexWrap: "wrap",
                      padding: "4px",
                      border: "1px solid",
                      borderColor: error ? "red" : "#ccc", // Turn red if error
                      borderRadius: "4px",
                    }}
                  >
                  {/* Search Input */}
                  <InputBase
                    id="keywordSearch"
                    name="keywordSearch"
                    placeholder="Search Keywords..."
                    onChange={handleSearchChange}
                    value={searchText}
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleKeywordAdd();
                      }
                    }}
                    sx={{
                      flex: 1,
                      minWidth: "120px",
                      color: "#38598A",
                    }}
                    startAdornment={
                      <InputAdornment position="start">
                        <IconButton sx={{ color: "#38598A" }}>
                          <span className="hideContent">Search keywords...</span>
                          <SearchIcon />
                        </IconButton>
                        {keywords.map((keyword, index) => (
                          <Chip
                            key={index}
                            label={keyword}
                            onDelete={() => handleKeywordDelete(keyword)}
                            className={classes.chip}
                            sx={{
                              backgroundColor: "#95c3ffc7",
                              margin: "1px",
                              height: "22px",
                              fontSize: "13px",
                              "& .MuiChip-deleteIcon": {
                                fontSize: "16px", // Adjust icon size
                              },
                            }}
                            //sx={{ margin: "4px 4px 4px 0" }}
                          />
                        ))}
                      </InputAdornment>
                    }
                  />
                  </Box>
                </Box>
              </Grid>
              {/* <ConditionalComponent>
                <Grid item container direction="row-reverse" xs={12}>
                  {keywords.map((keyword, index) => (
                    <Chip
                      key={`keyword-${index}`}
                      label={keyword}
                      onDelete={() => {
                        setKeywords(keywords.filter((_kw, i) => index !== i));
                      }}
                      color="primary"
                      className={classes.chip}
                      sx={{
                        backgroundColor: "#95c3ff",
                        margin: "1px",
                        height: "20px"
                      }}
                      size="small"
                    />
                  ))}
                </Grid>
              </ConditionalComponent> */}
            </Grid>
            <ConditionalComponent>
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
              <Grid item xs={6} container direction="row" spacing={2}>
                <Grid item xs={12}>
                  <Typography
                    sx={{
                      fontWeight: "bold",
                    }}
                    variant="h6"
                  >
                    Search by Received Date
                  </Typography>
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
                      //disabled={!selectedDateRangeType}
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
                          max: maxToDate,
                        },
                      }}
                      value={toDate || ""}
                      onChange={(e) => setToDate(formatDate(e.target.value))}
                      //disabled={!selectedDateRangeType}
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
                      inputProps={{ "aria-labelledby": "public-body-label" }}
                      input={<OutlinedInput label="Public Body" notched />}
                      renderValue={(selected) => {
                        if (selected.length === 0) {
                          return <em>All</em>;
                        }

                        return selected.join(", ");
                      }}
                      MenuProps={MenuProps}
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
              </Grid>

              <Grid item xs={12} container direction="row" rowSpacing={2} columnSpacing={1}
              sx={{ paddingTop: "30px" }}>
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
                    onClick={handleSearch}
                    disabled={
                      searchLoading ||
                      keywords.length <= 0
                    }
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
        <Tooltip content={tooltipContentLeft} position={"bottom right"} />
        <p className="hideContent" id="popup-6">
          Information1
        </p>
      </Grid>
    </>
  );
};

export default KeywordSearch;
