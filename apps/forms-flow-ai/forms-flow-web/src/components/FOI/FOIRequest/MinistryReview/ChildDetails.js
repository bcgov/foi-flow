import React from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";

const ChildDetails = React.memo((requestDetails) => {
  const _requestDetails = requestDetails.requestDetails;
  const requestType = _requestDetails.requestType
    ? _requestDetails.requestType.replace(/^./, (str) => str.toUpperCase())
    : "";

  const childDetails = {
    firstName: _requestDetails?.additionalPersonalInfo?.childFirstName,
    middleName: _requestDetails?.additionalPersonalInfo?.childMiddleName,
    lastName: _requestDetails?.additionalPersonalInfo?.childLastName,
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
        <div className="row foi-details-row">
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
      </CardContent>
    </Card>
  );
});

export default ChildDetails;
