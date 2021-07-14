import React from 'react';
import "./childdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import { formatDate } from "../../../helper/helper";

const ChildDetails = React.memo(({additionalInfo}) => {
    const [childFirstNameText, setChildFirstName] = React.useState(!!additionalInfo.childFirstName ? additionalInfo.childFirstName : "");
    const [childMiddleNameText, setChildMiddleName] = React.useState(!!additionalInfo.childMiddleName ? additionalInfo.childMiddleName : "");
    const [childLastNameText, setChildLastName] = React.useState(!!additionalInfo.childLastName ? additionalInfo.childLastName : "");
    const [childNickNameText, setNickName] = React.useState(!!additionalInfo.childAlsoKnownAs ? additionalInfo.childAlsoKnownAs : "");
    const dob = !!additionalInfo.childBirthDate ? new Date(additionalInfo.childBirthDate) : "";
    const dobString = formatDate(dob);
    const [childDOBText, setDOB] = React.useState(dobString);

    const handleFirtNameChange = (e) => {
        setChildFirstName(e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setChildMiddleName(e.target.value);
    }
    const handleLastNameChange = (e) => {
        setChildLastName(e.target.value);
    }
    const handleNickNameChange = (e) => {
        setNickName(e.target.value);
    }
    const handleDOBChange = (e) => {
        setDOB(e.target.value);
    }  
     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">CHILD DETAILS</label>
            <CardContent>
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                       
                        <TextField                            
                            label="First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childFirstNameText}
                            variant="outlined"
                            onChange={handleFirtNameChange}
                            fullWidth                         
                        />
                        <TextField                            
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childMiddleNameText}
                            variant="outlined"
                            onChange={handleMiddleNameChange}
                            fullWidth
                        />
                        <TextField                            
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                            fullWidth
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col">
                        <TextField                            
                            label="Also Known As" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childNickNameText}
                            variant="outlined"
                            onChange={handleNickNameChange}
                            fullWidth
                        />                        
                        <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={childDOBText} 
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

export default ChildDetails;