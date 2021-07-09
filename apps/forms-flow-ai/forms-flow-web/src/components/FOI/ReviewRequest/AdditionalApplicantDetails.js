import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import './additionalapplicantdetails.scss';
import { makeStyles } from '@material-ui/core/styles';
import { DateTimeWithLegend } from '../customComponents';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));

const AdditionalApplicantDetails = React.memo((props) => {
    const classes = useStyles();
    const dateData = {
      "label": "Date of Birth",
      "format": "mm/dd/yyyy",
      "value": "11/20/2001",
      "disabled": false,
      "required": false
  }
     return (
      <Card className="foi-child-details-card">            
      <label className="foi-child-details-label">ADDITIONAL APPLICANT DETAILS</label>
      <CardContent>
      <form className={classes.root} noValidate autoComplete="off">
          <div className="row foi-child-details-row">
              <div className="col-lg-6 foi-child-details-col">                       
                  <TextField                            
                      label="Personal Health Number" 
                      InputLabelProps={{ shrink: true, }} 
                      variant="outlined" 
                      defaultValue="0000 000 00"
                  />
                  <DateTimeWithLegend dateData = {dateData} />
                  
                  <TextField                            
                      label="Identity Verified" 
                      InputLabelProps={{ shrink: true, }} 
                      defaultValue="BC Services Card" 
                      variant="outlined" 
                  />                                                
              </div>
              <div className="col-lg-6 foi-child-details-col">
                  <TextField                            
                      label="Corrections Number" 
                      InputLabelProps={{ shrink: true, }} 
                      defaultValue="000 000 000" 
                      variant="outlined" 
                  /> 
                  <TextField                            
                      label="Employee Number" 
                      InputLabelProps={{ shrink: true, }} 
                      defaultValue="0000" 
                      variant="outlined" 
                  /> 
                  {/* <DateTimeWithLegend dateData = {dateData} /> 
                  <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel> */}
              </div>
          </div> 
          </form>             
      </CardContent>
  </Card>
    );
  });

export default AdditionalApplicantDetails;