import React from 'react';

import "./applicantdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { useSelector } from "react-redux";
import { SelectWithLegend } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));
const ApplicantDetails = React.memo(({requestDetails, selectCategoryValue, handleCategoryOnChange}) => {  

  
        const applicantFirstName = requestDetails!==null && requestDetails.firstName!==null ? requestDetails.firstName: "";
        const applicantMiddleName = requestDetails!==null && requestDetails.middleName !== null? requestDetails.middleName:"" ;
        const applicantLastName = requestDetails!==null && requestDetails.lastName  !== null? requestDetails.lastName:"" ;
        const organization = requestDetails!==null && requestDetails.businessName !==null ? requestDetails.businessName: "";
        const email = requestDetails!==null && requestDetails.email !== null ? requestDetails.email:"";
        const selectDefaultValue = requestDetails!==null && requestDetails.currentState === "Unopened"? "Select Category":"Select Category";
        const [applicantFirstNameText, setApplicantFirstName] = React.useState(applicantFirstName);
        const [applicantMiddleNameText, setApplicantMiddleName] = React.useState(applicantMiddleName);
        const [applicantLastNameText, setApplicantLastName] = React.useState(applicantLastName);
        const [organizationText, setOrganization] = React.useState(organization);
        const [emailText, setEmail] = React.useState(email);
        const category = useSelector(state=> state.foiRequests.foiCategoryList);
       
    const handleFirtNameChange = (e) => {
         setApplicantFirstName(e.target.value);
    }
    const handleMiddleNameChange = (e) => {
         setApplicantMiddleName(e.target.value);
    }
    const handleLastNameChange = (e) => {
        setApplicantLastName(e.target.value);
    }
    const handleOrganizationChange = (e) => {
        setOrganization(e.target.value);
    }
    const handleEmailChange = (e) => {
        setEmail(e.target.value);
    }
    
    const menuItems = category.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
     });
    
    const classes = useStyles();
    // const [selectValue, setSelectValue] = React.useState(selectDefaultValue);   
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">APPLICANT DETAILS</label>
            <CardContent>
            {/* <form className={classes.root} autoComplete="off"> */}
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">                       
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
                    <div className="col-lg-6 foi-applicant-details-col">                      
                       
                        <TextField                            
                            label="Organization" 
                            InputLabelProps={{ shrink: true, }} 
                            value={organizationText}
                            variant="outlined" 
                            fullWidth
                            onChange={handleOrganizationChange}
                        /> 
                        {/* <SelectWithLegend id="category" selectData = {category} legend="Category" selectDefault={selectDefaultValue} required={true} onSelectChange={}/> */}
                        <TextField
                            id="category"
                            label="Category"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectCategoryValue}
                            onChange={handleCategoryOnChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth
                            required
                            error={selectCategoryValue.toLowerCase().includes("select")}
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
                        /> 
                    </div>
                </div> 
                {/* </form>              */}
            </CardContent>
        </Card>
       
    );
  });

export default ApplicantDetails;