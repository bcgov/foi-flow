import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';



const RequestDetails = React.memo((requestDetails) => {


    return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row">
                  
                    <div className="col-lg-10 foi-details-col">                      
                       
                    </div>
                </div>
                <div className="row foi-details-row">
                  
                  <div className="col-lg-3 foi-details-col">                      
                     <span>2021 May 7</span>
                  </div>
                  <div className="col-lg-3 foi-details-col">                      
                  <span>2021 May 28</span>
                  </div>
                  <div className="col-lg-3 foi-details-col">                      
                  <span>2021 Jun 28</span>
                  </div>
              </div>               
            </CardContent>
        </Card>       
    );


})


export default RequestDetails;