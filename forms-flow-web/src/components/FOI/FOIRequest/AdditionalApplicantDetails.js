import React, {useEffect} from 'react';
import TextField from '@material-ui/core/TextField';
import './additionalapplicantdetails.scss';
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { Box, Fade } from "@mui/material";

const AdditionalApplicantDetails = React.memo(({requestDetails, createSaveRequestObject, disableInput, defaultExpanded, warning}) => {
    /**
     *  Addition Applicant details box in the UI
     *  No mandatory fields here
     */ 

     const useStyles = makeStyles({
      heading: {
        color: '#FFF',
        fontSize: '16px !important',
        fontWeight: 'bold !important'
      },
      accordionSummary: {
        flexDirection: 'row-reverse'
      },
      warning: {
        '& fieldset': {
          borderColor: '#ed6c02 !important'
        },
        '& label': {
          color: '#ed6c02 !important'
        }
      
      }
    });
    const classes = useStyles();
    const validateField = (data, name, options = {
      dateFormat: false,
      defaultValue: ""
    }) => {
      options.defaultValue = options.defaultValue || ""

      if(!data) {
        return options.defaultValue;
      }

      if(options.dateFormat) {
        return data[name] ? formatDate(data[name]) : options.defaultValue;
      }

      return data[name] || options.defaultValue;
    }
    
    //local state management for personalHealthNumber, identityVerified, correctionNumber, and birthDate
    const [personalHealthNumberText, setPersonalHealthNumber] = React.useState(
      validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER
      )
    );
    const [identityVerifiedText, setIdentityVerified] = React.useState(
      validateField(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED
      )
    );
    const [correctionsNumberText, setCorrectionsNumber] = React.useState(
      validateField(requestDetails, FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER)
    );
    const [employeeNumberText, setEmployeeNumber] = React.useState(
      validateField(requestDetails, FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER)
    );
    const [alsoKnownAsText, setAlsoKnownAs] = React.useState(
      validateField(requestDetails?.additionalPersonalInfo, FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS)
    );
    const [birthDateText, setDOB] = React.useState(
      validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.DOB,
        {
          dateFormat: true,
          defaultValue: "",
        }
      )
    );

    useEffect(() => {

      setPersonalHealthNumber(validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER
      ));
      setIdentityVerified(validateField(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED
      ));
      setCorrectionsNumber(validateField(requestDetails, FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER));
      setEmployeeNumber(
        validateField(requestDetails, FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER)
      );
      setDOB(
        validateField(
          requestDetails?.additionalPersonalInfo,
          FOI_COMPONENT_CONSTANTS.DOB,
          {
            dateFormat: true,
            defaultValue: "",
          }
        ));
      setAlsoKnownAs(validateField(
          requestDetails?.additionalPersonalInfo,
          FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS
        ))
    },[requestDetails]) 

  const handlePersonalHealthNumber = (e) => {
    setPersonalHealthNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, e.target.value);
  }

  const handleIdentityVerified = (e) => {
    setIdentityVerified(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED, e.target.value);
  }

  const handleCorrectionsNumber = (e) => {
    setCorrectionsNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER, e.target.value);
  }

  const handleEmployeeNumber = (e) => {
    setEmployeeNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER, e.target.value);
  }

  const handleAlsoKnownAs = (e) => {
    if (e.target.value?.length <= 250){
      setAlsoKnownAs(e.target.value);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS, e.target.value);
    }
  }

  const handleBirthDate = (e) => {
    setDOB(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DOB, e.target.value);
  }

     return (
      <div className='request-accordian' >
      <Accordion defaultExpanded={defaultExpanded}>
      <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} 
        id="additionalApplicantDetails-header">
        <Typography className={classes.heading}>ADDITIONAL APPLICANT DETAILS</Typography>
      </AccordionSummary>
      <AccordionDetails>
          <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">                       
                  <TextField   
                      id='personalHealthNumber'                         
                      label="Personal Health Number" 
                      inputProps={{ "aria-labelledby": "personalHealthNumber-label"}}
                      InputLabelProps={{ shrink: true, }} 
                      variant="outlined" 
                      className={warning && warning(FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER) && classes.warning}
                      value={personalHealthNumberText}
                      onChange={handlePersonalHealthNumber}
                      fullWidth
                      disabled={disableInput}
                  />                 
                  <TextField        
                    id='DOB'
                    label="Date of Birth"
                    type="date" 
                    value={birthDateText || ''} 
                    onChange={handleBirthDate}
                    inputProps={{ "aria-labelledby": "DOB-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    variant="outlined" 
                    className={warning && warning(FOI_COMPONENT_CONSTANTS.DOB) && classes.warning}
                    fullWidth
                    disabled={disableInput}
                  />
                  
                  <TextField  
                    id='identityVerified'                          
                    label="Identity Verified" 
                    inputProps={{ "aria-labelledby": "identityVerified-label"}}
                    InputLabelProps={{ shrink: true, }}                       
                    variant="outlined"
                    value={identityVerifiedText}
                    onChange={handleIdentityVerified}
                    fullWidth
                    disabled
                  />                                                
              </div>
              <div className="col-lg-6 foi-details-col">
                  <TextField       
                    id='correctionsNumber'                     
                    label="Corrections Number" 
                    inputProps={{ "aria-labelledby": "correctionsNumber-label"}}
                    InputLabelProps={{ shrink: true, }} 
                    variant="outlined" 
                    className={warning && warning(FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER) && classes.warning}
                    value={correctionsNumberText}
                    onChange={handleCorrectionsNumber}
                    fullWidth
                    disabled={disableInput}
                  /> 
                  <TextField   
                      id='employeeNumber'                         
                      label="Employee Number" 
                      inputProps={{ "aria-labelledby": "employeeNumber-label"}}
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined" 
                      value={employeeNumberText}
                      className={warning && warning(FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER) && classes.warning}
                      onChange={handleEmployeeNumber}
                      fullWidth
                      disabled={disableInput}
                  />
                  <Box>
                    <TextField   
                        id='alsoKnownAsText'                         
                        label="Also Known As" 
                        inputProps={{ "aria-labelledby": "alsoKnownAsText-label", maxLength: 250}}
                        InputLabelProps={{ shrink: true, }}                       
                        variant="outlined" 
                        value={alsoKnownAsText}
                        className={warning && warning(FOI_COMPONENT_CONSTANTS.ALSO_KNOWN_AS) && classes.warning}
                        onChange={handleAlsoKnownAs}
                        fullWidth
                        disabled={disableInput}
                        error={alsoKnownAsText.length >= 250}
                        helperText={(alsoKnownAsText.length >= 250) ? "250 character limit reached" : ""}
                        multiline
                        minRows={1}
                        maxRows={3}
                    />
                    <Fade in={alsoKnownAsText.length > 0 && alsoKnownAsText.length < 250} timeout={300}>     
                      <Typography
                        variant="caption"
                        sx={{
                          display: "block",
                          textAlign: "right",
                          mt: 0.5,
                          color: alsoKnownAsText.length >= 250 ? "error.main" : "text.secondary",
                          wordBreak: "break-word", // ensures text wraps instead of being cut off
                        }}
                      >
                        {alsoKnownAsText.length}/{250} characters
                      </Typography>
                    </Fade> 
                  </Box>              
              </div>
          </div> 
        </AccordionDetails>
    </Accordion>
  </div>
    );
  });

export default AdditionalApplicantDetails;