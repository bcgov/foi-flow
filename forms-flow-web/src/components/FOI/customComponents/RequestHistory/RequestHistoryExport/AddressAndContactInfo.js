import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';


const AddressAndContactInfo = React.memo((requestDetails) => {
  const _requestDetails = requestDetails.requestDetails;

  return (
    <Card id="applicantDetailsExportHistory" className="foi-details-card">
      <label className="foi-details-label">Address and Contact Information</label>
      <CardContent>
        <div className="row foi-details-row ">
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Email</b>
            </div>
            <div>
              <span>{_requestDetails?.email}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Home Phone</b>
            </div>
            <div>
              <span>{_requestDetails?.phonePrimary}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Mobile Phone</b>
            </div>
            <div>
            <span>{_requestDetails?.phoneSecondary}</span>
            </div>
          </div>
        </div>
        <div className="row foi-details-row ">
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Work Phone</b>
            </div>
            <div>
              <span>{_requestDetails?.workPhonePrimary}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Alternative Phone</b>
            </div>
            <div>
            <span>{_requestDetails?.workPhoneSecondary}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Street Address</b>
            </div>
            <div>
              <span>{_requestDetails?.address}</span>
            </div>
          </div>
        </div>
        <div className="row foi-details-row ">
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Secondary Street Address</b>
            </div>
            <div>
            <span>{_requestDetails?.addressSecondary}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>City</b>
            </div>
            <div>
              <span>{_requestDetails?.city}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Province</b>
            </div>
            <div>
            <span>{_requestDetails?.province}</span>
            </div>
          </div>
        </div>
        <div className="row foi-details-row ">
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Country</b>
            </div>
            <div>
              <span>{_requestDetails?.country}</span>
            </div>
          </div>
          <div className="col-lg-4 foi-details-col">
            <div>
              <b>Postal Code</b>
            </div>
            <div>
            <span>{_requestDetails?.postal}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});


export default AddressAndContactInfo;