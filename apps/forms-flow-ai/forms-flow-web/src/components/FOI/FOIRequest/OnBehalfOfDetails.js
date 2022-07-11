import React from 'react';
import "./onbehalfofdetails.scss";
import TextField from '@material-ui/core/TextField';
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

const OnBehalfOfDetails = React.memo(({additionalInfo, createSaveRequestObject, disableInput}) => {
    
     /**
     *  On Behalf of details box in the UI
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
        }
      });
      
      const classes = useStyles();

      const validateFields = (data, name, options = {
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

     

    //local states for Another person FirstName, MiddleName, LastName, NickName and DOB
    const [anotherFirstNameText, setAnotherFirstName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME));
    const [anotherMiddleNameText, setAnotherMiddleName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME));
    const [anotherLastNameText, setAnotherLastName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME));
    const [anotherNickNameText, setAnotherNickName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME));
    const dob = validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_DOB);
    const [anotherDOBText, setAnotherDOB] = React.useState(dob);
    
    const handleFirtNameChange = (e) => {
        setAnotherFirstName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME, e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setAnotherMiddleName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME, e.target.value);
    }
    const handleLastNameChange = (e) => {
        setAnotherLastName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME, e.target.value);
    }
    const handleNickNameChange = (e) => {
        setAnotherNickName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME, e.target.value);
    }
    const handleDOBChange = (e) => {
        setAnotherDOB(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_DOB, e.target.value);
    }   
     return (
        
        <div className='request-accordian' id="onBehalfOfDetails">
        <Accordion defaultExpanded={true}>
        <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} 
            id="onBehalfOfDetails-header">
            <Typography className={classes.heading}>ON BEHALF OF DETAILS</Typography>
        </AccordionSummary>
        <AccordionDetails>
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                        
                        <TextField      
                            id='onBehalfOfFirstName'                     
                            label="First Name" 
                            inputProps={{ "aria-labelledby": "onBehalfOfFirstName-label"}}
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            value={anotherFirstNameText}
                            onChange={handleFirtNameChange}
                            fullWidth
                            disabled={disableInput}
                        />
                        <TextField       
                            id='onBehalfOfMiddleName'                    
                            label="Middle Name" 
                            inputProps={{ "aria-labelledby": "onBehalfOfMiddleName-label"}}
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherMiddleNameText}
                            variant="outlined" 
                            onChange={handleMiddleNameChange}
                            fullWidth
                            disabled={disableInput}
                        />
                        <TextField      
                            id='onBehalfOfLastName'                     
                            label="Last Name" 
                            inputProps={{ "aria-labelledby": "onBehalfOfLastName-label"}}
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                            fullWidth
                            disabled={disableInput}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col"> 
                        <TextField                 
                            id='onBehalfOfAlsoKnownAs'           
                            label="Also Known As" 
                            inputProps={{ "aria-labelledby": "onBehalfOfAlsoKnownAs-label"}}
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherNickNameText}
                            variant="outlined" 
                            onChange={handleNickNameChange}
                            fullWidth
                            disabled={disableInput}
                        />                       
                        <TextField       
                            id='onBehalfOfDOB'         
                            label="Date of Birth"
                            type="date" 
                            value={anotherDOBText||''} 
                            onChange={handleDOBChange}
                            inputProps={{ "aria-labelledby": "onBehalfOfDOB-label"}}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined"
                            fullWidth
                            disabled={disableInput}
                        />                   
                    </div>
                </div> 
            </AccordionDetails>
      </Accordion>
    </div>
    );
  });

export default OnBehalfOfDetails;