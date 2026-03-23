import React, { useEffect, useContext, useState } from "react";
import { useSelector,useDispatch } from "react-redux";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { makeStyles } from "@material-ui/styles";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCirclePlus } from '@fortawesome/free-solid-svg-icons';
import SearchIcon from "@material-ui/icons/Search";
import CloseIcon from '@mui/icons-material/Close';
import { toast } from "react-toastify";
import {
  Grid,
  TextField,
  InputAdornment,
  IconButton,
  Autocomplete,
  CircularProgress
} from "@mui/material";
import {getFOIMinistryLinkedRequestInfo, linkedRequestsLists, deleteLinkedRequest, saveLinkedRequests} from "../../../apiManager/services/FOI/foiRequestServices";
import { LinkedRequestsTable } from "./LinkedRequestsTable";
import { RemoveLinkedRequestModal } from "./RemoveLinkedRequestModal";

const LinkedRequests = React.memo(
  ({
    requestDetails,
    isMinistry,
    ministryId,
    requestId,
    createSaveRequestObject,
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
    const [removeModalOpen, setRemoveModalOpen] = useState(false);
    const [linkedrequestToRemove, setLinkedRequestToRemove] = useState(null);
 
    const dispatch = useDispatch();

    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [options, setOptions] = useState([]);

    const getAxisRequestId = (item) => {
      const axisRequestId = Object.keys(item)[0];
      if (typeof axisRequestId === "string") return axisRequestId;
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
    const handleRemoveLinkedRequest = (linkedrequestToRemove) => {
      try {
        const [updatedLinkedRequests, updatedLinkedInfoRequests]= removeLinkedRequest(linkedrequestToRemove);
        const parentLinkedRequest = {
          foiministryrequestid: ministryId ?? null,
          rawrequestid: requestId,
          axisrequestid: requestDetails?.axisRequestId
        }
        const data = {
          linkedrequest_a: parentLinkedRequest,
          linkedrequest_b: linkedrequestToRemove,
        }
        const toastID = toast.loading(`Removing linked request ${linkedrequestToRemove?.axisrequestid}`);
        dispatch (
          deleteLinkedRequest(data, requestDetails?.axisRequestId, (err, _result) => {
            if (!err) {
              setLinkedRequests(updatedLinkedRequests);
              setLinkedRequestsInfo(updatedLinkedInfoRequests);
              createSaveRequestObject(FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS, _result["new_linkedrequests"]);
              toast.update(toastID, {
                type: "success",
                render: "Linked request details have been successfully updated",
                position: "top-right",
                isLoading: false,
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
            } else {
              toast.error(
                "Error in removing linked request. Please try again",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          })
        );
      } catch (error) {
        console.log(error);
      }
    }

    const removeLinkedRequest = (reqItem) => {
      const reqId = reqItem.axisrequestid;
      const updatedLinkedRequests = linkedRequests?.filter(item => getAxisRequestId(item) !== reqId);
      const updatedLinkedInfoRequests = linkedRequestsInfo?.filter(item => item.axisrequestid !== reqId);
      return [updatedLinkedRequests, updatedLinkedInfoRequests];
    }

    const renderRequest = (e, reqItem) => {
      e.preventDefault();
      const reqId = reqItem.axisrequestid;
      const item = linkedRequestsInfo.find(
        obj => obj.axisrequestid === reqId
      );
      const rawrequestId = item?.rawrequestid;
      const ministryId = item?.foiministryrequestid;
      const foirequestId = item?.foirequestid;
      let url = '';
      if (ministryId) {
        url = `/foi/foirequests/${foirequestId}/ministryrequest/${ministryId}`
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
      // linkedrequestinfo = {"axisrequestid": str, requeststatus: str, bcgovcode: str}
      // linkedrequests = {"axisrequestid": bcgovcode}
      if (!selectedValue) {
        return;
      }
      // Create a new array to avoid mutation issues
      const updatedLinkedRequests = [...(linkedRequests || [])];
      
      // Get the axis request ID from the selected value
      const newRequestId = selectedValue.axisrequestid;
      
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
        const axisRequestId = selectedValue.axisrequestid;
        const govCode = selectedValue.govcode;
        const linkedReqObj = {
          [selectedValue.axisrequestid]: govCode,
        };
        const linkedReqInfoObj = {
          "axisrequestid": axisRequestId,
          "requeststatus": selectedValue.requeststatus,
          "foiministryrequestid": selectedValue.foiministryrequestid || null, 
          "rawrequestid": selectedValue.rawrequestid,
          "govcode": govCode
        };
        updatedLinkedRequests.push(linkedReqObj);
        setLinkedRequests(updatedLinkedRequests);
        setLinkedRequestsInfo(prev => ([...prev, linkedReqInfoObj]));
      }
      
      // Clear the search after selection
      handleClearSearch();
    }

    const handleSaveLinkedRequests = () => {
      try {
        const parentLinkedRequest = {
          [requestDetails?.axisRequestId]: requestDetails.bcgovcode ? requestDetails?.bcgovcode : requestDetails?.selectedMinistries[0].code
        }
        const data = {
          linkedrequest_a: parentLinkedRequest,
          foiministryrequestid: ministryId ?? null,
          rawrequestid: requestId,
          new_linkedrequests: linkedRequestsInfo,
        }
        const toastID = toast.loading(`Saving linked requests`);
        dispatch (
          saveLinkedRequests(data, requestDetails?.axisRequestId, (err, _result) => {
            if (!err) {
              createSaveRequestObject(FOI_COMPONENT_CONSTANTS.LINKED_REQUESTS, linkedRequests, _result["new_linkedrequests"]);
              toast.update(toastID, {
                type: "success",
                render: "Linked request details have been successfully saved",
                position: "top-right",
                isLoading: false,
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
            } else {
              toast.error(
                "Error in saving linked requests. Please try again",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          })
        );
      } catch (error) {
        console.log(error);
      }
    }
    const handleOpenModal = (linkedRequest) => {
      setLinkedRequestToRemove(linkedRequest);
      setRemoveModalOpen(true);
    }
    const handleCloseModal = () => {
      setLinkedRequestToRemove(null);
      setRemoveModalOpen(false);
    }
    const handleModalSave = () => {
      handleRemoveLinkedRequest(linkedrequestToRemove);
      setLinkedRequestToRemove(null);
      setRemoveModalOpen(false);
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
                renderRequest={renderRequest}
                isMinistry={isMinistry}
                handleOpenModal={handleOpenModal}
              />
              <div style={{display:"flex", flexDirection: "row", justifyContent:"center", alignItems: "center"}}>
                {!showSearch && (
                <div style={{display: "flex", flexDirection: "row", alignItems: "center", margin: "7px 0px 7px 0px"}}>
                    <button onClick={() => setShowSearch(true)} style={{ border: "none", background: "none" }}>
                        <FontAwesomeIcon icon={faCirclePlus}  size="lg" color="#38598A" />
                    </button>
                    <p onClick={() => setShowSearch(true)} style={{fontWeight: "bold", color: "#38598A", cursor: "pointer"}}>Add Linked Request</p>
                </div>
                )}
                {showSearch && (
                  <Grid
                    item
                    xs={12}
                    sx={{
                      p: 1,
                      width: "25%",
                      maxWidth: "400px",
                      padding: "0px"
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
                <button
                  type="button"
                  style={{maxWidth: "250px", marginBottom: "10px", height: "37px", marginLeft: "100px"}}
                  className={`btn-bottom btn-save btn`}
                  onClick={() => handleSaveLinkedRequests()}
                >
                  Save Linked Requests
                </button>
              </div>
            </div>
            <div className="row foi-details-row foi-details-row-break"></div>
          </AccordionDetails>
        </Accordion>
        <RemoveLinkedRequestModal
          modalOpen={removeModalOpen}
          handleClose={handleCloseModal}
          handleSave={handleModalSave}
        />
      </div>
    );
  }
);

export default LinkedRequests;