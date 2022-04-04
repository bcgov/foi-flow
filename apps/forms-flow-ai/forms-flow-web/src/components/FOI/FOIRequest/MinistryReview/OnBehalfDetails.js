import React from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";

const OnBehalfDetails = React.memo((requestDetails) => {
  const _requestDetails = requestDetails.requestDetails;
  const requestType = _requestDetails.requestType
    ? _requestDetails.requestType.replace(/^./, (str) => str.toUpperCase())
    : "";

  const onBehalfDetails = {
    firstName: _requestDetails?.additionalPersonalInfo?.anotherFirstName,
    middleName: _requestDetails?.additionalPersonalInfo?.anotherMiddleName,
    lastName: _requestDetails?.additionalPersonalInfo?.anotherLastName,
  };

  const onBehalfDetailsEntered = Object.values(onBehalfDetails).some(
    (value) => !!value
  );

  if (requestType !== "Personal" || !onBehalfDetailsEntered) {
    return null;
  }

  return (
    <Card id="onBehalfDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">On Behalf Details</label>
      <CardContent>
        <div className="row foi-details-row">
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>First Name</b>
            </div>
            <div>
              <span>{onBehalfDetails.firstName}</span>
            </div>
          </div>
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Middle Name</b>
            </div>
            <div>
              <span>{onBehalfDetails.middleName}</span>
            </div>
          </div>
          <div className="col-lg-3 foi-details-col">
            <div>
              <b>Last Name</b>
            </div>
            <div>
              <span>{onBehalfDetails.lastName}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

export default OnBehalfDetails;
