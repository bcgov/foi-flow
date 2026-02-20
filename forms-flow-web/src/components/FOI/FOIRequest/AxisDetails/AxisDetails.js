import React, {useEffect} from 'react';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { useDispatch} from "react-redux";
import { checkDuplicateAndFetchRequestDataFromAxis } from '../../../../apiManager/services/FOI/foiRequestServices';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { debounce } from "lodash";


const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
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
    const [enableAxisSync, setEnableAxisSync] = React.useState(false)
    let axisIdValidation = {};


    useEffect(() => {
       if(Object.entries(requestDetails)?.length !== 0){
        handleAxisDetailsValue(requestDetails.axisRequestId, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
        const axisDetails = {
            axisRequestId : requestDetails.axisRequestId
        }
        handleAxisDetailsInitialValue(axisDetails);
       }
      }, [requestDetails, handleAxisDetailsInitialValue]);

    useEffect(() => {
        if (axisRequestId) {
            validateAxisId(axisRequestId);
        }
    }, [requestDetails.isconsultflag]);

    const handleAxisIdChange = (e) => {
      const inputValue = e.target.value.toUpperCase();
      setAxisRequestId(inputValue);
      validateAxisId(inputValue);
    };
    
    const validateAxisId = (inputValue) => {
      let helperText = "";
      const axisIDPattern = /^[A-Za-z]+-\d+\-\d+(?:-\d+)?$/;
      const consultAxisIDPattern = /^[A-Za-z]+-\d{4}-\d{5}-CON$/;
      const pattern = requestDetails.isconsultflag ? consultAxisIDPattern : axisIDPattern;

      if (inputValue) {
          const isValid = pattern.test(inputValue);
          helperText = isValid ? "" : "Invalid Axis ID Number";
          updateValidation(helperText);
          if (isValid) {
            checkDuplicatedAxisID(inputValue);
          }else {
            handleAxisDetailsValue("", FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID); 
          }
      } else {
        updateValidation("");
      }
    };
    
    const updateValidation = (helperText) => {
      const axisIdValidation = { field: "AxisId", helperTextValue: helperText };
      setValidation(axisIdValidation);
      handleAxisIdValidation(axisIdValidation);
    };
    
    const checkDuplicatedAxisID = debounce((inputValue) => {
      dispatch(checkDuplicateAndFetchRequestDataFromAxis(inputValue, false, null, (err, data) => {
        if (!err) {
          if (data && data.indexOf("Axis Id exists") >= 0) {
            updateValidation("Request already exists");
            handleAxisDetailsValue("", FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
          } else {
            updateValidation("");
            handleAxisDetailsValue(inputValue, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
            createSaveRequestObject(FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID, inputValue);
          }
        } else {
          console.error("Error checking for duplicate request ID:", err);
          updateValidation("Error checking request ID");
        }
      }));
    }, 300);

    const syncWithAxis = () => {
        dispatch(checkDuplicateAndFetchRequestDataFromAxis(axisRequestId, false, saveRequestObject,(err, data) => {
            if(!err){
                if(Object.entries(data).length === 0){
                    axisIdValidation = {field: "AxisId", helperTextValue: "Invalid AXIS ID Number"}
                    setValidation(axisIdValidation);  
                }
                else if(data){
                    let responseMsg = data;
                    responseMsg+='';
                    if(responseMsg.indexOf("Unauthorized-RestrictedAxisRequest") >= 0)
                      setAxisMessage("UNAUTHORIZED");
                    else if(responseMsg.indexOf("Exception happened while GET operations of request") >= 0)
                      setAxisMessage("ERROR");
                    else if(responseMsg.indexOf("Axis Id exists") >= 0){
                        axisIdValidation = {field: "AxisId", helperTextValue: "AXIS ID Number already exists"};
                        setValidation(axisIdValidation);
                    }
                }
            }
            else
                setAxisMessage("ERROR");
        }));
    }

     return (
        
        <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="axisDetails-header">
            <Typography className={classes.heading}>AXIS DETAILS</Typography>
          </AccordionSummary>
        <AccordionDetails>         
            <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">                       
                    <TextField   
                        id='axisId'                         
                        label="AXIS ID Number" 
                        inputProps={{ "aria-labelledby": "axisId-label", style: { textTransform: "uppercase" }}}
                        InputLabelProps={{ shrink: true, }} 
                        variant="outlined"                             
                        value={axisRequestId}
                        fullWidth
                        onChange={handleAxisIdChange}
                        error={(validation.helperTextValue !== "" && validation.helperTextValue !== undefined)}
                        helperText={validation.helperTextValue}
                        disabled={!enableAxisSync}
                    />
                </div>
                <div className="col-lg-3 foi-details-col">
                    <button 
                      type="button" 
                      onClick={() => setEnableAxisSync((prev) => {
                        setAxisRequestId("")
                        handleAxisDetailsValue("", FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
                        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID, "");
                        return !prev
                      })} 
                      style={{float: "left"}}
                      className='btn-enable-axis-sync'>{!enableAxisSync ? "Enable Sync" : "Disable Sync"}</button>
                </div>
                <div className="col-lg-3 foi-details-col">
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