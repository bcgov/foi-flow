import React, {useEffect} from 'react';
import { InputLabel } from '@material-ui/core';
import Link from '@material-ui/core/Link';
import TextField from '@material-ui/core/TextField';
import MinistryAssignToDropdown from '../MinistryAssignToDropdown';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { openRequestDetails } from '../../../../apiManager/services/FOI/foiRequestServices';
import RequestDetails from './RequestDetails';
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIFullAssignedToList } from "../../../../apiManager/services/FOI/foiRequestServices";

const RequestHeader = React.memo((requestDetails) => {
    const _requestDetails = requestDetails.requestDetails;

    const preventDefault = (event) => event.preventDefault();

    const handleMinistryAssignedToValue =()=>{

    }

    const createSaveRequestObject = () =>{

    }

    const dispatch = useDispatch();
    useEffect(() => {
      dispatch(fetchFOIFullAssignedToList());
    },[dispatch]); 

    const assignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
    function getFullName(assignedToList, requestDetails) {
        const groupName = requestDetails.assignedGroup ? requestDetails.assignedGroup : "Unassigned";
        const assignedTo = requestDetails.assignedTo ? requestDetails.assignedTo : groupName;
        if (assignedToList.length > 0) {
            const assigneeGroup = assignedToList.find(_assigneeGroup => _assigneeGroup.name === groupName);
            const assignee = assigneeGroup && assigneeGroup.members && assigneeGroup.members.find(_assignee => _assignee.username === assignedTo);
            if (groupName === assignedTo) {
                return groupName;
            }
            else {
                return assignee !== undefined ? `${assignee.lastname}, ${assignee.firstname}`: "invalid user";
            }
        }
        else {
            return groupName;
        }
    }

    const headerText = _requestDetails.idNumber ? `Request #${_requestDetails.idNumber}` : FOI_COMPONENT_CONSTANTS.REVIEW_REQUEST;
    const assignedToValue = getFullName(assignedToList, _requestDetails);

    return (

        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h1 className="foi-review-request-text foi-ministry-requestheadertext">{headerText}</h1>
                    </Link>
                </div>
                <div className="foi-request-review-header-col1-row" style={{marginTop:5+'px',display:'block'}}>
                    <img src="/assets/Images/wacher.PNG" alt="wacher" style={{width:200+'px',height:50+'px'}} />
                </div>
            </div>
            
            <div className="foi-assigned-to-container">
                <div className="foi-assigned-to-inner-container">
                <TextField
                    id="assignedTo"
                    label="IAO Assigned To"
                    InputLabelProps={{ shrink: true, }}                              
                    value={assignedToValue}                    
                    input={<InputLabel />} 
                    variant="outlined"
                    fullWidth                    
                    disabled = {true}                                        
                >                               
                </TextField> 
                </div>

            
                    <>
                      <MinistryAssignToDropdown requestDetails={_requestDetails} handleMinistryAssignedToValue={handleMinistryAssignedToValue} createSaveRequestObject={createSaveRequestObject} isMinistryCoordinator={true} />
                    </>
                
            </div>
        </div>




    );




})

export default RequestHeader