import React, {useEffect} from 'react';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { useDispatch} from "react-redux";
import { fetchRequestDataFromAxis } from '../../../../apiManager/services/FOI/foiRequestServices';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';


const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
    foiAxisRequestIds,
    handleAxisDetailsInitialValue,
    handleAxisDetailsValue,
    handleAxisIdValidation,
    setAxisMessage,
    saveRequestObject
}) => {

    const useStyles = makeStyles({
        heading: {
          color: '#FFF',
          fontSize: '16px !important',
          fontWeight: 'bold !important'
        },
        accordionSummary: {
          flexDirection: 'row-reverse'
        }
      });
    const classes = useStyles();
    const dispatch = useDispatch();
    const [axisRequestId, setAxisRequestId] = React.useState("");
    const [validation, setValidation] = React.useState({});
    var axisIdValidation = {};


    useEffect(() => {
       if(Object.entries(requestDetails)?.length !== 0){
        handleAxisDetailsValue(requestDetails.axisRequestId, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
        const axisDetails = {
            axisRequestId : requestDetails.axisRequestId
        }
        handleAxisDetailsInitialValue(axisDetails);
       }
      }, [requestDetails, handleAxisDetailsInitialValue]);


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
        dispatch(fetchRequestDataFromAxis(axisRequestId, false, saveRequestObject,(err, data) => {
            if(!err){
                if(Object.entries(data).length === 0){
                    axisIdValidation = {field: "AxisId", helperTextValue: "Invalid AXIS ID Number"}
                    setValidation(axisIdValidation);  
                }
                else if(data){
                    let responseMsg = data;
                    responseMsg+='';
                    if(responseMsg.indexOf("Exception happened while GET operations of request") >= 0)
                      setAxisMessage("ERROR");
                }
            }
            else
                setAxisMessage("ERROR");
        }));
    }

     return (
        
        <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography className={classes.heading}>AXIS DETAILS</Typography>
          </AccordionSummary>
        <AccordionDetails>         
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
        </AccordionDetails>
      </Accordion>
      </div>      
    );
  });

export default AxisDetails;