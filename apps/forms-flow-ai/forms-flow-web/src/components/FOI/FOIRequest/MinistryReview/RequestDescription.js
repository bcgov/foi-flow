import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';



const RequestDescription = React.memo((requestDetails) => {


    return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
            <CardContent>          
                <div className="row foi-details-row">
                  
                    <div className="col-lg-10 foi-details-col">                      
                       
                    </div>
                </div>
                <div className="row foi-details-row">
                  
                  <div className="col-lg-10 foi-details-col">                      
                     All records regarding seismic upgrades and funding for schools across the province
                  </div>
              </div>               
            </CardContent>
        </Card>       
    );


})


export default RequestDescription;