import React from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";
import { formatDate } from "../../../../helper/FOI/helper";

const useStyles = makeStyles(() => ({
  rowMargin: {
    marginBottom: "1em",
  },
}));

const AdditionalApplicantDetails = React.memo((requestDetails) => {
  const classes = useStyles();
  const _requestDetails = requestDetails.requestDetails;
  const requestType = _requestDetails.requestType
    ? _requestDetails.requestType.replace(/^./, (str) => str.toUpperCase())
    : "";
  const additionalApplicantDetails = {
    personalHealthNumber:
      _requestDetails?.additionalPersonalInfo?.personalHealthNumber,
    birthDate: _requestDetails?.additionalPersonalInfo?.birthDate,
    employeeNumber: _requestDetails?.publicServiceEmployeeNumber,
    correctionsNumber: _requestDetails?.correctionalServiceNumber,
  };

  const additionalApplicantDetailsEntered = Object.values(
    additionalApplicantDetails
  ).some((value) => !!value);

  if (requestType !== "Personal" || !additionalApplicantDetailsEntered) {
    return null;
  }

  return (
    <Card id="additionalApplicantDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">Additional Applicant Details</label>
      <CardContent>
        <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Personal Health Number</b>
            </div>
            <div>
              <span>{additionalApplicantDetails.personalHealthNumber}</span>
            </div>
          </div>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Employee Number</b>
            </div>
            <div>
              <span>{additionalApplicantDetails.employeeNumber}</span>
            </div>
          </div>
        </div>

        <div className="row foi-details-row">
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Date of Birth</b>
            </div>
            <div>
              <span>
                {formatDate(additionalApplicantDetails.birthDate, "yyyy/MM/dd")}
              </span>
            </div>
          </div>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Corrections Number</b>
            </div>
            <div>
              <span>{additionalApplicantDetails.correctionsNumber}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

export default AdditionalApplicantDetails;
