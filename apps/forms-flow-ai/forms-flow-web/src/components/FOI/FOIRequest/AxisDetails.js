import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useDispatch} from "react-redux";
import { fetchRequestDataFromAxis } from '../../../apiManager/services/FOI/foiRequestServices';


const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
    syncAxisData,
    foiAxisRequestIds
}) => {
    const dispatch = useDispatch();
    const [axisRequestIdErrorText, setAxisRequestIdErrorText] = React.useState("");
    const [axisRequestId, setAxisRequestId] = React.useState("");
    const handleAxisIdChange = (e) => {
        if(e.target.value) {
            const val =  foiAxisRequestIds?.includes(e.target.value)
                ? "AXIS Request already synced": "";
            setAxisRequestIdErrorText(val);
        }
        setAxisRequestId(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID, e.target.value);
    }

    const syncWithAxis = () => {
        dispatch(fetchRequestDataFromAxis(axisRequestId, (err, data) => {
            if(!err){
                if(Object.entries(data).length !== 0)
                    syncAxisData(data);
                else
                    setAxisRequestIdErrorText("Invalid AXIS ID Number.");
            }
        }));
    }

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">AXIS DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                       
                        <TextField                            
                            label="AXIS ID Number" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined"                             
                            value={axisRequestId}
                            fullWidth
                            onChange={handleAxisIdChange}
                            error={(axisRequestIdErrorText !== "" && axisRequestIdErrorText !== undefined)}
                            helperText={axisRequestIdErrorText}
                        />
                    </div>
                    <div className="col-lg-6 foi-details-col">                       
                        <button type="button" onClick={() => syncWithAxis()} style={{float: "right"}} disabled={!axisRequestId || axisRequestIdErrorText !== ""}
                        className='btn-axis-sync'>Sync with AXIS</button>
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );
  });

export default AxisDetails;