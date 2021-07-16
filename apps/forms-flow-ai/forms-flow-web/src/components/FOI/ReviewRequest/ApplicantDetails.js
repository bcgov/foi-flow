import React from 'react';
import { useSelector } from "react-redux";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';

const ApplicantDetails = React.memo(({requestDetails, handleCategoryInitialValue, handleCategoryValue, handleEmailValidation}) => {
    //gets the category list master data
    const category = useSelector(state=> state.foiRequests.foiCategoryList);

    //state management of Applicant FirstName, MiddleName, LastName, Organization, Email and Category
    const [applicantFirstNameText, setApplicantFirstName] = React.useState(requestDetails.firstName? requestDetails.firstName: "");
    const [applicantMiddleNameText, setApplicantMiddleName] = React.useState(requestDetails.middleName? requestDetails.middleName:"" );
    const [applicantLastNameText, setApplicantLastName] = React.useState(requestDetails.lastName? requestDetails.lastName:"");
    const [organizationText, setOrganization] = React.useState(requestDetails.businessName? requestDetails.businessName: "");
    const [emailText, setEmail] = React.useState(requestDetails.email ? requestDetails.email:"");
    const [selectedCategory, setCategoryValue] = React.useState(requestDetails.currentState !== "Unopened"? "Select Category":"Select Category");

    //handle initial value for required field validation
    React.useEffect(() => {       
        const categoryValue = requestDetails.currentState !== "Unopened"? "Select Category":"Select Category";
        handleCategoryInitialValue(categoryValue);
    },[requestDetails, handleCategoryInitialValue])

    //handle onchange of firstName
    const handleFirtNameChange = (e) => {
         setApplicantFirstName(e.target.value);
    }
    //handle onchange of middleName
    const handleMiddleNameChange = (e) => {
         setApplicantMiddleName(e.target.value);
    }
    //handle onchange of lastName
    const handleLastNameChange = (e) => {
        setApplicantLastName(e.target.value);
    }
    //handle onchange of organization
    const handleOrganizationChange = (e) => {
        setOrganization(e.target.value);
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
              
    }
    //handle category change
    const handleCategoryOnChange = (e) => {
        setCategoryValue(e.target.value);
        //event bubble up - send the updated category for required field validation
        handleCategoryValue(e.target.value);
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
                        />
                        <TextField                          
                            label="Applicant Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={applicantMiddleNameText}
                            variant="outlined"
                            fullWidth
                            onChange={handleMiddleNameChange}
                        />
                        <TextField                            
                            label="Applicant Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={applicantLastNameText}
                            variant="outlined"
                            fullWidth
                            onChange={handleLastNameChange}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col">                      
                       
                        <TextField                            
                            label="Organization" 
                            InputLabelProps={{ shrink: true, }} 
                            value={organizationText}
                            variant="outlined" 
                            fullWidth
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
                            onChange={handleEmailChange}
                            error={validation.helperTextValue !== undefined && validation.helperTextValue !== ""}
                            helperText={validation.helperTextValue}
                        /> 
                    </div>
                </div>             
            </CardContent>
        </Card>       
    );
  });

export default ApplicantDetails;