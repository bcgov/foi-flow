import React, {useEffect} from 'react';
import "./childdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';

import { DateTimeWithLegend } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));
const ChildDetails = React.memo(({requestDetails}) => {
    const [childFirstNameText, setChildFirstName] = React.useState(!!requestDetails.additionalpersonalInfo.childFirstName ? requestDetails.additionalpersonalInfo.childFirstName : "");
    const [childMiddleNameText, setChildMiddleName] = React.useState(!!requestDetails.additionalpersonalInfo.childmiddleName ? requestDetails.additionalpersonalInfo.childmiddleName : "");
    const [childLastNameText, setChildLastName] = React.useState(!!requestDetails.additionalpersonalInfo.childlastName ? requestDetails.additionalpersonalInfo.childlastName : "");
    const [childNickNameText, setNickName] = React.useState(!!requestDetails.additionalpersonalInfo.childalsoKnownAs ? requestDetails.additionalpersonalInfo.childalsoKnownAs : "");
    const [childDOBText, setDOB] = React.useState(!!requestDetails.additionalpersonalInfo.childbirthDate ? requestDetails.additionalpersonalInfo.childbirthDate : "");
    
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
    
    const classes = useStyles();
     return (
        
        <Card className="foi-child-details-card">            
            <label className="foi-child-details-label">CHILD DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-child-details-row">
                    <div className="col-lg-6 foi-child-details-col">                       
                        <TextField                            
                            label="First Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childFirstNameText}
                            variant="outlined"
                            onChange={handleFirtNameChange}                            
                        />
                        <TextField                            
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childMiddleNameText}
                            variant="outlined"
                            onChange={handleMiddleNameChange}
                        />
                        <TextField                            
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-child-details-col">
                        <TextField                            
                            label="Also Known As" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childNickNameText}
                            variant="outlined"
                            onChange={handleNickNameChange}
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
                        />
                        <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default ChildDetails;