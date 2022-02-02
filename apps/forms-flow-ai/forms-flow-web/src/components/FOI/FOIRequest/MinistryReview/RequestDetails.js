import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { formatDate } from "../../../../helper/FOI/helper";
import { StateEnum } from '../../../../constants/FOI/statusEnum';

const RequestDetails = React.memo((requestDetails) => {

    const _requestDetails = requestDetails.requestDetails;    

    return (
        Object.entries(_requestDetails).length >0 && _requestDetails!=undefined  ?
      <>
        <Card className="foi-details-card">
            <div className="row foi-details-row">
              <div className="col-lg-8 foi-details-col ">
                <label className="foi-details-label">REQUEST DETAILS</label></div>
              <div className="col-lg-4 foi-details-col "><a href='#' className="foi-floatright foi-link">Ministries Canvassed</a></div>
            </div>
            <CardContent>          
                <div className="row foi-details-row foi-justifyleft">
                  
                    <div className="col-lg-10 foi-details-col ">                     
                        <b>Selected Ministry: {_requestDetails.selectedMinistries && _requestDetails.selectedMinistries[0].name }</b> 
                    </div>
                    
                </div>
                <div className="row foi-details-row foi-justifyleft">
                </div>
                <div className="row foi-details-row foi-rowtoppadding foi-justify-spacyaround">
                  
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                    <span><b>Request Opened</b></span>                      
                    <span className="foi-rowtoppadding">{formatDate(_requestDetails.requestProcessStart,'MMM dd yyyy')}</span>
                  </div>
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                  <span><b>Records Due Date</b></span>                      
                  <span className="foi-rowtoppadding">{_requestDetails.currentState && _requestDetails.currentState.toLowerCase() !== StateEnum.onhold.name.toLowerCase() ? formatDate(_requestDetails.cfrDueDate,'MMM dd yyyy') : "N/A"}</span>
                  </div>
                  <div className="col-lg-4 foi-details-col foi-inline-grid">
                  <span><b>Legislated Due Date</b></span>                      
                  <span className="foi-rowtoppadding">{_requestDetails.currentState && _requestDetails.currentState.toLowerCase() !== StateEnum.onhold.name.toLowerCase() ? formatDate(_requestDetails.dueDate,'MMM dd yyyy'): "N/A"}</span>
                  </div>
              </div>               
            </CardContent>
        </Card> </>: null     
    );


})


export default RequestDetails;