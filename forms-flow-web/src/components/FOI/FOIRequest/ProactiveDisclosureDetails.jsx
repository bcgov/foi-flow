import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import { makeStyles } from "@material-ui/styles";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import Popover from "@material-ui/core/Popover";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import InputAdornment from "@material-ui/core/InputAdornment";
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { fetchFOIProactiveDisclosureCategoryList } from "../../../apiManager/services/FOI/foiMasterDataServices";
import QuarterSelector from "./QuarterSelector";
import MonthSelector from "./MonthSelector";
import YearSelector from "./YearSelector";

const useStyles = makeStyles((theme) => ({
  heading: {
    color: "#FFF",
    fontSize: "16px !important",
    fontWeight: "bold !important",
  },

  accordionSummary: {
    flexDirection: "row-reverse",
  },

  popoverContent: {
    padding: 10,
  },

  tabs: {
    borderBottom: "1px solid #e8e8e8",
  },

  tabIndicator: {
    backgroundColor: "#000 !important",
    height: "3px",
  },

  tabRoot: {
    textTransform: "none",
    minWidth: 0,
    fontWeight: 400,
    flex: 1,
    maxWidth: "none",
    marginRight: 0,
    marginLeft: 0,

    "&:hover": {
      color: "#000",
      opacity: 1,
    },

    "&.tabSelected": {
      color: "#000",
      fontWeight: "bold",
    },

    "&:focus": {
      color: "#000",
    }
  }
}));


