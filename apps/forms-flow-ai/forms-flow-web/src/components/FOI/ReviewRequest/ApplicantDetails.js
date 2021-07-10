import React from 'react';

import "./applicantdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
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
const ApplicantDetails = React.memo(({requestDetails}) => {  

console.log(`requestDetails = ${JSON.stringify(requestDetails)}`);
 const applicantFirstName = requestDetails!==null && requestDetails.firstName!==null ? requestDetails.firstName: "";
 const applicantMiddleName = requestDetails!==null && requestDetails.middleName !== null? requestDetails.middleName:"" ;
 const applicantLastName = requestDetails!==null && requestDetails.lastName  !== null? requestDetails.lastName:"" ;
const organization = requestDetails!==null && requestDetails.businessName !==null ? requestDetails.businessName: "";
const selectDefaultValue = requestDetails!==null && requestDetails.currentState === "Unopened"? "Select Category":"Select Category";
console.log(`select = ${selectDefaultValue}`);
const email = requestDetails!==null && requestDetails.email !== null ? requestDetails.email:"";
    const category = useSelector(state=> state.foiRequests.foiCategoryList);
    // const foiRequestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
    
    const classes = useStyles();
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">APPLICANT DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">                       
                        <TextField                            
                            label="Applicant First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined"                             
                            value={applicantFirstName}
                            fullWidth
                        />
                        <TextField                          
                            label="Applicant Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                           value={applicantMiddleName}
                            variant="outlined"
                            fullWidth
                        />
                        <TextField                            
                            label="Applicant Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={applicantLastName}
                            variant="outlined"
                            fullWidth 
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-applicant-details-col">                      
                       
                        <TextField                            
                            label="Organization" 
                            InputLabelProps={{ shrink: true, }} 
                            value={organization}
                            variant="outlined" 
                            fullWidth
                        /> 
                        <SelectWithLegend selectData = {category} legend="Category" selectDefault={selectDefaultValue} required={true}/>
                       
                        <TextField                           
                            label="Email" 
                            InputLabelProps={{ shrink: true, }} 
                            value={email}
                            variant="outlined" 
                            fullWidth
                        /> 
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default ApplicantDetails;