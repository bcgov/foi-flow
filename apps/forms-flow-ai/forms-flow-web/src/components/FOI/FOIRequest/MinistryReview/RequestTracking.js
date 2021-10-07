import React, { useEffect, useState }  from 'react';
import CFRStatus from './CFRStatus';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

const RequestTracking = React.memo((props) => {



    return(

        <Card className="foi-details-card">            
        <label className="foi-details-label">REQUEST TRACKING</label>
        <CardContent>          
            <div className="row foi-details-row">
              
                <div className="col-lg-10 foi-details-col">                      
                   <CFRStatus/>
                </div>
            </div>
                <hr/>     
        </CardContent>
    </Card>    
    )


})

export default RequestTracking