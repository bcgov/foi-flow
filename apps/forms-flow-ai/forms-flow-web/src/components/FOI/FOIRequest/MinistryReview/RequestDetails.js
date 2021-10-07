import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';
import { formatDate } from "../../../../helper/FOI/helper";


const RequestDetails = React.memo((requestDetails) => {

    const _requestDetails = requestDetails.requestDetails

    return (
        Object.entries(_requestDetails).length >0 && _requestDetails!=undefined  ?
      <>
        <Card className="foi-details-card">
        <div className="row foi-details-row foi-justifyleft"> 
        <div className="col-lg-8 foi-details-col ">           
            <label className="foi-details-label">REQUEST DETAILS</label></div>
            <div className="col-lg-4 foi-details-col "><a href='#'>Ministries Canvassed</a></div>
            </div>
            <CardContent>          
                <div className="row foi-details-row foi-justifyleft">
                  
                    <div className="col-lg-10 foi-details-col ">                     
                        <b>Selected Ministry: {_requestDetails.selectedMinistries[0].name}</b> 
                    </div>
                    
                </div>
                <div className="row foi-details-row foi-justifyleft">
                </div>
                <div className="row foi-details-row foi-rowtoppadding">
                  
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                    <span><b>Request Opened</b></span>                      
                    <span>{formatDate(_requestDetails.requestProcessStart,'yyyy MMM, dd')}</span>
                  </div>
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                  <span><b>Records Due Date</b></span>                      
                  <span>{formatDate(_requestDetails.cfrDueDate,'yyyy MMM, dd')}</span>
                  </div>
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                  <span><b>Legislated Due Date</b></span>                      
                  <span>{formatDate(_requestDetails.dueDate,'yyyy MMM, dd')}</span>
                  </div>
              </div>               
            </CardContent>
        </Card> </>: null     
    );


})


export default RequestDetails;