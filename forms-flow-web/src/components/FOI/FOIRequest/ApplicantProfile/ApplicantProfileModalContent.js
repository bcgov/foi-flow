import React from "react";
import Accordion from "@material-ui/core/Accordion";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { toast } from "react-toastify";
import Loading from "../../../../containers/Loading";
import { ApplicantProfileSearchView } from "./ApplicantProfileSearchView";
import Alert from "@mui/material/Alert";
import ApplicantDetailsSections from "./ApplicantDetailsSections";
import { DataGrid } from "@mui/x-data-grid";
import Box from "@mui/material/Box";
import { isBeforeOpen } from "../utils";

const ApplicantProfileModalContent = ({
  isLoading,
  setIsLoading,
  rows,
  setRows,
  requestDetails,
  saveApplicantObject,
  setSaveApplicantObject,
  createSaveApplicantObject,
  selectedApplicant,
  setSelectedApplicant,
  applicantHistory,
  showApplicantHistory,
  createConfirmation,
  confirmationMessage,
  isAddRequest,
  isUnopenedRequest,
  isProfileDifferent,
  setIsProfileDifferent,
  isChangeToDifferentProfile,
  isUnassignProfile,
  warning,
  requestHistory,
  setRequestHistory,
  dispatch,
  showApplicantProfileTab,
  setShowApplicantProfileTab,
  showSearchApplicantsTab,
  setShowSearchApplicantsTab,
  showRequestHistoryTab,
}) => {
  const requestHistoryColumns = [
    {
      field: "axisrequestid",
      headerName: "REQUEST ID",
      flex: 1,
      renderCell: (params) => {
        let link = "";
        if (params.row.receiveddate == "Historical Request") {
          link = "/foi/historicalrequest/" + params.row.axisrequestid;
        } else if (params.row.ministryrequestid) {
          link =
            "/foi/foirequests/" +
            params.row.requestid +
            "/ministryrequest/" +
            params.row.ministryrequestid;
        } else {
          link = "/foi/reviewrequest/" + params.row.requestid;
        }
        return (
          <span className="table-cell-truncate">
            <a
              style={{ color: "rgba(0, 0, 0, 0.87)" }}
              href={link}
              target="_blank"
            >
              {params.row.axisrequestid}
            </a>
          </span>
        );
      },
    },
    {
      field: "requeststatus",
      headerName: "CURRENT STATE",
      flex: 1,
    },
    {
      field: "receiveddate",
      headerName: "RECEIVED DATE",
      flex: 1,
    },
    {
      field: "description",
      headerName: "REQUEST DESRCIPTION",
      flex: 2,
    },
  ];

  const copyInfo = () => {
    let updatedApplicant = { ...selectedApplicant };
    for (let field in selectedApplicant) {
      if (
        field === "additionalPersonalInfo" &&
        requestDetails.requestType === "personal"
      ) {
        for (let infofield in requestDetails[field]) {
          if (
            requestDetails[field][infofield] &&
            requestDetails[field][infofield] !==
              selectedApplicant[field][infofield]
          ) {
            updatedApplicant[field][infofield] =
              requestDetails[field][infofield];
          }
        }
      } else if (
        requestDetails[field] &&
        selectedApplicant[field] !== requestDetails[field]
      ) {
        updatedApplicant[field] = requestDetails[field];
      }
    }
    setSaveApplicantObject(updatedApplicant);
    setIsProfileDifferent(false);
  };

  if (isLoading) {
    return <Loading />;
  }

  if (confirmationMessage && isChangeToDifferentProfile)
    return (
      <>
        <Alert severity="warning" sx={{ fontSize: "1.2rem" }}>
          Just a heads up:<br></br>
          Previous information on this request will be overwritten by the
          applicant profile information, and won't be retrievable.<br></br>
          Are you sure you would like to change the applicant profile linked to
          this request?
        </Alert>
      </>
    );
  if (confirmationMessage && isUnassignProfile)
    return (
      <div style={{ textAlign: "center" }}>
        The linked applicant profile will be removed, but the information for
        this request will stay the same. You can make updates to the request,
        and when the request is moved into the Open state, the correspondening
        applicant profile will be automatically created.
      </div>
    );

  if (confirmationMessage)
    return (
      <div style={{ textAlign: "center" }}>
        Are you sure you would like to save changes for all active requests
        associated with this profile?
        <br />
        <i>
          Please ensure you have checked the Request History to see the
          request(s) that will be affected.
        </i>
      </div>
    );

  if (createConfirmation && isBeforeOpen(requestDetails)) {
    return (
      <ApplicantDetailsSections
        requestDetails={saveApplicantObject}
        contactDetailsNotGiven={false}
        createSaveRequestObject={createSaveApplicantObject}
        handleApplicantDetailsInitialValue={() => {}}
        handleApplicantDetailsValue={() => {}}
        disableInput={false}
        defaultExpanded={true}
        showHistory={showApplicantHistory}
        warning={null}
        displayOtherNotes={true}
        isAddRequest={isAddRequest}
        isUnopenedRequest={isUnopenedRequest}
        requestType={requestDetails?.requestType}
        disableAdditionalDetails={false}
      />
    );
  }
  if (createConfirmation)
    return (
      <>
        <div style={{ textAlign: "center" }}>
          A new Profile will be created from the following information. The old
          profile will not be connected to this request anymore.
        </div>
        <ApplicantDetailsSections
          requestDetails={saveApplicantObject}
          contactDetailsNotGiven={false}
          createSaveRequestObject={createSaveApplicantObject}
          handleApplicantDetailsInitialValue={() => {}}
          handleApplicantDetailsValue={() => {}}
          disableInput={true}
          defaultExpanded={true}
          showHistory={showApplicantHistory}
          warning={null}
          displayOtherNotes={true}
          isAddRequest={isAddRequest}
          isUnopenedRequest={isUnopenedRequest}
          requestType={requestDetails?.requestType}
        />
      </>
    );

  if (applicantHistory) {
    return (
      <>
        {applicantHistory.map((entry, index) => (
          <Accordion key={index} defaultExpanded={index === 0}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography className="acc-request-description">
                APPLICANT CONTACT DETAILS
              </Typography>
              <Typography className="acc-username-date">
                {entry.createdby} - {entry.updatedat}
              </Typography>
            </AccordionSummary>

            <AccordionDetails className="acc-details">
              <div className="acc-details-1">
                {Object.keys(entry.fields).map((field) => (
                  <React.Fragment key={field}>
                    <div className="acc-applicant-profile-history-row">
                      <Typography className="acc-start-date">
                        <b>{field}: </b>
                        {entry.fields[field]}
                      </Typography>
                    </div>
                    <div className="acc-applicant-profile-history-row">
                      <Typography className="acc-start-date">
                        <b>Previous {field}: </b>
                        {entry.previousvalues[field]}
                      </Typography>
                    </div>
                  </React.Fragment>
                ))}
              </div>
            </AccordionDetails>
          </Accordion>
        ))}
      </>
    );
  }

  const renderApplicantProfileTabMessage = () => {
    if (isChangeToDifferentProfile)
      return (
        <span style={{ fontSize: "13px" }}>
          You are changing the applicant profile that is linked to this request.
        </span>
      );
    if (isProfileDifferent)
      return (
        <span style={{ fontSize: "13px" }}>
          Some of the fields in this profile do not match your original request.
          <button
            type="button"
            className="btn-link btn-update-profile"
            onClick={copyInfo}
          >
            UPDATE ALL
          </button>
        </span>
      );
    return (
      <span style={{ fontSize: "13px" }}>
        All of the fields in the applicant profile match your original request.
      </span>
    );
  };

  if (showApplicantProfileTab) {
    if (selectedApplicant) {
      return (
        <>
          {renderApplicantProfileTabMessage()}

          <ApplicantDetailsSections
            requestDetails={saveApplicantObject}
            contactDetailsNotGiven={false}
            createSaveRequestObject={createSaveApplicantObject}
            handleApplicantDetailsInitialValue={() => {}}
            handleApplicantDetailsValue={() => {}}
            disableInput={
              isChangeToDifferentProfile ||
              !requestDetails?.foiRequestApplicantID
                ? true
                : false
            }
            defaultExpanded={isChangeToDifferentProfile ? true : false}
            showHistory={showApplicantHistory}
            warning={warning}
            displayOtherNotes={true}
            isAddRequest={isAddRequest}
            isUnopenedRequest={isUnopenedRequest}
            requestType={requestDetails?.requestType}
          />
        </>
      );
    } else {
      return (
        <ApplicantProfileSearchView
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          rows={rows}
          setRows={setRows}
          setSelectedApplicant={setSelectedApplicant}
          setRequestHistory={setRequestHistory}
          dispatch={dispatch}
          toast={toast}
          initialSearchMode={
            isAddRequest || isUnopenedRequest ? "manual" : "auto"
          }
        />
      );
    }
  }

  if (showRequestHistoryTab) {
    return (
      <>
        <Box sx={{ height: "100%", width: "100%" }}>
          <DataGrid
            className="foi-data-grid foi-request-history-grid"
            rows={requestHistory}
            columns={requestHistoryColumns}
            rowHeight={30}
            headerHeight={50}
            hideFooter={true}
            loading={isLoading}
            // onRowClick={selectApplicantRow}
            getRowHeight={() => "auto"}
            getRowId={(row) => row.axisrequestid}
          />
        </Box>
      </>
    );
  }

  if (showSearchApplicantsTab) {
    return (
      <ApplicantProfileSearchView
        setShowSearchApplicantsTab={setShowSearchApplicantsTab}
        setShowApplicantProfileTab={setShowApplicantProfileTab}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
        rows={rows}
        setRows={setRows}
        setSelectedApplicant={setSelectedApplicant}
        setRequestHistory={setRequestHistory}
        dispatch={dispatch}
        toast={toast}
        initialSearchMode={"manual"}
      />
    );
  }
  return <></>;
};
export default ApplicantProfileModalContent;
