import React from 'react';
import "./onbehalfofdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const OnBehalfOfDetails = React.memo(({additionalInfo, createSaveRequestObject, disableInput}) => {
    
     /**
     *  On Behalf of details box in the UI
     *  No mandatory fields here
     */ 

       const getFirstName = (request) =>{
        return !!request.anotherFirstName ? request.anotherFirstName : "";
       }
       const getMiddleName = (request) =>{
        return !!request.anotherMiddleName ? request.anotherMiddleName : "";
       }
       const getLastName =(request) =>{
        return !!request.anotherLastName ? request.anotherLastName : "";
       }
       const getNickName = (request) =>{
        return !!request.anotherAlsoKnownAs ? request.anotherAlsoKnownAs : "";
       }
       const getDOB = (request) =>{
        return !!request.anotherBirthDate ? formatDate(request.anotherBirthDate) : "";
       }


      const validateFields = (request, name) => {
        if (request !== undefined) {
          switch(name){
            case (FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME):
              return getFirstName(request);
            case (FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME):
              return getMiddleName(request);
            case (FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME):
              return getLastName(request);
            case (FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME):
              return getNickName(request);
            case (FOI_COMPONENT_CONSTANTS.ANOTHER_DOB):
              return getDOB(request);
         }
        }
        return "";
      }

    //local states for Another person FirstName, MiddleName, LastName, NickName and DOB
    const [anotherFirstNameText, setAnotherFirstName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME));
    const [anotherMiddleNameText, setAnotherMiddleName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME));
    const [anotherLastNameText, setAnotherLastName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME));
    const [anotherNickNameText, setAnotherNickName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME));
    const dob = validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.ANOTHER_DOB);
    const [anotherDOBText, setAnotherDOB] = React.useState(dob);
    
    const handleFirtNameChange = (e) => {
        setAnotherFirstName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME, e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setAnotherMiddleName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME, e.target.value);
    }
    const handleLastNameChange = (e) => {
        setAnotherLastName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME, e.target.value);
    }
    const handleNickNameChange = (e) => {
        setAnotherNickName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME, e.target.value);
    }
    const handleDOBChange = (e) => {
        setAnotherDOB(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ANOTHER_DOB, e.target.value);
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
                            disabled={disableInput}
                        />
                        <TextField                          
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherMiddleNameText}
                            variant="outlined" 
                            onChange={handleMiddleNameChange}
                            fullWidth
                            disabled={disableInput}
                        />
                        <TextField                           
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={anotherLastNameText}
                            variant="outlined"
                            onChange={handleLastNameChange}
                            fullWidth
                            disabled={disableInput}
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
                            disabled={disableInput}
                        />                       
                        <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={anotherDOBText||''} 
                            onChange={handleDOBChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined"
                            fullWidth
                            disabled={disableInput}
                        />                   
                        <InputLabel id="demo-simple-select-label" className="foi-attached-documents-label">Attached Documents</InputLabel>
                    </div>
                </div> 
            </CardContent>
        </Card>
       
    );
  });

export default OnBehalfOfDetails;