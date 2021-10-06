import React from 'react';
import { InputLabel } from '@material-ui/core';
import Link from '@material-ui/core/Link';
import TextField from '@material-ui/core/TextField';
import MinistryAssignToDropdown from '../MinistryAssignToDropdown';

const RequestHeader = React.memo((requestDetails) => {

    const preventDefault = (event) => event.preventDefault();

    const handleMinistryAssignedToValue =()=>{

    }

    const createSaveRequestObject = () =>{

    }

    

    return (

        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h3 className="foi-review-request-text">Request # EDUC-2021</h3>
                    </Link>
                </div>           
            </div>
            
            <div className="foi-assigned-to-container">
                <div className="foi-assigned-to-inner-container">
                <TextField
                    id="assignedTo"
                    label="IAO Assigned To"
                    InputLabelProps={{ shrink: true, }}                              
                    value="Abin Antony"                    
                    input={<InputLabel />} 
                    variant="outlined"
                    fullWidth                    
                    disabled = {true}                                        
                >                               
                </TextField> 
                </div>

            
                    <>
                      <MinistryAssignToDropdown requestDetails={requestDetails} handleMinistryAssignedToValue={handleMinistryAssignedToValue} createSaveRequestObject={createSaveRequestObject} isMinistryCoordinator={true} />
                    </>
                
            </div>
        </div>




    );




})

export default RequestHeader