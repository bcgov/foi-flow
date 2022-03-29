import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { ConditionalComponent } from "../../../../helper/FOI/helper";
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

  return (
    <Card id="applicantDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">Applicant Details</label>
      <CardContent>
        <ConditionalComponent condition={requestType === "Personal"}>
          <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
            <div className="col-lg-3 foi-details-col">
              <div>
                <b>First Name</b>
              </div>
              <div>
                <span>{_requestDetails.firstName}</span>
              </div>
            </div>
            <div className="col-lg-3 foi-details-col">
              <div>
                <b>Middle Name</b>
              </div>
              <div>
                <span>{_requestDetails.middleName}</span>
              </div>
            </div>
            <div className="col-lg-3 foi-details-col">
              <div>
                <b>Last Name</b>
              </div>
              <div>
                <span>{_requestDetails.lastName}</span>
              </div>
            </div>
          </div>
        </ConditionalComponent>
        <div className="row foi-details-row ">
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