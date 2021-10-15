import React, { useEffect, useState }  from 'react';
import CFRStatus from './CFRStatus';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import DivisionalStages from './Divisions/DivisionalStages';
const RequestTracking = React.memo((props) => {



    return(

        <Card className="foi-details-card">            
        <label className="foi-details-label">DIVISIONAL TRACKING</label>
        <CardContent>                       
                <div className="row foi-details-row">
              
                <div className="col-lg-12 foi-details-col">                      
                  <DivisionalStages />
                </div>
            </div>  
        </CardContent>
    </Card>    
    )


})

export default RequestTracking