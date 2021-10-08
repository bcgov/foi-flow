import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';



const ApplicantDetails = React.memo((requestDetails) => {

    const _requestDetails = requestDetails.requestDetails;
    const requestType = _requestDetails.requestType ? _requestDetails.requestType.replace(/^./, str => str.toUpperCase()) : "";

    return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">APPLICANT DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row ">
                    <div className="col-lg-3 foi-details-col">
                        <div><b>Application Type</b></div>
                        <div><span>{_requestDetails.category}</span></div>
                    </div>
                    <div className="col-lg-3 foi-details-col">
                        <div><b>Request Type</b></div>
                        <div><span>{requestType}</span></div>
                    </div>
                    <div className="col-lg-3 foi-details-col">
                        <div><b>Authorization</b></div>
                        <div><span>YYYY MM DD</span></div>
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );


})


export default ApplicantDetails;