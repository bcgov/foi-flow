import React, {useEffect} from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { useDispatch} from "react-redux";
import { fetchRequestDataFromAxis } from '../../../apiManager/services/FOI/foiRequestServices';


const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
    foiAxisRequestIds,
    handleAxisDetailsValue,
    handleAxisIdValidation
}) => {
    const dispatch = useDispatch();
    const [axisRequestId, setAxisRequestId] = React.useState("");
    const [validation, setValidation] = React.useState({});
    var axisIdValidation = {};


    useEffect(() => {
       if(Object.entries(requestDetails)?.length !== 0){
        handleAxisDetailsValue(requestDetails.axisRequestId, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
       }
      }, [requestDetails]);


    const handleAxisIdChange = (e) => {
        if(e.target.value) {
            let helperText = "";
            if(/^[A-Z]+(?:[-]){0,2}\d+\-\d+$/.test(e.target.value)){
                helperText =  foiAxisRequestIds?.includes(e.target.value)
                    ? "AXIS ID Number already exists": "";
            }
            else
                helperText = "Invalid Axis ID Number";
                
            axisIdValidation = {field: "AxisId", helperTextValue: helperText};
            setValidation(axisIdValidation);
        }
        else{
            axisIdValidation = {field: "AxisId", helperTextValue: ""}
            setValidation(axisIdValidation);  
        }
        handleAxisIdValidation(axisIdValidation);
        setAxisRequestId(e.target.value);
        handleAxisDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID, e.target.value);
    }

    const syncWithAxis = () => {
        dispatch(fetchRequestDataFromAxis(axisRequestId, (err, data) => {
            if(!err){
                if(Object.entries(data).length === 0){
                    axisIdValidation = {field: "AxisId", helperTextValue: "Invalid AXIS ID Number"}
                    setValidation(axisIdValidation);  
                }
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
                            error={(validation.helperTextValue !== "" && validation.helperTextValue !== undefined) || axisRequestId === ""}
                            helperText={validation.helperTextValue}
                            required
                        />
                    </div>
                    <div className="col-lg-6 foi-details-col">                       
                        <button type="button" onClick={() => syncWithAxis()} style={{float: "right"}} disabled={!axisRequestId || validation.helperTextValue !== ""}
                        className='btn-axis-sync'>Sync with AXIS</button>
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );
  });

export default AxisDetails;