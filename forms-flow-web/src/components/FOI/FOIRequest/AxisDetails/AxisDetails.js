import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { useDispatch} from "react-redux";
import { checkDuplicateAndFetchRequestDataFromAxis } from '../../../../apiManager/services/FOI/foiRequestServices';
import { fetchOriginalRequestDetails } from '../../../../apiManager/services/FOI/foiRequestConsultServices';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { debounce } from "lodash";
import clsx from 'clsx';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import { Chip } from '@mui/material';
import InputAdornment from "@material-ui/core/InputAdornment";
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

const AxisDetails = React.memo(({  
    requestDetails,
    createSaveRequestObject,
    handleAxisDetailsInitialValue,
    handleAxisDetailsValue,
    handleAxisIdValidation,
    handleOriginalRequestIDInitialValue,
    handleOriginalRequestIDValue,
    setAxisMessage,
    saveRequestObject,
    isAddConsultRequest,
    isDataSynced,
}) => {

    const useStyles = makeStyles({
        heading: {
          color: '#FFF',
          fontSize: '16px !important',
          fontWeight: 'bold !important'
        },
        accordionSummary: {
          flexDirection: 'row-reverse'
        },
        showOriginalRequestIdFieldValidation: {
          color: "#CE3E39",
          fontStyle: 'italic',
          fontSize: '13px !important'
        },
        hideOriginalRequestIdFieldValidation: {
          visibility: 'hidden !important'
        },
        warningAmberIcon:{
          color: "#CE3E39 !important",
          width: "20px !important",
          transform: 'translateY(-1%) !important',
          fontSize: "medium !important",
          marginRight: "-50px !important",
        },
        showIcon: {
          color: "#CE3E39 !important",
          backgroundColor: "#fff !important",
          position: 'absolute !important',
          right: 45,
          pointerEvents: 'none !important',
        },
        hideIcon: {
          visibility: 'hidden !important',
        },
      });
    const classes = useStyles();
    const dispatch = useDispatch();
    const [axisRequestId, setAxisRequestId] = React.useState("");
    const [isButtonDisabled, setIsButtonDisabled] = useState(false);
    const [originalRequestId, setOriginalRequestId] = React.useState("");
    const [validation, setValidation] = React.useState({});
    const [isOriginalRequestIdValid, setIsOriginalRequestIdValid] = useState(false);
    let axisIdValidation = {};
    let originalRequestIdValidation = {};


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
      const axisIDPattern = /^[A-Za-z]+-\d{4}-\d{5}$/;
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

    const getOriginalRequestDetails = () => {
        if (!originalRequestId) {
            originalRequestIdValidation = { field: "originalRequestId", helperTextValue: "This field is required" };
            setValidation(originalRequestIdValidation);
            setIsButtonDisabled(false);
            setIsOriginalRequestIdValid(false);
            return;
        }

        dispatch(fetchOriginalRequestDetails(originalRequestId,(err, data) => {
          if(!err){
            if (data.ispresent) {
              setValidation("");
              setIsButtonDisabled(true);
              setIsOriginalRequestIdValid(true);
          } else {
              originalRequestIdValidation = { field: "originalRequestId", helperTextValue: "Invalid Request ID Number" };
              setValidation(originalRequestIdValidation);
              setIsButtonDisabled(false);
              setIsOriginalRequestIdValid(false);
          }
        } else {
          setAxisMessage("ERROR");
        }
        }));
        
    }

    const getHeadingText = () => {
      return isAddConsultRequest ? "Original Request ID" : "AXIS DETAILS";
    };

    const handleOriginalRequestIDChange = (e) => {
      const inputValue = e.target.value.toUpperCase();
      // setAxisRequestId(inputValue);
      // validateAxisId(inputValue);
      setOriginalRequestId(inputValue)
      handleOriginalRequestIDValue(requestDetails.axisRequestId, FOI_COMPONENT_CONSTANTS.AXIS_REQUEST_ID);
      setIsOriginalRequestIdValid(inputValue !== "");
    };

     return (
        
        <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="axisDetails-header">
            <Typography className={classes.heading}>{getHeadingText()}</Typography>
            {isDataSynced && (
              <Chip
                  icon={<CheckCircleOutlineIcon className="synced-data-icon"/>}
                  label={"Synchronized data"}
                  className="synced-data-chip"
              />
            )}
          </AccordionSummary>
        <AccordionDetails>         
        {isAddConsultRequest ? (
          <>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col">                       
              <TextField   
                  id='originalRequestId'                         
                  label={"Original Request ID Number"}
                  inputProps={{ "aria-labelledby": "axisId-label", style: { textTransform: "uppercase" }}}
                  InputLabelProps={{ shrink: true }} 
                  InputProps={{
                    endAdornment: (
                        <InputAdornment position="end">
                            <Chip
                          icon={
                              <WarningAmberIcon
                              className={clsx(classes.warningAmberIcon)} 
                              />
                          }
                          className={clsx({
                              [classes.showIcon]: !isOriginalRequestIdValid,
                              [classes.hideIcon]: isOriginalRequestIdValid,
                          })}
                      />
                        </InputAdornment>
                    )
                  }}
                  variant="outlined"                             
                  value={originalRequestId}
                  fullWidth
                  onChange={handleOriginalRequestIDChange}
                  error={(validation.helperTextValue !== "" && validation.helperTextValue !== undefined) || originalRequestId === ""}
                  helperText={validation.helperTextValue}
                  required
              />
               <h5
                  className={clsx({
                    [classes.showOriginalRequestIdFieldValidation]: !isOriginalRequestIdValid,
                    [classes.hideOriginalRequestIdFieldValidation]: isOriginalRequestIdValid,
                  })}
               >This field is required</h5>
            </div>
          <div className="col-lg-6 foi-details-col">                       
              <button type="button" onClick={() => getOriginalRequestDetails()} style={{float: "right"}} disabled={isButtonDisabled}
              className='btn-original-request-sync'>Sync with Request</button>
          </div>
      </div>
        </>             
        ):(
          <>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col">                       
                <TextField   
                    id='axisId'                         
                    label={"AXIS ID Number"}
                    inputProps={{ "aria-labelledby": "axisId-label", style: { textTransform: "uppercase" }}}
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
        </>
            )}             
        </AccordionDetails>
      </Accordion>
      </div>      
    );
  });

export default AxisDetails;