import React, { useEffect, useState }  from 'react';
import CFRStatus from './CFRStatus';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import DivisionalStages from './Divisions/DivisionalStages';
import { useDispatch, useSelector } from "react-redux";
import {
    fetchFOIMinistryDivisionalStages
  } from "../../../../apiManager/services/FOI/foiRequestServices";
const RequestTracking = React.memo(({pubmindivstagestomain,existingDivStages,ministrycode}) => {

    const dispatch = useDispatch();
    useEffect(() => {    
        if(ministrycode)
        {
            
            dispatch(fetchFOIMinistryDivisionalStages(ministrycode)); 
        }
        
   },[ministrycode,dispatch])

  
  let divisionalstages = useSelector(state=> state.foiRequests.foiMinistryDivisionalStages);
  
  const popselecteddivstages = (selectedMinDivstages) => {      
      pubmindivstagestomain(selectedMinDivstages)
  }

    return(

        <Card className="foi-details-card">            
        <label className="foi-details-label">DIVISIONAL TRACKING</label>
        <CardContent>                       
                <div className="row foi-details-row">
              
                <div className="col-lg-12 foi-details-col">
                    {

                        divisionalstages!=undefined && Object.entries(divisionalstages).length >0 && divisionalstages.divisions.length >0 ? <DivisionalStages divisionalstages={divisionalstages} existingDivStages={existingDivStages} popselecteddivstages={popselecteddivstages}   /> : null
                    }                      
                  
                </div>
            </div>  
        </CardContent>
    </Card>    
    )


})

export default RequestTracking