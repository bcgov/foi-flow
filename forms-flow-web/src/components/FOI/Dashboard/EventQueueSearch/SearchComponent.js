import { useState, useContext } from "react";
import "../dashboard.scss";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import { DateRangeTypes } from "./enum";
import { formatDate } from "../../../../helper/FOI/helper";
import { ActionContext } from "./ActionContext";
import { addYears } from "../utils";
import { makeStyles } from "@material-ui/core/styles";

const DEFAULT_PAGE_SIZE = 100;
const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;

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

const EventQueueSearch = ({ userDetail }) => {
  const classes = useStyles();

  const {
    handleUpdateSearchFilter,
    eventSearchParams,
    defaultSortModel,
  } = useContext(ActionContext);

  const [selectedDateRangeType, setSelectedDateRangeType] = useState(
    eventSearchParams?.dateRangeType || ""
  );
  const [fromDate, setFromDate] = useState(eventSearchParams?.fromDate || "");
  const [toDate, setToDate] = useState(eventSearchParams?.toDate || "");
  const oneYearFromNow = formatDate(addYears(1));
  const [maxFromDate, setMaxFromDate] = useState(formatDate(new Date()));
  const [maxToDate, setMaxToDate] = useState(oneYearFromNow);

  const resetMaxFromDate = (dateRangeType) => {
    setMaxFromDate(dateRangeType === "eventDate" ? formatDate(new Date()) : oneYearFromNow);
  };

  const resetMaxToDate = (dateRangeType) => {
    setMaxToDate(dateRangeType === "eventDate" ? formatDate(new Date()) : oneYearFromNow);
  };

  const handleApplySearchFilters = () => {
    handleUpdateSearchFilter({
      dateRangeType: selectedDateRangeType || null,
      fromDate: fromDate || null,
      toDate: toDate || null,
      page: 1,
      size: eventSearchParams?.size || DEFAULT_PAGE_SIZE,
      sort: defaultSortModel,
      userId: userDetail.preferred_username
    });
  };

  const handleResetSearchFilters = () => {
    setSelectedDateRangeType("");
    setFromDate("");
    setToDate("");
  };

  const disableApplySearch = () => {
    return !selectedDateRangeType || !fromDate || !toDate;
  }

  return (
    <Grid item container xs={12} >
      <Grid item xs={12}>
        <Paper component={Grid} sx={{ display: "flex", width: "100%", backgroundColor: "#F9FBFD", border: "1px solid #38598A" }} alignItems="flex-start" direction="row" container>
          <Grid item xs={6} container direction="row" spacing={2} className={classes.searchBody}>
            <Grid item xs={12}>
              <Typography sx={{ fontWeight: "bold" }} variant="h6">Search By Event Date</Typography>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="date-type-label" required={true} shrink>Type of Date Range</InputLabel>
                <Select labelId="date-type-label" id="date-type" displayEmpty value={selectedDateRangeType} onChange={(e) => {
                    setSelectedDateRangeType(e.target.value);
                    resetMaxFromDate(e.target.value);
                    resetMaxToDate(e.target.value);
                  }} inputProps={{ "aria-labelledby": "date-type-label" }} input={<OutlinedInput label="Type of Date Range" notched />}>
                  <MenuItem disabled value=""><em>Select Type of Date Range</em></MenuItem>
                  {DateRangeTypes.map((dateRangeType) => (
                    <MenuItem key={`date-range-type-${dateRangeType.name}`} value={dateRangeType.name}>{dateRangeType.value}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid container item direction="row"  justifyContent="flex-start" alignItems="center" xs={12} sx={{ mb: "1em"}}>
              <Grid item xs={5}>
                <TextField id="from-date" label="From" required={true} type="date" InputLabelProps={{ shrink: true }} variant="outlined" value={fromDate || ""} InputProps={{ inputProps: { max: formatDate(toDate) || maxFromDate } }} onChange={(e) => setFromDate(formatDate(e.target.value))} disabled={!selectedDateRangeType} fullWidth />
              </Grid>
              <Grid item xs={2}>
                <Typography align="center" sx={{ fontWeight: "bold" }} variant="h6">to</Typography>
              </Grid>
              <Grid item xs={5}>
                <TextField id="to-date" label="To" required={true} type="date" InputLabelProps={{ shrink: true }} InputProps={{ inputProps: { min: formatDate(fromDate), max: maxToDate } }} value={toDate || ""} onChange={(e) => setToDate(formatDate(e.target.value))} disabled={!selectedDateRangeType} variant="outlined" fullWidth />
              </Grid>
            </Grid>

            <Grid item xs={12} container direction="row" columnSpacing={1}>
              <Grid item>
                <Button color="primary" disabled={disableApplySearch()} sx={{ backgroundColor: "#38598A", color: "white", fontWeight: "bold", textTransform: "none" }} variant="contained" onClick={handleApplySearchFilters} disableElevation>
                  Apply Search
                </Button>
              </Grid>
              <Grid item>
                <Button variant="outlined" sx={{ color: "#38598A", border: "1px solid #38598A", fontWeight: "bold", textTransform: "none",}} onClick={handleResetSearchFilters}>
                  Clear All Filters
                </Button>
              </Grid>
             </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default EventQueueSearch;
