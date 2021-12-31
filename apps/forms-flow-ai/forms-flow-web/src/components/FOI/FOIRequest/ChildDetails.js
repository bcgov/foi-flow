import React from 'react';
import "./childdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import { formatDate } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const ChildDetails = React.memo(({additionalInfo, createSaveRequestObject, disableInput}) => {

     /**
     *  Child details box in the UI
     *  No mandatory fields here
     */ 

    const validateFields = (data, name, options = {
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

   

    //local states for Child FirstName, MiddleName, LastName, NickName and DOB
    const [childFirstNameText, setChildFirstName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME));
    const [childMiddleNameText, setChildMiddleName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME));
    const [childLastNameText, setChildLastName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME));
    const [childNickNameText, setNickName] = React.useState(validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME));
    const dob = validateFields(additionalInfo, FOI_COMPONENT_CONSTANTS.CHILD_DOB);
    const [childDOBText, setDOB] = React.useState(dob);
 
    const handleFirtNameChange = (e) => {
        setChildFirstName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME, e.target.value);
    }
    const handleMiddleNameChange = (e) => {
        setChildMiddleName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME, e.target.value);
    }
    const handleLastNameChange = (e) => {
        setChildLastName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME, e.target.value);
    }
    const handleNickNameChange = (e) => {
        setNickName(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME, e.target.value);
    }
    const handleDOBChange = (e) => {
        setDOB(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CHILD_DOB, e.target.value);
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
                            disabled={disableInput}
                        />
                        <TextField                            
                            label="Middle Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childMiddleNameText}
                            variant="outlined"
                            onChange={handleMiddleNameChange}
                            fullWidth
                            disabled={disableInput}
                        />
                        <TextField                            
                            label="Last Name" 
                            InputLabelProps={{ shrink: true, }} 
                            value={childLastNameText}
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
                            value={childNickNameText}
                            variant="outlined"
                            onChange={handleNickNameChange}
                            fullWidth
                            disabled={disableInput}
                        />                        
                        <TextField                
                            label="Date of Birth"
                            type="date" 
                            value={childDOBText||''} 
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

export default ChildDetails;