const ProactiveDisclosureDetails = React.memo(
  ({
    requestDetails,
    handleRequestDetailsValue,
    handleRequestDetailsInitialValue,
    handleProactiveDetailsValue,
    handleProactiveDetailsInitialValue,
    createSaveRequestObject,
    disableInput,
    saveRequestObject,
  }) => {
    const dispatch = useDispatch();
    const classes = useStyles();
    // Get master data from Redux store
    const requestTypes = useSelector(
      (state) => state.foiRequests.foiRequestTypeList || []
    );
    const categoryTypes = useSelector(
      (state) => state.foiRequests.foiProactiveDisclosureCategoryList || []
    );
    // const reportPeriods = useSelector(
    //   (state) => state.foiRequests.foiReportPeriodList || []
    // );

    useEffect(() => {
      dispatch(fetchFOIProactiveDisclosureCategoryList());
    }, []);

    const validateField = (request, fieldName, value) => {
      if (!request) return value || "";
      switch (fieldName) {
        case "requestType":
          return request.requestType || "Select Request Type";
        case "proactiveDisclosureCategory":
          return request.proactiveDisclosureCategory || "Select a Category";
        case "reportPeriod":
          return request.reportPeriod || "Select a Report Period";
        case "startDate":
          return request.startDate ? formatDate(request.startDate) : "";
        case "cfrDueDate":
          return request.cfrDueDate || "";
        case "earliestEligiblePublicationDate":
          return request.earliestEligiblePublicationDate
            ? formatDate(request.earliestEligiblePublicationDate)
            : "";
        default:
          return "";
      }
    };

    useEffect(() => {
      const initialRequestType = validateField(
        saveRequestObject,
        FOI_COMPONENT_CONSTANTS.REQUEST_TYPE
      );
      setSelectedRequestType(initialRequestType);
      const requestDetailsObject = {
        requestType: initialRequestType,
      };

      handleRequestDetailsInitialValue?.(requestDetailsObject);
    }, [saveRequestObject]);

    // Initialize form values
    useEffect(() => {
      //const initialRequestType = validateField(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE);
      const initialCategoryType = validateField(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.PROACTIVE_DISCLOSURE_CATEGORY,
        {
          dateFormat: false,
          defaultValue: "Select a Category",
        }
      );
      const initialReportPeriod = validateField(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.REPORT_PERIOD,
        {
          dateFormat: false,
          defaultValue: "Select a Report Period",
        }
      );
      //const startDate = !!requestDetails.requestProcessStart ? formatDate(request.requestProcessStart) : "";
      const initialStartDate = requestDetails?.requestProcessStart
        ? formatDate(requestDetails.requestProcessStart)
        : validateField(requestDetails, "startDate");
      const initialCfrDueDate = validateField(requestDetails, "cfrDueDate");
      const initialEarliestPublicationDate = validateField(
        requestDetails,
        "earliestEligiblePublicationDate"
      );

      //setSelectedRequestType(initialRequestType);
      setSelectedProactiveCategory(initialCategoryType);
      setSelectedReportPeriod(initialReportPeriod);
      setStartDate(initialStartDate);
      setCfrDueDate(initialCfrDueDate);
      setEarliestEligiblePublicationDate(initialEarliestPublicationDate);

      const disclosureDetailsObject = {
        proactiveDisclosureCategory: initialCategoryType,
        reportPeriod: initialReportPeriod,
        requestStartDate: initialStartDate,
        cfrDueDate: initialCfrDueDate,
        earliestEligiblePublicationDate: initialEarliestPublicationDate,
      };

      handleProactiveDetailsInitialValue?.(disclosureDetailsObject);
      createSaveRequestObject?.(
        FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES,
        disclosureDetailsObject
      );
    }, [requestDetails, handleRequestDetailsInitialValue]);

    const [selectedRequestType, setSelectedRequestType] = useState(
      validateField(saveRequestObject, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE)
    );
    const [selectedProactiveCategory, setSelectedProactiveCategory] = useState(
      validateField(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.PROACTIVE_DISCLOSURE_CATEGORY,
        {
          dateFormat: false,
          defaultValue: "Select a Category",
        }
      )
    );
    const [selectedReportPeriod, setSelectedReportPeriod] = useState(
      validateField(requestDetails, FOI_COMPONENT_CONSTANTS.REPORT_PERIOD, {
        dateFormat: false,
        defaultValue: "Select a Report Period",
      })
    );
    const [startDate, setStartDate] = useState("");
    const [cfrDueDate, setCfrDueDate] = useState("");
    const [earliestEligiblePublicationDate, setEarliestEligiblePublicationDate] = useState("");

    const [anchorEl, setAnchorEl] = useState(null);
    const [tabValue, setTabValue] = useState(0);

    const handleReportPeriodClick = (event) => {
      if (disableInput) return;
      setAnchorEl(event.currentTarget);
      const isQuarter = selectedReportPeriod?.toLowerCase().includes("quarter");
      const isYearly = selectedReportPeriod && (/^\d{4}$/.test(selectedReportPeriod));
      let initialTab = 0;
      if (isQuarter) initialTab = 1;
      if (isYearly) initialTab = 2;
      setTabValue(initialTab);
    };

    const handlePopoverClose = () => {
      setAnchorEl(null);
    };

    const handleTabChange = (event, newValue) => {
      setTabValue(newValue);
    };

    const handlePeriodUpdate = (date, period) => {
      if (period) handleReportPeriodChange({ target: { value: period } });
      handlePopoverClose();
    };

    const getReportPeriodDisplay = (period) => {
      if (!period) return "";
      return period;
    };

    // Event handlers
    const handleRequestTypeChange = (e) => {
      const value = e.target.value;
      setSelectedRequestType(value);
      handleRequestDetailsValue?.(value, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE);
      createSaveRequestObject?.(FOI_COMPONENT_CONSTANTS.REQUEST_TYPE, value);
    };

    const handleProactiveCategoryChange = (e) => {
      const value = e.target.value;
      setSelectedProactiveCategory(value);
      handleProactiveDetailsValue?.(
        value,
        FOI_COMPONENT_CONSTANTS.PROACTIVE_DISCLOSURE_CATEGORY
      );
      createSaveRequestObject?.(
        FOI_COMPONENT_CONSTANTS.PROACTIVE_DISCLOSURE_CATEGORY,
        value
      );
    };

    const handleReportPeriodChange = (e) => {
      const value = e.target.value;
      setSelectedReportPeriod(value);
      handleProactiveDetailsValue?.(
        value,
        FOI_COMPONENT_CONSTANTS.REPORT_PERIOD
      );
      createSaveRequestObject?.(FOI_COMPONENT_CONSTANTS.REPORT_PERIOD, value);
    };

    const handleCFRDueDateChange = (e) => {
      const value = e.target.value;
      setCfrDueDate(value);
      handleProactiveDetailsValue?.(value, "cfrDueDate");
      createSaveRequestObject?.("cfrDueDate", value);
    };

    const handleStartDateChange = (e) => {
      const value = e.target.value;
      setStartDate(value);
      handleProactiveDetailsValue?.(value, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE);
      createSaveRequestObject?.(FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, value);
    };

    const handleEarliestPublicationDateChange = (e) => {
      const value = e.target.value;
      setEarliestEligiblePublicationDate(value);
      handleProactiveDetailsValue?.(value, "earliestEligiblePublicationDate");
      createSaveRequestObject?.("earliestEligiblePublicationDate", value);
      // Keep publicationDate in sync with earliestEligiblePublicationDate
      handleProactiveDetailsValue?.(value, "publicationDate");
      createSaveRequestObject?.("publicationDate", value);
    };

    const requestTypeMenuItems = requestTypes.map((item) => (
      <MenuItem
        key={item.name}
        value={item.name}
        disabled={item.name.toLowerCase().includes("select")}
      >
        {item.name}
      </MenuItem>
    ));

    const categoryTypeMenuItems = categoryTypes.map((item) => (
      <MenuItem
        key={item.name}
        value={item.name}
      >
        {item.name}
      </MenuItem>
    ));


    return (
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className="accordionSummary"
            expandIcon={<ExpandMoreIcon />}
            id="proactiveDisclosureDetails-header"
          >
            <Typography className="heading">
              PROACTIVE DISCLOSURE DETAILS
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div style={{ width: "100%" }}>
              <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">
                  <TextField
                    id="requestType"
                    label="Request Type"
                    inputProps={{ "aria-labelledby": "requestType-label" }}
                    InputLabelProps={{ shrink: true }}
                    select
                    value={selectedRequestType}
                    onChange={handleRequestTypeChange}
                    variant="outlined"
                    fullWidth
                    required
                    disabled={disableInput}
                    error={selectedRequestType.toLowerCase().includes("select")}
                  >
                    {requestTypeMenuItems}
                  </TextField>

                  <TextField
                    id="reportPeriod"
                    label="Report Period"
                    inputProps={{ "aria-labelledby": "reportPeriod-label" }}
                    InputLabelProps={{ shrink: true }}
                    // select // Removed select to use custom Popover
                    value={getReportPeriodDisplay(selectedReportPeriod)}
                    // onChange={handleReportPeriodChange} // Controlled by Popover
                    variant="outlined"
                    fullWidth
                    required
                    disabled={disableInput}
                    error={selectedReportPeriod
                      ?.toLowerCase()
                      ?.includes("select") || selectedReportPeriod === "N/A"}
                    InputProps={{
                      readOnly: true,
                      endAdornment: (
                        <InputAdornment position="end">
                          <ExpandMoreIcon style={{ color: disableInput ? "rgba(0, 0, 0, 0.26)" : "#757575", cursor: "pointer", pointerEvents: "auto" }} />
                        </InputAdornment>
                      ),
                    }}
                    onClick={handleReportPeriodClick}
                  />

                  <Popover
                    open={Boolean(anchorEl)}
                    anchorEl={anchorEl}
                    onClose={handlePopoverClose}
                    anchorOrigin={{
                      vertical: 'bottom',
                      horizontal: 'left',
                    }}
                    transformOrigin={{
                      vertical: 'top',
                      horizontal: 'left',
                    }}
                    PaperProps={{
                      style: { width: '590px', padding: '0px' }
                    }}
                  >
                    <Tabs
                      value={tabValue}
                      onChange={handleTabChange}
                      variant="fullWidth"
                      aria-label="report period tabs"
                      className={classes.tabs}
                      classes={{ indicator: classes.tabIndicator }}
                      indicatorColor="primary"
                      textColor="inherit"
                    >
                      <Tab
                        label="Monthly"
                        classes={{ root: classes.tabRoot, selected: classes.tabSelected }}
                      />
                      <Tab
                        label="Quarterly"
                        classes={{ root: classes.tabRoot, selected: classes.tabSelected }}
                      />
                      <Tab
                        label="Yearly"
                        classes={{ root: classes.tabRoot, selected: classes.tabSelected }}
                      />
                    </Tabs>
                    <div className="tabContent" style={{ padding: '10px', height: '400px' }}>
                      {tabValue === 0 && (
                        <MonthSelector
                          date={startDate}
                          selectedMonth={selectedReportPeriod}
                          onUpdate={handlePeriodUpdate}
                        />
                      )}
                      {tabValue === 1 && (
                        <QuarterSelector
                          date={startDate}
                          selectedQuarter={selectedReportPeriod}
                          onUpdate={handlePeriodUpdate}
                        />
                      )}
                      {tabValue === 2 && (
                        <YearSelector
                          date={startDate}
                          selectedYear={selectedReportPeriod}
                          onUpdate={handlePeriodUpdate}
                        />
                      )}
                    </div>
                  </Popover>

                  <TextField
                    id="cfrDueDate"
                    label="CFR Due Date"
                    type="date"
                    value={cfrDueDate}
                    onChange={handleCFRDueDateChange}
                    inputProps={{
                      "aria-labelledby": "cfrDueDate-label",
                      // max: formatDate(new Date()),
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
                    error={cfrDueDate == undefined || cfrDueDate === ""}
                    required
                  />
                </div>

                <div className="col-lg-6 foi-details-col">
                  <TextField
                    id="categoryType"
                    label="Category Type"
                    inputProps={{ "aria-labelledby": "categoryType-label" }}
                    InputLabelProps={{ shrink: true }}
                    select
                    value={selectedProactiveCategory}
                    onChange={handleProactiveCategoryChange}
                    variant="outlined"
                    fullWidth
                    required
                    disabled={disableInput}
                    error={selectedProactiveCategory
                      .toLowerCase()
                      .includes("select")}
                  >
                    {categoryTypeMenuItems}
                  </TextField>

                  <TextField
                    id="startDate"
                    label="Start Date"
                    type="date"
                    value={startDate}
                    onChange={handleStartDateChange}
                    inputProps={{
                      "aria-labelledby": "startDate-label",
                      max: formatDate(new Date()),
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
                    error={startDate == undefined || startDate === ""}
                    required
                  />

                  <TextField
                    id="earliestEligiblePublicationDate"
                    label="Publication Date"
                    type="date"
                    value={earliestEligiblePublicationDate}
                    onChange={handleEarliestPublicationDateChange}
                    inputProps={{
                      "aria-labelledby": "earliestEligiblePublicationDate-label",
                      // max: formatDate(new Date()),
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
                    error={earliestEligiblePublicationDate == undefined || earliestEligiblePublicationDate === ""}
                    required
                  />
                </div>
              </div>



            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  }
);

ProactiveDisclosureDetails.propTypes = {
  requestDetails: PropTypes.object,
  handleRequestDetailsValue: PropTypes.func,
  handleRequestDetailsInitialValue: PropTypes.func,
  handleProactiveDetailsValue: PropTypes.func,
  handleProactiveDetailsInitialValue: PropTypes.func,
  createSaveRequestObject: PropTypes.func,
  disableInput: PropTypes.bool,
  saveRequestObject: PropTypes.object,
};

export default ProactiveDisclosureDetails;
