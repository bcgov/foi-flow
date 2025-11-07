import React, { useEffect, useContext, useState } from "react";
import { useParams } from "react-router-dom";
import { useSelector,useDispatch } from "react-redux";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import {
  shouldDisableFieldForMinistryRequests,
  findRequestState,
} from "./utils";
import { makeStyles } from "@material-ui/styles";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import CancelIcon from '@mui/icons-material/Cancel';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import SearchIcon from "@material-ui/icons/Search";
import CloseIcon from '@mui/icons-material/Close';
import {
  Grid,
  TextField,
  InputAdornment,
  IconButton,
  Autocomplete,
  InputBase,
  Link,
  CircularProgress
} from "@mui/material";
import {linkedRequestsLists} from "../../../apiManager/services/FOI/foiRequestServices";

const LinkedRequests = React.memo(
  ({
    requestDetails,
    requestStatus,
    handleRequestDetailsValue,
    handleRequestDetailsInitialValue,
    createSaveRequestObject,
    disableInput,
    isHistoricalRequest,
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
    const [searchResults, setSearchResults] = useState([]);
    const [options, setOptions] = useState([]);

    const getRequestId = (item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") return Object.keys(item)[0];
      return null;
    };

    const handleSearch = (value) => {
      if (!value || value?.trim() === "") {
        setOptions([]);
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
      const reqId = getRequestId(reqItem);
      let updatedLinkedRequests = linkedRequests?.filter(item => getRequestId(item) !== reqId);
      setLinkedRequests(updatedLinkedRequests);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS, updatedLinkedRequests);
    }

    const renderReviewRequest = (e, reqItem) => {
      e.preventDefault();
      const reqId = getRequestId(reqItem);
      const item = linkedRequestsInfo.find(
        obj => obj.axisrequestid === reqId
      );
      const requestId = item ? item.requestid : null;
      const ministryId = item ? item.ministryid : null;
      let url = '';
      if (ministryId) {
        url = `/foi/foirequests/${requestId}/ministryrequest/${ministryId}`
      } else {
        url = `/foi/reviewrequest/${requestId}`;
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

    const linkRequest = (selectedValue) => {
      if (!selectedValue) {
        return;
      }

      // Create a new array to avoid mutation issues
      const updatedLinkedRequests = [...(linkedRequests || [])];
      
      // Get the request ID from the selected value
      const newRequestId = getRequestId(selectedValue);
      
      // Check if this request ID already exists in the array
      const alreadyExists = updatedLinkedRequests.some(
        item => getRequestId(item) === newRequestId
      );

      if (!alreadyExists && newRequestId) {
        // Push the entire object (format: {"CTZ-324342-3422":"CTZ"})
        updatedLinkedRequests.push(selectedValue);
        setLinkedRequests(updatedLinkedRequests);
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
            
              <ul className="linked-request-list">
                {linkedRequests?.map((reqItem, index) => {
                  const reqId = getRequestId(reqItem);
                  return (
                    <li key={reqId || index} className="linked-request-item">
                      <Link
                        component="button"
                        sx={{ color: "#38598A", cursor: "pointer", textDecoration: "underline"}}
                        onClick={(e) => renderReviewRequest(e, reqItem)}
                        className="linked-request-link"
                      >
                        {reqId}
                      </Link>
                      <button
                        className="btn btn-link text-danger"
                        aria-label={`Remove linked request ${reqId}`}
                        onClick={() => removeLinkedRequest(reqItem)}
                      >
                        <CancelIcon
                          fontSize="small"
                          sx={{ color: "#038 !important" }}
                        />
                      </button>
                    </li>
                  );
                })}
              </ul>

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
                      if (!option) return "";
                      if (typeof option === "string") return option;
                      const key = Object.keys(option)[0];
                      return key || "";
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