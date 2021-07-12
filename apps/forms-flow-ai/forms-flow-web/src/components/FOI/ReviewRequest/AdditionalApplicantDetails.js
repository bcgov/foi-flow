import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import './additionalapplicantdetails.scss';
import { makeStyles } from '@material-ui/core/styles';
import { DateTimeWithLegend } from '../customComponents';
import { formatDate } from "../../../helper/helper";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));

const AdditionalApplicantDetails = React.memo(({additionalInfo}) => {
    const classes = useStyles();
  
    const [personalHealthNumberText, setPersonalHealthNumber] = React.useState(!!additionalInfo.personalHealthNumber ? additionalInfo.personalHealthNumber : "0000 000 00");
    const [identityVerifiedText, setIdentityVerified] = React.useState(!!additionalInfo.identityVerified ? additionalInfo.identityVerified : "");  
    const [correctionsNumberText, setCorrectionsNumber] = React.useState(!!additionalInfo.correctionsNumber ? additionalInfo.correctionsNumber : "0000 000 00");
    const [employeeNumberText, setEmployeeNumber] = React.useState(!!additionalInfo.employeeNumber ? additionalInfo.employeeNumber : "0000 000 00");
    const dob = !!additionalInfo.birthDate ? new Date(additionalInfo.birthDate) : "";
    const dobString = formatDate(dob);
    const [birthDateText, setDOB] = React.useState(dobString);

  const handlePersonalHealthNumber = (e) => {
    setPersonalHealthNumber(e.target.value);
  }

  const handleIdentityVerified = (e) => {
    setIdentityVerified(e.target.value);
  }

  const handleCorrectionsNumber = (e) => {
    setCorrectionsNumber(e.target.value);
  }

  const handleEmployeeNumber = (e) => {
    setEmployeeNumber(e.target.value);
  }

  const handleBirthDate = (e) => {
    setDOB(e.target.value);
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
                      value={personalHealthNumberText}
                      onChange={handlePersonalHealthNumber}
                  />
                  {/* <DateTimeWithLegend dateData = {dateData} /> */}
                  <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={birthDateText} 
                            onChange={handleBirthDate}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                        />
                  
                  <TextField                            
                      label="Identity Verified" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined"
                      value={identityVerifiedText}
                      onChange={handleIdentityVerified}
                  />                                                
              </div>
              <div className="col-lg-6 foi-child-details-col">
                  <TextField                            
                      label="Corrections Number" 
                      InputLabelProps={{ shrink: true, }} 
                      variant="outlined" 
                      value={correctionsNumberText}
                      onChange={handleCorrectionsNumber}
                  /> 
                  <TextField                            
                      label="Employee Number" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined" 
                      value={employeeNumberText}
                      onChange={handleEmployeeNumber}
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