import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import "./requestdescriptionbox.scss";
import TextField from "@material-ui/core/TextField";
import { MinistriesList } from "../customComponents";
import { makeStyles } from "@material-ui/core/styles";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { StateEnum } from "../../../constants/FOI/statusEnum";
import { formatDate } from "../../../helper/FOI/helper";
import RequestDescriptionHistory from "../RequestDescriptionHistory";
import { useParams } from "react-router-dom";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import {
  isValidMinistryCode,
  countOfMinistrySelected,
} from "../FOIRequest/utils";

const useStyles = makeStyles({
  headingError: {
    color: "#ff0000",
  },
  headingNormal: {
    color: "000000",
  },
  btndisabled: {
    color: "#808080",
  },
  heading: {
    color: "#FFF",
    fontSize: "16px !important",
    fontWeight: "bold !important",
  },
  accordionSummary: {
    flexDirection: "row-reverse",
  },
  ministrySection: {
    marginTop: "24px",
  },
});

const ProactiveDisclosureDescription = React.memo(
  ({
    programAreaList,
    requestDetails,
    requiredRequestDetailsValues,
    handleOnChangeRequiredRequestDescriptionValues,
    handleInitialRequiredRequestDescriptionValues,
    handleUpdatedProgramAreaList,
    createSaveRequestObject,
    disableInput,
  }) => {
    const classes = useStyles();
    const { ministryId } = useParams();
    
    // Get master data - use const, not let
    const masterProgramAreas = useSelector(
      (state) => state.foiRequests.foiProgramAreaList
    );
    
    // Filter once - use const
    const proactiveProgramAreaList = masterProgramAreas?.filter(
      (value) => !["OCC", "TIC", "CLB", "CFD", "COR", "IIO", "LDB", "LSB", "MGC", "OBC"].includes(value?.iaocode)
    );
    
    const requestDescriptionHistoryList = useSelector(
      (state) => state.foiRequests.foiRequestDescriptionHistoryList
    );

    const [localProgramAreaList, setLocalProgramAreaList] = React.useState([]);

    // Component state management for startDate, endDate and Description
    const [startDate, setStartDate] = React.useState(
      !!requestDetails.fromDate
        ? formatDate(new Date(requestDetails.fromDate))
        : ""
    );
    const [endDate, setEndDate] = React.useState(
      !!requestDetails.toDate ? formatDate(new Date(requestDetails.toDate)) : ""
    );
    const [requestDescriptionText, setRequestDescription] = React.useState(
      !!requestDetails.description ? requestDetails.description : ""
    );

    // Updates the default values from the request description box
    useEffect(() => {
      setStartDate(
        !!requestDetails.fromDate
          ? formatDate(new Date(requestDetails.fromDate))
          : ""
      );
      setEndDate(
        !!requestDetails.toDate
          ? formatDate(new Date(requestDetails.toDate))
          : ""
      );
      setRequestDescription(
        !!requestDetails.description ? requestDetails.description : ""
      );
      
      if (Object.entries(requestDetails).length !== 0) {
        setSelectedMinistries();
      }
      
      const descriptionObject = {
        startDate: !!requestDetails.fromDate
          ? formatDate(new Date(requestDetails.fromDate))
          : "",
        endDate: !!requestDetails.toDate
          ? formatDate(new Date(requestDetails.toDate))
          : "",
        description: !!requestDetails.description
          ? requestDetails.description
          : "",
        isProgramAreaSelected:
          requestDetails?.selectedMinistries?.length === 1 &&
          requestDetails?.selectedMinistries.some((programArea) =>
            isValidMinistryCode(programArea.code, proactiveProgramAreaList)
          ),
        ispiiredacted: ministryId ? true : !!requestDetails.ispiiredacted,
      };
      handleInitialRequiredRequestDescriptionValues(descriptionObject);
    }, [requestDetails, handleInitialRequiredRequestDescriptionValues]);

    // Separate useEffect for program area changes - removed proactiveProgramAreaList from dependencies
    useEffect(() => {
      setSelectedMinistries();
    }, [programAreaList, masterProgramAreas]);

    const setSelectedMinistries = () => {
      let updatedList = [...proactiveProgramAreaList]; // Create a copy, don't reassign
      
      // If updated program area list not exists then, update the master list with selected ministries
      if (Object.entries(programAreaList)?.length === 0) {
        const selectedMinistries = !!requestDetails.selectedMinistries
          ? requestDetails.selectedMinistries
          : "";
        
        if (
          selectedMinistries !== "" &&
          Object.entries(proactiveProgramAreaList).length !== 0
        ) {
          const selectedList = selectedMinistries.map(
            (element) => element.code
          );
          updatedList = updatedList.map((programArea) => ({
            ...programArea,
            isChecked: !!selectedList.find(
              (selectedMinistry) => selectedMinistry === programArea.bcgovcode
            )
          }));
        } else {
          // If it is add request then keep all check boxes unchecked
          updatedList = updatedList.map((programArea) => ({
            ...programArea,
            isChecked: false
          }));
        }
      } else {
        // If updated program area list exists then use that list instead of master data
        updatedList = programAreaList;
      }
      
      setLocalProgramAreaList(updatedList);
    };

    // Handle onchange of start date and set state with latest value
    const handleStartDateChange = (event) => {
      setStartDate(event.target.value);
      if (endDate === "" || new Date(event.target.value) > new Date(endDate))
        setEndDate(event.target.value);
      
      handleOnChangeRequiredRequestDescriptionValues(
        event.target.value,
        FOI_COMPONENT_CONSTANTS.FROM_DATE
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.FROM_DATE,
        event.target.value
      );
    };

    // Handle onchange of end date and set state with latest value
    const handleEndDateChange = (event) => {
      setEndDate(event.target.value);
      handleOnChangeRequiredRequestDescriptionValues(
        event.target.value,
        FOI_COMPONENT_CONSTANTS.TO_DATE
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.TO_DATE,
        event.target.value
      );
    };

    // Handle onchange of description and set state with latest value
    const handleRequestDescriptionChange = (event) => {
      setRequestDescription(event.target.value);
      handleOnChangeRequiredRequestDescriptionValues(
        event.target.value,
        FOI_COMPONENT_CONSTANTS.DESCRIPTION
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.DESCRIPTION,
        event.target.value
      );
    };

    // Handle onchange of Program Area List and bubble up the latest data
    const handleUpdatedMasterProgramAreaList = (updatedProgramAreaList) => {
      handleOnChangeRequiredRequestDescriptionValues(
        countOfMinistrySelected(updatedProgramAreaList) === 1 &&
          updatedProgramAreaList?.some(
            (programArea) =>
              programArea.isChecked &&
              isValidMinistryCode(programArea.bcgovcode, proactiveProgramAreaList)
          ),
        FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED
      );
      handleUpdatedProgramAreaList(updatedProgramAreaList);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST,
        updatedProgramAreaList
      );
    };

    const [openModal, setOpenModal] = React.useState(false);
    
    const handleDescriptionHistoryClick = () => {
      setOpenModal(true);
    };
    
    const handleModalClose = () => {
      setOpenModal(false);
    };

    const sortedList = requestDescriptionHistoryList.sort((a, b) => {
      return new Date(a.createdAt) - new Date(b.createdAt);
    });

    const filteredList = sortedList.filter(
      (request, index, self) =>
        index ===
        self.findIndex(
          (copyRequest) =>
            copyRequest.description === request.description &&
            copyRequest.fromDate === request.fromDate &&
            copyRequest.toDate === request.toDate
        )
    );

    const statesBeforeOpen = [
      StateEnum.unopened.name.toLowerCase(),
      StateEnum.intakeinprogress.name.toLowerCase(),
      StateEnum.peerreview.name.toLowerCase(),
    ];

    return (
      <div className="request-accordian">
        <Accordion defaultExpanded={true}>
          <AccordionSummary
            className={classes.accordionSummary}
            expandIcon={<ExpandMoreIcon />}
            id="proactiveDescription-header"
          >
            <Typography className={classes.heading}>
              PROACTIVE DISCLOSURE DESCRIPTION
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div style={{ width: '100%' }}>
              <div>
                <button
                  type="button"
                  className={`btn btn-link btn-description-history ${
                    filteredList.length <= 1 ? classes.btndisabled : ""
                  }`}
                  disabled={filteredList.length <= 1}
                  onClick={handleDescriptionHistoryClick}
                >
                  Description History
                </button>
              </div>
              <RequestDescriptionHistory
                requestDescriptionHistoryList={filteredList}
                openModal={openModal}
                handleModalClose={handleModalClose}
              />
              
              <div className="row foi-details-row foi-request-description-row">
                <div className="col-lg-6 foi-details-col">
                  <h5 className="foi-date-range-h5">
                    Date Range for Record Search
                  </h5>
                </div>
                <div className="col-lg-3 foi-details-col foi-request-dates">
                  <TextField
                    id="recordStartDate"
                    label="Start Date"
                    type="date"
                    value={startDate}
                    className={classes.textField}
                    onChange={handleStartDateChange}
                    InputLabelProps={{
                      shrink: true,
                    }}
                    InputProps={{ inputProps: { max: formatDate(new Date()) } }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
                  />
                </div>
                <div className="col-lg-3 foi-details-col foi-request-dates">
                  <TextField
                    id="recordEndDate"
                    label="End Date"
                    type="date"
                    value={endDate}
                    className={classes.textField}
                    onChange={handleEndDateChange}
                    InputLabelProps={{
                      shrink: true,
                    }}
                    InputProps={{
                      inputProps: { min: startDate, max: formatDate(new Date()) },
                    }}
                    variant="outlined"
                    fullWidth
                    disabled={disableInput}
                  />
                </div>
              </div>
              
              <div className="row foi-details-row">
                <div className="col-lg-12">
                  <div className="foi-request-description-textbox">
                    <TextField
                      id="outlined-multiline-proactive-description"
                      required={true}
                      label="Ministerial Directive"
                      multiline
                      rows={4}
                      value={requestDescriptionText}
                      variant="outlined"
                      InputLabelProps={{ shrink: true }}
                      onChange={handleRequestDescriptionChange}
                      error={requestDescriptionText === ""}
                      fullWidth
                      disabled={disableInput}
                    />
                  </div>
                </div>
              </div>

              {Object.entries(localProgramAreaList).length !== 0 &&
                (!requestDetails.currentState ||
                  statesBeforeOpen.includes(
                    requestDetails.currentState?.toLowerCase()
                  )) && (
                  <MinistriesList
                    masterProgramAreaList={localProgramAreaList}
                    handleUpdatedMasterProgramAreaList={
                      handleUpdatedMasterProgramAreaList
                    }
                    disableInput={disableInput}
                    isProactiveDisclosure={true}
                  />
                )}
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  }
);

export default ProactiveDisclosureDescription;