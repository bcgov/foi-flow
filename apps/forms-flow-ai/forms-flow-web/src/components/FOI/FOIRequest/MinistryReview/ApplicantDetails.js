import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { InputLabel } from '@material-ui/core';



const ApplicantDetails = React.memo((requestDetails) => {


    return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">APPLICANT DETAILS</label>
            <CardContent>          
                <div className="row foi-details-row">
                  
                    <div className="col-lg-3 foi-details-col">                      
                                               
                        <TextField
                            id="applicanttype"
                            label="Applicant Type"
                            InputLabelProps={{ shrink: true, }}                                      
                            value="Interest Group"                            
                            input={<InputLabel />} 
                            variant="outlined"
                            fullWidth                           
                        >                                    
                        </TextField> 
                        </div>
                        <div className="col-lg-3 foi-details-col"> 
                        <TextField
                            id="requesttype"
                            label="Request Type"
                            InputLabelProps={{ shrink: true, }}                                      
                            value="General Request"
                            
                            input={<InputLabel />} 
                            variant="outlined"
                            fullWidth                           
                        >                                    
                        </TextField>
                        </div>
                        <div className="col-lg-3 foi-details-col">
                        <TextField
                            id="authorization"
                            label="Authorization"
                            InputLabelProps={{ shrink: true, }}                                      
                            value="YYYY MM DD"                            
                            input={<InputLabel />} 
                            variant="outlined"
                            fullWidth                           
                        >                                    
                        </TextField>
                        </div>
                    
                </div>             
            </CardContent>
        </Card>       
    );


})


export default ApplicantDetails;