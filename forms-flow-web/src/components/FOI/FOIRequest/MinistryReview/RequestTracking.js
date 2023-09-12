import React, { useEffect }  from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import DivisionalStages from './Divisions/DivisionalStages';
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIMinistryDivisionalStages } from "../../../../apiManager/services/FOI/foiMasterDataServices";
const RequestTracking = React.memo(({pubmindivstagestomain,existingDivStages,ministrycode,createMinistrySaveRequestObject,requestStartDate, setHasReceivedDate}) => {

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

        <Card style={{overflow: "visible"}} className="foi-details-card" id="divisionalTracking">
        <label className="foi-details-label">DIVISIONAL TRACKING</label>
        <CardContent>                       
                <div className="row foi-details-row">
              
                <div className="col-lg-12 foi-details-col">
                    {

                        divisionalstages!=undefined && Object.entries(divisionalstages).length >0 && divisionalstages.divisions.length >0 ? <DivisionalStages divisionalstages={divisionalstages} existingDivStages={existingDivStages} popSelectedDivStages={popselecteddivstages}  createMinistrySaveRequestObject={createMinistrySaveRequestObject} requestStartDate= {requestStartDate} setHasReceivedDate={setHasReceivedDate} /> : <span className="nodivstages">Divisional stages does not exists for this ministry</span>
                    }                      
                  
                </div>
            </div>  
        </CardContent>
    </Card>    
    )


})

export default RequestTracking