import React, {useEffect} from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import './additionalapplicantdetails.scss';
import { formatDate } from "../../../helper/FOI/helper";

import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const AdditionalApplicantDetails = React.memo(({requestDetails, createSaveRequestObject, disableInput}) => {
    /**
     *  Addition Applicant details box in the UI
     *  No mandatory fields here
     */ 

    const validateField = (data, name, options = {
      dateFormat: false,
      defaultValue: ""
    }) => {
      options.defaultValue = options.defaultValue || ""

      if(!data) {
        return options.defaultValue;
      }

      if(options.dateFormat) {
        return data[name] ? formatDate(data[name]) : options.defaultValue;
      }

      return data[name] || options.defaultValue;
    }
    
    //local state management for personalHealthNumber, identityVerified, correctionNumber, and birthDate
    const [personalHealthNumberText, setPersonalHealthNumber] = React.useState(
      validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER
      )
    );
    const [identityVerifiedText, setIdentityVerified] = React.useState(
      validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED
      )
    );
    const [correctionsNumberText, setCorrectionsNumber] = React.useState(
      validateField(requestDetails, FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER)
    );
    const [employeeNumberText, setEmployeeNumber] = React.useState(
      validateField(requestDetails, FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER)
    );
    const [birthDateText, setDOB] = React.useState(
      validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.DOB,
        {
          dateFormat: true,
          defaultValue: "",
        }
      )
    );

    useEffect(() => {

      setPersonalHealthNumber(validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED
      ));
      setIdentityVerified(validateField(
        requestDetails?.additionalPersonalInfo,
        FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED
      ));
      setCorrectionsNumber(validateField(requestDetails, FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER));
      setEmployeeNumber(
        validateField(requestDetails, FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER)
      );
      setDOB(
        validateField(
          requestDetails?.additionalPersonalInfo,
          FOI_COMPONENT_CONSTANTS.DOB,
          {
            dateFormat: true,
            defaultValue: "",
          }
        ));
    },[requestDetails]) 

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
                      disabled={disableInput}
                  />                 
                  <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={birthDateText || ''} 
                            onChange={handleBirthDate}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            fullWidth
                            disabled={disableInput}
                        />
                  
                  <TextField                            
                      label="Identity Verified" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined"
                      value={identityVerifiedText}
                      onChange={handleIdentityVerified}
                      fullWidth
                      disabled={disableInput}
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
                      disabled={disableInput}
                  /> 
                  <TextField                            
                      label="Employee Number" 
                      InputLabelProps={{ shrink: true, }}                       
                      variant="outlined" 
                      value={employeeNumberText}
                      onChange={handleEmployeeNumber}
                      fullWidth
                      disabled={disableInput}
                  />                 
              </div>
          </div> 

      </CardContent>
  </Card>
    );
  });

export default AdditionalApplicantDetails;