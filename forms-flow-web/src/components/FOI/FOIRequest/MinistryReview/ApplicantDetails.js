import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { ConditionalComponent, formatDate } from "../../../../helper/FOI/helper";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";

const useStyles = makeStyles(() => ({
  rowMargin: {
    marginBottom: "1em",
  },
}));

const ApplicantDetails = React.memo((requestDetails) => {
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
    alsoKnownAs: _requestDetails?.additionalPersonalInfo?.alsoKnownAs,
    identityVerified: _requestDetails?.identityVerified,
  };

  return (
    <Card id="applicantDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">Applicant Details</label>

      <CardContent>
        <ConditionalComponent condition={requestType === "Personal"}>
          <>
            <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>First Name</b>
                </div>
                <div>
                  <span className="long-text">{_requestDetails.firstName}</span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Middle Name</b>
                </div>
                <div>
                  <span className="long-text">{_requestDetails.middleName}</span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Last Name</b>
                </div>
                <div>
                  <span className="long-text">{_requestDetails.lastName}</span>
                </div>
              </div>
            </div>

            <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Also Known As</b>
                </div>
                <div>
                  <span className="long-text">
                    {additionalApplicantDetails.alsoKnownAs}
                  </span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Date of Birth</b>
                </div>
                <div>
                  <span>
                    {formatDate(
                      additionalApplicantDetails.birthDate,
                      "yyyy/MM/dd"
                    )}
                  </span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Corrections Number</b>
                </div>
                <div>
                  <span className="long-text">
                    {additionalApplicantDetails.correctionsNumber}
                  </span>
                </div>
              </div>
            </div>

            <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Employee Number</b>
                </div>
                <div>
                  <span className="long-text">
                    {additionalApplicantDetails.employeeNumber}
                  </span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Personal Health Number</b>
                </div>
                <div>
                  <span className="long-text">
                    {additionalApplicantDetails.personalHealthNumber}
                  </span>
                </div>
              </div>

              <div className="col-lg-4 foi-details-col">
                <div>
                  <b>Identity Verified</b>
                </div>
                <div>
                  <span className="long-text">
                    {additionalApplicantDetails.identityVerified}
                  </span>
                </div>
              </div>
            </div>
          </>
        </ConditionalComponent>

        <div className="row foi-details-row">
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Application Type</b>
            </div>
            <div>
              <span>{_requestDetails.category}</span>
            </div>
          </div>

          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Request Type</b>
            </div>
            <div>
              <span>{requestType}</span>
            </div>
          </div>

          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Authorization</b>
            </div>
            <div>
              <span>YYYY MM DD</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

export default ApplicantDetails;