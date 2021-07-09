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
const ChildDetails = React.memo((props) => {
  
    useEffect(() => {       
        
    }, [])

    const dateData = {
        "label": "Date of Birth",
        "format": "mm/dd/yyyy",
        "value": "11/20/2001",
        "disabled": false,
        "required": false
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
                            variant="outlined" 
                            defaultValue="Jane"
                        />
                        <TextField                            
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="M" 
                            variant="outlined" 
                        />
                        <TextField                            
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="Deo" 
                            variant="outlined" 
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-child-details-col">
                        <TextField                            
                            label="Also Known As" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="nickname" 
                            variant="outlined" 
                        /> 
                        <DateTimeWithLegend dateData = {dateData} /> 
                        <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default ChildDetails;