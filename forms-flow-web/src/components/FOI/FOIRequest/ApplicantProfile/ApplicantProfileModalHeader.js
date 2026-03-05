import { ButtonBase } from "@mui/material";
import Divider from "@mui/material/Divider";
import clsx from "clsx";

const ApplicantProfileModalHeader = ({
  confirmationMessage,
  applicantHistory,
  selectedApplicant,
  createConfirmation,
  requestHistory,
  showApplicantProfileTab,
  setShowApplicantProfileTab,
  showRequestHistoryTab,
  setShowRequestHistoryTab,
  showSearchApplicantsTab,
  setShowSearchApplicantsTab,
  classes
}) => {
  const FormattedHeader = ({ text }) => {
    return (
      <h3 className="request-history-header search-applicants-header applicant-profile-header">
        {text}
      </h3>
    );
  };

  if (confirmationMessage)
    return <FormattedHeader text={"Saving Changes to Applicant Profile"} />;
  if (applicantHistory) return <FormattedHeader text={"Applicant History"} />;
  if (!selectedApplicant) return <FormattedHeader text={"Search Applicants"} />;
  if (createConfirmation)
    return <FormattedHeader text={"Create New Profile"} />;

  // Renders the tab options if none of the above conditions are met
  return (
    <>
      <ButtonBase
        onClick={() => {
          setShowApplicantProfileTab(true);
          setShowRequestHistoryTab(false);
          setShowSearchApplicantsTab(false);
        }}
        disableRipple
        className={clsx("request-history-header applicant-profile-header", {
          [classes.disabledTitle]: !showApplicantProfileTab,
        })}
      >
        Applicant Profile
      </ButtonBase>
      <Divider
        sx={{
          mr: 2,
          ml: 2,
          borderRightWidth: 3,
          height: 28,
          borderColor: "black",
          display: "inline-flex",
          top: 8,
          position: "relative",
        }}
        flexItem
        orientation="vertical"
      />
      <ButtonBase
        onClick={() => {
          setShowRequestHistoryTab(true);
          setShowApplicantProfileTab(false);
          setShowSearchApplicantsTab(false);
        }}
        disableRipple
        className={clsx("request-history-header applicant-profile-header", {
          [classes.disabledTitle]: !showRequestHistoryTab,
        })}
      >
        Request History ({requestHistory?.length})
      </ButtonBase>
      <Divider
        sx={{
          mr: 2,
          ml: 2,
          borderRightWidth: 3,
          height: 28,
          borderColor: "black",
          display: "inline-flex",
          top: 8,
          position: "relative",
        }}
        flexItem
        orientation="vertical"
      />
      <ButtonBase
        onClick={() => {
          setShowSearchApplicantsTab(true);
          setShowRequestHistoryTab(false);
          setShowApplicantProfileTab(false);
        }}
        disableRipple
        className={clsx("request-history-header applicant-profile-header", {
          [classes.disabledTitle]: !showSearchApplicantsTab,
        })}
      >
        Search Applicants
      </ButtonBase>
    </>
  );
};

export default ApplicantProfileModalHeader;
