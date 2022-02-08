import React from 'react';
import { useSelector } from "react-redux";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { formatDate } from "../../../helper/FOI/helper";
import { shouldDisableFieldForMinistryRequests } from "./utils";

const ApplicantDetails = React.memo(({requestDetails, contactDetailsNotGiven, handleApplicantDetailsInitialValue, 
    handleApplicantDetailsValue, handleEmailValidation, createSaveRequestObject, disableInput, requestStatus}) => {

    const disableFieldForMinistryRequest = shouldDisableFieldForMinistryRequests(requestStatus)
    /**
     *  Applicant Details box in the UI
     *  FirstName, LastName and Category - Mandatory fields
     */ 

    //gets the category list master data
    const category = useSelector(state=> state.foiRequests.foiCategoryList);

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

   
    //state management of Applicant FirstName, MiddleName, LastName, Organization, Email and Category
    const [applicantFirstNameText, setApplicantFirstName] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME));
    const [applicantMiddleNameText, setApplicantMiddleName] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME));
    const [applicantLastNameText, setApplicantLastName] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME));
    const [organizationText, setOrganization] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.ORGANIZATION));
    const [emailText, setEmail] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL));
    const [selectedCategory, setCategoryValue] = React.useState(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.FOI_CATEGORY,
            {
                dateFormat: false,
                defaultValue: "Select Category",
            }
            ));

    //handle initial value for required field validation
    React.useEffect(() => {
        const applicantDetailsObject = {
            firstName: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME),
            lastName: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME),
            email: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL),
            category: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.FOI_CATEGORY,
                {
                    dateFormat: false,
                    defaultValue: "Select Category",
                }),            
          }
        handleApplicantDetailsInitialValue(applicantDetailsObject);
    },[requestDetails, handleApplicantDetailsInitialValue])

    //handle onchange of firstName
    const handleFirtNameChange = (e) => {
         setApplicantFirstName(e.target.value);
         handleApplicantDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME);
         createSaveRequestObject(FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME, e.target.value);
    }
    //handle onchange of middleName
    const handleMiddleNameChange = (e) => {
         setApplicantMiddleName(e.target.value);
         createSaveRequestObject(FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME, e.target.value);
    }
    //handle onchange of lastName
    const handleLastNameChange = (e) => {
        setApplicantLastName(e.target.value);
        handleApplicantDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME, e.target.value);
    }
    //handle onchange of organization
    const handleOrganizationChange = (e) => {
        setOrganization(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ORGANIZATION, e.target.value);
    }

    //state management for email validation
    const [validation, setValidation] = React.useState({});
    //handle onchange of email and the validation
    const handleEmailChange = (e) => {
        var emailValidation = {};
        if(e.target.value) {
            const helperText =  /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e.target.value)
                ? ""
                : "Email is not valid.";
            emailValidation = {field: "Email", helperTextValue: helperText};
            setValidation(emailValidation);
             
        }
        else {
            emailValidation = {field: "Email", helperTextValue: ""}
            setValidation(emailValidation);            
        }
        handleEmailValidation(emailValidation);
        setEmail(e.target.value);
        handleApplicantDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL, e.target.value);    
    }

    //handle category change
    const handleCategoryOnChange = (e) => {
        setCategoryValue(e.target.value);
        //event bubble up - send the updated category for required field validation
        handleApplicantDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.FOI_CATEGORY);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.FOI_CATEGORY, e.target.value);   
    }
    
    //generate the menu items for the category
    const menuItems = category.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
     });    

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">APPLICANT DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                       
                        <TextField                            
                            label="Applicant First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined"                             
                            value={applicantFirstNameText}
                            fullWidth
                            onChange={handleFirtNameChange}
                            required={true}
                            disabled={disableInput}
                            error={applicantFirstNameText===""}
                        />
                        <TextField                          
                            label="Applicant Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={applicantMiddleNameText}
                            variant="outlined"
                            fullWidth
                            disabled={disableInput}
                            onChange={handleMiddleNameChange}
                        />
                        <TextField                            
                            label="Applicant Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={applicantLastNameText}
                            variant="outlined"
                            fullWidth
                            onChange={handleLastNameChange}
                            required={true}
                            disabled={disableInput}
                            error={applicantLastNameText===""}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col">                      
                       
                        <TextField                            
                            label="Organization" 
                            InputLabelProps={{ shrink: true, }} 
                            value={organizationText}
                            variant="outlined" 
                            fullWidth
                            disabled={disableInput}
                            onChange={handleOrganizationChange}
                        /> 
                        <TextField
                            id="category"
                            label="Category"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectedCategory}
                            onChange={handleCategoryOnChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth
                            required
                            disabled={disableInput || disableFieldForMinistryRequest}
                            error={selectedCategory.toLowerCase().includes("select")}
                        >            
                        {menuItems}
                        </TextField> 
                        <TextField                           
                            label="Email" 
                            InputLabelProps={{ shrink: true, }} 
                            value={emailText}
                            variant="outlined" 
                            fullWidth
                            required={true}
                            disabled={disableInput}
                            onChange={handleEmailChange}
                            error={(validation.helperTextValue !== undefined && validation.helperTextValue !== "") || (emailText == "" && contactDetailsNotGiven)}
                            helperText={validation.helperTextValue}
                        /> 
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );
  });

export default ApplicantDetails;