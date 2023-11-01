import React, { useEffect }  from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import DivisionalStages from './Divisions/DivisionalStages';
import { useDispatch, useSelector } from "react-redux";
import FOI_COMPONENT_CONSTANTS from "../../../../constants/FOI/foiComponentConstants";
import { fetchFOIMinistryDivisionalStages, fetchFOIPersonalDivisions } from "../../../../apiManager/services/FOI/foiMasterDataServices";
const RequestTracking = React.memo(({
    pubmindivstagestomain,
    existingDivStages,
    ministrycode,
    createMinistrySaveRequestObject,
    requestStartDate,
    setHasReceivedDate,
    requestType
}) => {

    const dispatch = useDispatch();
    useEffect(() => {
        if(ministrycode)
        {
            if(ministrycode == "MCF" && requestType == FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL) {
                dispatch(fetchFOIPersonalDivisions(ministrycode));
            } else {
                dispatch(fetchFOIMinistryDivisionalStages(ministrycode));
            }
        }
    },[ministrycode,dispatch])

    let divisionalstages = useSelector(state=> state.foiRequests.foiMinistryDivisionalStages);
    let MSDSections = useSelector((state) => state.foiRequests.foiPersonalDivisionsAndSections);

    if(ministrycode == "MSD" && MSDSections?.divisions?.length > 0) {
        divisionalstages.divisions = MSDSections.divisions;
    }
    
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

                        divisionalstages!=undefined 
                            && Object.entries(divisionalstages).length > 0
                            && divisionalstages.divisions
                            && divisionalstages.divisions.length > 0
                            && divisionalstages.stages
                            && divisionalstages.stages.length > 0 ? <DivisionalStages divisionalstages={divisionalstages} existingDivStages={existingDivStages} popSelectedDivStages={popselecteddivstages}  createMinistrySaveRequestObject={createMinistrySaveRequestObject} requestStartDate= {requestStartDate} setHasReceivedDate={setHasReceivedDate} /> : <span className="nodivstages">Divisional stages does not exists for this ministry</span>
                    }                      
                  
                </div>
            </div>  
        </CardContent>
    </Card>    
    )


})

export default RequestTracking