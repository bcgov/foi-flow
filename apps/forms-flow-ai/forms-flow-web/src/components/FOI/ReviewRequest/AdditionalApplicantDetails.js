import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import './additionalapplicantdetails.scss';
import { formatDate } from "../../../helper/FOI/helper";

import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const AdditionalApplicantDetails = React.memo(({additionalInfo, createSaveRequestObject}) => {
    /**
     *  Addition Applicant details box in the UI
     *  No mandatory fields here
     */ 
  
    //local state management for personalHealthNumber, identityVerified, correctionNumber, and birthDate
    const [personalHealthNumberText, setPersonalHealthNumber] = React.useState(!!additionalInfo.personalHealthNumber ? additionalInfo.personalHealthNumber : "0000 000 00");
    const [identityVerifiedText, setIdentityVerified] = React.useState(!!additionalInfo.identityVerified ? additionalInfo.identityVerified : "");  
    const [correctionsNumberText, setCorrectionsNumber] = React.useState(!!additionalInfo.correctionsNumber ? additionalInfo.correctionsNumber : "0000 000 00");
    const [employeeNumberText, setEmployeeNumber] = React.useState(!!additionalInfo.employeeNumber ? additionalInfo.employeeNumber : "0000 000 00");
    const dob = !!additionalInfo.birthDate ? new Date(additionalInfo.birthDate) : "";   
    const [birthDateText, setDOB] = React.useState(formatDate(dob));

  const handlePersonalHealthNumber = (e) => {
    setPersonalHealthNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER, e.target.value);
  }

  const handleIdentityVerified = (e) => {
    setIdentityVerified(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED, e.target.value);
  }

  const handleCorrectionsNumber = (e) => {
    setCorrectionsNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER, e.target.value);
  }

  const handleEmployeeNumber = (e) => {
    setEmployeeNumber(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER, e.target.value);
  }

  const handleBirthDate = (e) => {
    setDOB(e.target.value);
    createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DOB, e.target.value);
  }

     return (
      <Card className="foi-details-card">            
      <label className="foi-details-label">ADDITIONAL APPLICANT DETAILS</label>
      <CardContent>     
          <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">                       
                  <TextField                            
                      label="Personal Health Number" 
                      InputLabelProps={{ shrink: true, }} 
                      variant="outlined" 
                      value={personalHealthNumberText}
                      onChange={handlePersonalHealthNumber}
                      fullWidth
                  />                 
                  <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={birthDateText} 
                            onChange={handleBirthDate}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            fullWidth
                        />
                  
                  <TextField                            
                      label="Identity Verified" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined"
                      value={identityVerifiedText}
                      onChange={handleIdentityVerified}
                      fullWidth
                  />                                                
              </div>
              <div className="col-lg-6 foi-details-col">
                  <TextField                            
                      label="Corrections Number" 
                      InputLabelProps={{ shrink: true, }} 
                      variant="outlined" 
                      value={correctionsNumberText}
                      onChange={handleCorrectionsNumber}
                      fullWidth
                  /> 
                  <TextField                            
                      label="Employee Number" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined" 
                      value={employeeNumberText}
                      onChange={handleEmployeeNumber}
                      fullWidth
                  />                 
              </div>
          </div> 

      </CardContent>
  </Card>
    );
  });

export default AdditionalApplicantDetails;