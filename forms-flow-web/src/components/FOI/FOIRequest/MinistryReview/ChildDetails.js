import React from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { formatDate } from "../../../../helper/FOI/helper";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";

const useStyles = makeStyles(() => ({
  rowMargin: {
    marginBottom: "1em",
  },
}));

const ChildDetails = React.memo((requestDetails) => {
  const classes = useStyles();
  const _requestDetails = requestDetails.requestDetails;
  const requestType = _requestDetails.requestType
    ? _requestDetails.requestType.replace(/^./, (str) => str.toUpperCase())
    : "";

  const childDetails = {
    firstName: _requestDetails?.additionalPersonalInfo?.childFirstName,
    middleName: _requestDetails?.additionalPersonalInfo?.childMiddleName,
    lastName: _requestDetails?.additionalPersonalInfo?.childLastName,
    childAlsoKnownAs: _requestDetails?.additionalPersonalInfo?.childAlsoKnownAs,
    childBirthDate: _requestDetails?.additionalPersonalInfo?.childBirthDate
  };

  const childDetailsEntered = Object.values(childDetails).some(
    (value) => !!value
  );

  if (requestType !== "Personal" || !childDetailsEntered) {
    return null;
  }

  return (
    <Card id="childDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">Child Details</label>
      <CardContent>
        <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>First Name</b>
            </div>
            <div>
              <span>{childDetails.firstName}</span>
            </div>
          </div>
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Middle Name</b>
            </div>
            <div>
              <span>{childDetails.middleName}</span>
            </div>
          </div>
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Last Name</b>
            </div>
            <div>
              <span>{childDetails.lastName}</span>
            </div>
          </div>
          </div>
          <div className="row foi-details-row">
            <div className="col-lg-3 foi-details-col">
              <div>
                <b>Also Known As</b>
              </div>
              <div>
                <span className="long-text">{childDetails.childAlsoKnownAs}</span>
              </div>
            </div>
            <div className="col-lg-3 foi-details-col">
              <div>
                <b>Date of Birth</b>
              </div>
              <div>
                <span>{formatDate(childDetails.childBirthDate, "yyyy/MM/dd")}</span>
              </div>
            </div>
        </div>
      </CardContent>
    </Card>
  );
});

export default ChildDetails;
