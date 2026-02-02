import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import { makeStyles } from "@material-ui/styles";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { fetchFOIProactiveDisclosureCategoryList } from "../../../apiManager/services/FOI/foiMasterDataServices";

const useStyles = makeStyles({
  heading: {
    color: "#FFF",
    fontSize: "16px !important",
    fontWeight: "bold !important",
  },
  accordionSummary: {
    flexDirection: "row-reverse",
  },
});

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
    const classes = useStyles();
    const dispatch = useDispatch();

    // Get master data from Redux store
    const requestTypes = useSelector(
      (state) => state.foiRequests.foiRequestTypeList || []
    );
    const categoryTypes = useSelector(
      (state) => state.foiRequests.foiProactiveDisclosureCategoryList || []
    );
    const reportPeriods = useSelector(
      (state) => state.foiRequests.foiReportPeriodList || []
    );

    useEffect(() => {
      dispatch(fetchFOIProactiveDisclosureCategoryList());
    }, []);

    // Validation helper
    const validateField = (request, fieldName, value) => {
      if (!request) return value || "";
      switch (fieldName) {
        case "requestType":
          return request.requestType || "Select Request Type";
        case "proactiveDisclosureCategory":
          return request.proactiveDisclosureCategory || "Select a Category";
        case "reportPeriod":
          return request.reportPeriod || "N/A";
        case "startDate":
          return request.startDate ? formatDate(request.startDate) : "";
        case "cfrDueDate":
          return request.cfrDueDate || "N/A";
        case "publicationDate":
          return request.publicationDate
            ? formatDate(request.publicationDate)
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
        FOI_COMPONENT_CONSTANTS.REPORT_PERIOD
      );
      //const startDate = !!requestDetails.requestProcessStart ? formatDate(request.requestProcessStart) : "";
      const initialStartDate = requestDetails?.requestProcessStart
        ? formatDate(requestDetails.requestProcessStart)
        : validateField(requestDetails, "startDate");
      const initialCfrDueDate = validateField(requestDetails, "cfrDueDate");
      const initialPublicationDate = validateField(
        requestDetails,
        "publicationDate"
      );

      //setSelectedRequestType(initialRequestType);
      setSelectedProactiveCategory(initialCategoryType);
      setSelectedReportPeriod(initialReportPeriod);
      setStartDate(initialStartDate);
      setCfrDueDate(initialCfrDueDate);
      setPublicationDate(initialPublicationDate);

      const disclosureDetailsObject = {
        proactiveDisclosureCategory: initialCategoryType,
        reportPeriod: initialReportPeriod,
        requestStartDate: initialStartDate,
        cfrDueDate: initialCfrDueDate,
        publicationDate: initialPublicationDate,
      };

      handleProactiveDetailsInitialValue?.(disclosureDetailsObject);
      createSaveRequestObject?.(
        FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES,
        disclosureDetailsObject
      );
    }, [requestDetails, handleRequestDetailsInitialValue]);

    // Local state management
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
        defaultValue: "N/A",
      })
    );
    const [startDate, setStartDate] = useState("");
    const [cfrDueDate, setCfrDueDate] = useState("");
    const [publicationDate, setPublicationDate] = useState("");

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

    const handlePublicationDateChange = (e) => {
      const value = e.target.value;
      setPublicationDate(value);
      handleProactiveDetailsValue?.(value, "publicationDate");
      createSaveRequestObject?.("publicationDate", value);
    };

    // Generate menu items
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
        disabled={!item.name.toLowerCase().includes("calendars")}
      >
        {item.name}
      </MenuItem>
    ));

    const reportPeriodMenuItems = reportPeriods.map((item) => {
      const year = startDate ? startDate.split("-")[0] : "";
      return (
        <MenuItem
          key={item.name}
          value={item.name}
          disabled={item.name.toLowerCase().includes("n/a")}
        >
          {year && !item.name.toLowerCase().includes("n/a") ? `${item.name} ${year}` : item.name}
        </MenuItem>
      );
    });

    return (
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className={classes.accordionSummary}
            expandIcon={<ExpandMoreIcon />}
            id="proactiveDisclosureDetails-header"
          >
            <Typography className={classes.heading}>
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
                    select
                    value={selectedReportPeriod}
                    onChange={handleReportPeriodChange}
                    variant="outlined"
                    fullWidth
                    required
                    disabled={disableInput || !startDate}
                    error={selectedReportPeriod
                      ?.toLowerCase()
                      ?.includes("select")}
                  >
                    {reportPeriodMenuItems}
                  </TextField>

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
                    required
                  />

                  <TextField
                    id="publicationDate"
                    label="Publication Date"
                    type="date"
                    value={publicationDate}
                    onChange={handlePublicationDateChange}
                    inputProps={{
                      "aria-labelledby": "publicationDate-label",
                      // max: formatDate(new Date()),
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
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

export default ProactiveDisclosureDetails;
