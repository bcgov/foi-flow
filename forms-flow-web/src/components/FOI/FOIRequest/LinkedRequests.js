import React, { useEffect, useContext, useState } from "react";
import { useSelector,useDispatch } from "react-redux";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { makeStyles } from "@material-ui/styles";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import AddCircleIcon from '@mui/icons-material/AddCircle';
import SearchIcon from "@material-ui/icons/Search";
import CloseIcon from '@mui/icons-material/Close';
import {
  Grid,
  TextField,
  InputAdornment,
  IconButton,
  Autocomplete,
  CircularProgress
} from "@mui/material";
import {getFOIMinistryLinkedRequestInfo, linkedRequestsLists} from "../../../apiManager/services/FOI/foiRequestServices";
import { LinkedRequestsTable } from "./LinkedRequestsTable";

const LinkedRequests = React.memo(
  ({
    requestDetails,
    createSaveRequestObject,
    isMinistry
  }) => {
    const useStyles = makeStyles({
      heading: {
        color: "#FFF",
        fontSize: "16px !important",
        fontWeight: "bold !important",
      },
      accordionSummary: {
        flexDirection: "row-reverse",
      },
      linkedRequests:{
        float: "left",
      }
    });
    const classes = useStyles();
    const [linkedRequests, setLinkedRequests] = useState(requestDetails?.linkedRequests)
    const [linkedRequestsInfo, setLinkedRequestsInfo] = useState(requestDetails?.linkedRequestsInfo)
    const [loading, setLoading] = useState(false);
 
    const dispatch = useDispatch();

    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [options, setOptions] = useState([]);

    const getAxisRequestId = (item) => {
      if (typeof item.axisrequestid === "string") return item.axisrequestid;
      return null;
    };

    const handleSearch = (value) => {
      if (!value || value?.trim() === "") {
        setOptions([]);
        setSearchQuery("");
        return;
      }
      setSearchQuery(value);
      fetchSuggestions(value);
    };

    const handleClearSearch = () => {
      setShowSearch(false);
      setSearchQuery("");
      setOptions([]);
    }

    const removeLinkedRequest = (reqItem) => {
      const reqId = getAxisRequestId(reqItem);
      const updatedLinkedRequests = linkedRequests?.filter(item => getAxisRequestId(item) !== reqId);
      const updatedLinkedInfoRequests = linkedRequestsInfo?.filter(item => getAxisRequestId(item) !== reqId);
      setLinkedRequests(updatedLinkedRequests);
      setLinkedRequestsInfo(updatedLinkedInfoRequests);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS, updatedLinkedRequests);
    }

    const renderReviewRequest = (e, reqItem) => {
      e.preventDefault();
      const reqId = getAxisRequestId(reqItem);
      const item = linkedRequestsInfo.find(
        obj => obj.axisrequestid === reqId
      );
      const rawrequestId = item?.rawrequestid;
      const ministryId = item?.foiministryrequestid;
      let url = '';
      if (ministryId) {
        url = `/foi/foirequests/${ministryId}/ministryrequest/${ministryId}`
      } else {
        url = `/foi/reviewrequest/${rawrequestId}`;
      }
      window.open(url, "_blank", "noopener,noreferrer");
    };
    
    const fetchSuggestions = (value) => {
      const ministryCode = requestDetails?.selectedMinistries?.length > 0
        ? requestDetails.selectedMinistries[0].code
        : "";
      const queryParams = { q: value };
      try {
        dispatch(
          linkedRequestsLists(
            queryParams,
            requestDetails?.axisRequestId,
            ministryCode,
            (err, _res) => {
              if (err) {
              } else {
                setOptions(_res);
                console.log(_res);
              }
            }
          )
        );
      } catch (error) {
        console.log(error);
      }
    };

    const linkRequest = async (selectedValue) => {
      if (!selectedValue) {
        return;
      }
      // Create a new array to avoid mutation issues
      const updatedLinkedRequests = [...(linkedRequests || [])];
      
      // Get the request ID from the selected value
      const newRequestId = getAxisRequestId(selectedValue);
      
      // Check if this request ID already exists in the array
      const alreadyExists = updatedLinkedRequests.some(
        item => getAxisRequestId(item) === newRequestId
      );

      // Get FOIMinistryRequest Status and MinistryId if FOIRawRequest Status is Archived
      if (selectedValue.requeststatus === "Archived" && !alreadyExists) {
        const res = await dispatch(getFOIMinistryLinkedRequestInfo(selectedValue.axisrequestid));
        selectedValue.requeststatus = res.requeststatus;
        selectedValue.foiministryrequestid = res.foiministryrequestid;
      }

      // Add the new linkedrequest object to linkedrequest and linkedrequstinfo
      if (!alreadyExists && newRequestId) {
        const linkedReqObj = {
          "axisrequestid": selectedValue.axisrequestid,
        };
        const linkedReqInfoObj = {
          "axisrequestid": selectedValue.axisrequestid,
          "requeststatus": selectedValue.requeststatus,
          "foiministryrequestid": selectedValue.foiministryrequestid || null, 
          "rawrequestid": selectedValue.rawrequestid,
          "govcode": selectedValue.govcode
        };
        updatedLinkedRequests.push(linkedReqObj);
        setLinkedRequests(updatedLinkedRequests);
        setLinkedRequestsInfo(prev => ([...prev, linkedReqInfoObj]));
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS, updatedLinkedRequests);
      }
      
      // Clear the search after selection
      handleClearSearch();
    }

    return (
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className={classes.accordionSummary}
            expandIcon={<ExpandMoreIcon />}
            id="requestDetails-header"
          >
            <Typography className={classes.heading}>LINKED REQUESTS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="linked-requests">
              <LinkedRequestsTable
                linkedRequestsInfo={linkedRequestsInfo}
                linkedRequests={linkedRequests}
                renderReviewRequest={renderReviewRequest}
                removeLinkedRequest={removeLinkedRequest}
                isMinistry={isMinistry}
              />
              {!showSearch && (
                <button
                  type="button"
                  className={`btn ${classes.linkedRequests}`}
                  onClick={() => setShowSearch(true)}
                >
                  <AddCircleIcon
                    fontSize="small"
                    sx={{ margin: "0 5px" }}
                  />
                  Add Linked Request
                </button>
              )}
              {showSearch && (
                <Grid
                  item
                  xs={12}
                  sx={{
                    p: 1,
                    width: "35%"
                  }}
                >
                  <Autocomplete
                    freeSolo
                    disableClearable
                    loading={loading}
                    options={options || []}
                    getOptionLabel={(option) => {
                      const axisrequestid = option.axisrequestid
                      if (!option) return "";
                      return axisrequestid;
                    }}
                    inputValue={searchQuery}
                    onInputChange={(e, newValue) => {
                      if (e?.type === "change") {
                        handleSearch(newValue);
                      }
                    }}
                    onChange={(e, selectedValue) => {
                      if (selectedValue) {
                        linkRequest(selectedValue);
                      }
                    }}
                    sx={{
                      "& .MuiOutlinedInput-root": {
                        borderRadius: "6px",
                        height: 40,
                        border: "1px solid #ccc",
                        "& fieldset": { border: "none" },
                        "&:hover fieldset": { border: "none" },
                        "&.Mui-focused fieldset": { border: "1px solid #38598A" },
                      },
                      "& .MuiInputBase-input": {
                        padding: "6px 8px",
                        fontSize: "0.9rem",
                      },
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        placeholder="Search RequestID"
                        InputProps={{
                          ...params.InputProps,
                          startAdornment: (
                            <InputAdornment position="start">
                              <IconButton sx={{ color: "#003388" }}>
                                <SearchIcon sx={{ color: "#038", "& path": { fill: "#038" } }} />
                              </IconButton>
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              {loading ? (
                                <CircularProgress size={18} />
                              ) : 
                                <IconButton
                                  size="small"
                                  onClick={handleClearSearch}
                                  aria-label="Clear search"
                                  sx={{ p: 0.5, color: "#038" }}
                                >
                                  <CloseIcon fontSize="small" />
                                </IconButton>
                              }
                            </InputAdornment>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>
              )}
            </div>
            <div className="row foi-details-row foi-details-row-break"></div>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  }
);

export default LinkedRequests;