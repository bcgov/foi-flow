import React from 'react';
import "./onbehalfofdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import { formatDate } from "../../../helper/helper";


const OnBehalfOfDetails = React.memo(({additionalInfo}) => {
  
    const [anotherFirstNameText, setAnotherFirstName] = React.useState(!!additionalInfo.anotherFirstName ? additionalInfo.anotherFirstName : "");
    const [anotherMiddleNameText, setAnotherMiddleName] = React.useState(!!additionalInfo.anotherMiddleName ? additionalInfo.anotherMiddleName : "");
    const [anotherLastNameText, setAnotherLastName] = React.useState(!!additionalInfo.anotherLastName ? additionalInfo.anotherLastName : "");
    const [anotherNickNameText, setAnotherNickName] = React.useState(!!additionalInfo.anotherAlsoKnownAs ? additionalInfo.anotherAlsoKnownAs : "");
    const dob = !!additionalInfo.anotherBirthDate ? new Date(additionalInfo.anotherBirthDate) : "";
    const dobString = formatDate(dob);
    const [anotherDOBText, setAnotherDOB] = React.useState(dobString);
    
    const handleFirtNameChange = (e) => {
        setAnotherFirstName(e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setAnotherMiddleName(e.target.value);
    }
    const handleLastNameChange = (e) => {
        setAnotherLastName(e.target.value);
    }
    const handleNickNameChange = (e) => {
        setAnotherNickName(e.target.value);
    }
    const handleDOBChange = (e) => {
        setAnotherDOB(e.target.value);
    }   
     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">ON BEHALF OF DETAILS</label>
            <CardContent>
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                        
                        <TextField                           
                            label="First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            value={anotherFirstNameText}
                            onChange={handleFirtNameChange}
                            fullWidth
                        />
                        <TextField                          
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherMiddleNameText}
                            variant="outlined" 
                            onChange={handleMiddleNameChange}
                            fullWidth
                        />
                        <TextField                           
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                            fullWidth
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col"> 
                        <TextField                            
                            label="Also Known As" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherNickNameText}
                            variant="outlined" 
                            onChange={handleNickNameChange}
                            fullWidth
                        />                       
                        <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={anotherDOBText} 
                            onChange={handleDOBChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined"
                            fullWidth
                        />                   
                        <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
                    </div>
                </div> 
            </CardContent>
        </Card>
       
    );
  });

export default OnBehalfOfDetails;