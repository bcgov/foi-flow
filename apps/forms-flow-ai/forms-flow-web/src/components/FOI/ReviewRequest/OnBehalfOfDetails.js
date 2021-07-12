import React from 'react';
import "./onbehalfofdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';

import { makeStyles } from '@material-ui/core/styles';
import { formatDate } from "../../../helper/helper";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));
const OnBehalfOfDetails = React.memo(({additionalInfo}) => {
  
    const [anotherFirstNameText, setAnotherFirstName] = React.useState(!!additionalInfo.anotherFirstName ? additionalInfo.anotherFirstName : "");
    const [anotherMiddleNameText, setAnotherMiddleName] = React.useState(!!additionalInfo.anothermiddleName ? additionalInfo.anothermiddleName : "");
    const [anotherLastNameText, setAnotherLastName] = React.useState(!!additionalInfo.anotherastName ? additionalInfo.anotherastName : "");
    const [anotherNickNameText, setAnotherNickName] = React.useState(!!additionalInfo.anotheralsoKnownAs ? additionalInfo.anotheralsoKnownAs : "");
    const dob = !!additionalInfo.anotherbirthDate ? new Date(additionalInfo.anotherbirthDate) : "";
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
    const classes = useStyles();
     return (
        
        <Card className="foi-onbehalf-details-card">            
            <label className="foi-onbehalf-details-label">ON BEHALF OF DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-onbehalf-details-row">
                    <div className="col-lg-6 foi-onbehalf-details-col">                        
                        <TextField                           
                            label="First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            value={anotherFirstNameText}
                            onChange={handleFirtNameChange}
                        />
                        <TextField                          
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherMiddleNameText}
                            variant="outlined" 
                            onChange={handleMiddleNameChange}
                        />
                        <TextField                           
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-onbehalf-details-col"> 
                        <TextField                            
                            label="Also Known As" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherNickNameText}
                            variant="outlined" 
                            onChange={handleNickNameChange}
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
                        />                   
                        <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default OnBehalfOfDetails;