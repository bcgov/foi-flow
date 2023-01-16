import React, {useEffect} from 'react';
import { InputLabel } from '@material-ui/core';
import Link from '@material-ui/core/Link';
import TextField from '@material-ui/core/TextField';
import MinistryAssignToDropdown from '../MinistryAssignToDropdown';
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIFullAssignedToList } from "../../../../apiManager/services/FOI/foiMasterDataServices";
import { Watcher } from '../../customComponents';
import { useParams } from 'react-router-dom';
import { getHeaderText } from './utils';
import { StateEnum } from '../../../../constants/FOI/statusEnum';

const RequestHeader = React.memo(({requestDetails, userDetail, handleMinistryAssignedToValue, setSaveMinistryRequestObject}) => {

    const { requestId, ministryId } = useParams();
    const _requestDetails = requestDetails;
    const ministryAssignedToList = useSelector(state=> state.foiRequests.foiMinistryAssignedToList);
    const requestState = requestDetails?.currentState;
    const assignedToList = useSelector(
      (state) => state.foiRequests.foiFullAssignedToList
    );
    const preventDefault = (event) => event.preventDefault();

    const dispatch = useDispatch();
    useEffect(() => {
      if (assignedToList?.length === 0) {
        dispatch(fetchFOIFullAssignedToList());
      }
    }, [dispatch]); 

    const getGroupName = () => {
        if (_requestDetails.assignedGroup)
            return _requestDetails.assignedGroup;
        return "Unassigned";
    }

    const getAssignedTo = (groupName) => {
        if (_requestDetails.assignedTo)
            return _requestDetails.assignedTo;
        return groupName;
    }
    function getFullName() {
        const groupName = getGroupName();
        const assignedTo = getAssignedTo(groupName);
        if (assignedToList?.length > 0) {
            const assigneeGroup = assignedToList.find(_assigneeGroup => _assigneeGroup.name === groupName);
            const assignee = assigneeGroup?.members?.find(_assignee => _assignee.username === assignedTo);
            if (groupName === assignedTo) 
                return groupName;
            return assignee !== undefined ? `${assignee.lastname}, ${assignee.firstname}`: "invalid user";
        }
        return groupName;
    }

    
    const headerText = getHeaderText(_requestDetails);

    document.title = headerText;
    
    const assignedToValue = getFullName();

    // const disableInput = false;
    // const isIAORestrictedRequest = false;
    const setIsLoaded = () => {};

    const watcherBox = (
        requestState?.toLowerCase() == StateEnum.closed.name.toLowerCase() ?
        (<></>)
        :
        (
            <Watcher
                watcherFullList={ministryAssignedToList}
                ministryId={ministryId}
                userDetail={userDetail}
                // disableInput={disableInput}
                // isIAORestrictedRequest={isIAORestrictedRequest}
                setIsLoaded={setIsLoaded}
            />
        )
      );

    return (

        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row axis-request-id">
                    <Link href="#" onClick={preventDefault}>
                        <h1 className="foi-review-request-text foi-ministry-requestheadertext">{headerText}</h1>
                    </Link>
                </div>
                <div className="foi-request-review-header-col1-row axis-request-id" style={{marginTop:5+'px',display:'block'}}>
                    {watcherBox}
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
                    <MinistryAssignToDropdown requestState={requestState} requestDetails={_requestDetails} 
                    ministryAssignedToList={ministryAssignedToList} 
                    handleMinistryAssignedToValue={handleMinistryAssignedToValue} 
                    isMinistryCoordinator={true} requestId={requestId} ministryId={ministryId} 
                    setSaveMinistryRequestObject={setSaveMinistryRequestObject} />
                </>
            </div>
        </div>




    );




})

export default RequestHeader