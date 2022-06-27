import React from 'react';
import "./childdetails.scss";
import TextField from '@material-ui/core/TextField';
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import {closeChildDetails} from '../FOIRequest/utils';


const ChildDetails = React.memo(({additionalInfo, createSaveRequestObject, disableInput,userDetail,requestType}) => {

     /**
     *  Child details box in the UI
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

   

    //local states for Child FirstName, MiddleName, LastName, NickName and DOB
    const [childFirstNameText, setChildFirstName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME));
    const [childMiddleNameText, setChildMiddleName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME));
    const [childLastNameText, setChildLastName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME));
    const [childNickNameText, setNickName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME));
    const dob = validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_DOB);
    const [childDOBText, setDOB] = React.useState(dob);
 
    const handleFirtNameChange = (e) => {
        setChildFirstName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME, e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setChildMiddleName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME, e.target.value);
    }
    const handleLastNameChange = (e) => {
        setChildLastName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME, e.target.value);
    }
    const handleNickNameChange = (e) => {
        setNickName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME, e.target.value);
    }
    const handleDOBChange = (e) => {
        setDOB(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_DOB, e.target.value);
    }  
     return (
        
        <div className='request-accordian' id="childDetails">
        <Accordion defaultExpanded={!closeChildDetails(userDetail,requestType)} >
        <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} 
            id="childDetails-header">
            <Typography className={classes.heading}>CHILD DETAILS</Typography>
        </AccordionSummary>
        <AccordionDetails>
            <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">                       
                    <TextField   
                        id='childFirstName'                        
                        label="First Name" 
                        inputProps={{ "aria-labelledby": "childFirstName-label"}}
                        InputLabelProps={{ shrink: true, }} 
                        value={childFirstNameText}
                        variant="outlined"
                        onChange={handleFirtNameChange}
                        fullWidth
                        disabled={disableInput}
                    />
                    <TextField            
                        id='childMiddleName'                
                        label="Middle Name" 
                        inputProps={{ "aria-labelledby": "childMiddleName-label"}}
                        InputLabelProps={{ shrink: true, }} 
                        value={childMiddleNameText}
                        variant="outlined"
                        onChange={handleMiddleNameChange}
                        fullWidth
                        disabled={disableInput}
                    />
                    <TextField          
                        id='childLastName'                  
                        label="Last Name" 
                        inputProps={{ "aria-labelledby": "childLastName-label"}}
                        InputLabelProps={{ shrink: true, }} 
                        value={childLastNameText}
                        variant="outlined"
                        onChange={handleLastNameChange}
                        fullWidth
                        disabled={disableInput}
                    />                                                
                </div>
                <div className="col-lg-6 foi-details-col">
                    <TextField          
                        id='childAlsoKnownAs'                  
                        label="Also Known As" 
                        inputProps={{ "aria-labelledby": "childAlsoKnownAs-label"}}
                        InputLabelProps={{ shrink: true, }} 
                        value={childNickNameText}
                        variant="outlined"
                        onChange={handleNickNameChange}
                        fullWidth
                        disabled={disableInput}
                    />                        
                    <TextField        
                        id='childDOB'        
                        label="Date of Birth"
                        type="date" 
                        value={childDOBText||''} 
                        onChange={handleDOBChange}
                        inputProps={{ "aria-labelledby": "childDOB-label"}}
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

export default ChildDetails;