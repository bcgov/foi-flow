import React, {useEffect, useState} from 'react';
import { Grid, InputLabel } from '@material-ui/core';
import Link from '@material-ui/core/Link';
import TextField from '@material-ui/core/TextField';
import MinistryAssignToDropdown from '../MinistryAssignToDropdown';
import { useDispatch, useSelector } from "react-redux";
import { fetchFOIFullAssignedToList } from "../../../../apiManager/services/FOI/foiMasterDataServices";
import { Watcher } from '../../customComponents';
import { useParams } from 'react-router-dom';
import { getHeaderText } from './utils';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { isRequestWatcherOrMinistryAssignee, addToRestrictedRequestTagList } from "../../../../helper/FOI/helper";
import RequestMinistryRestriction from "../../customComponents/RequestMinistryRestriction";
import _ from 'lodash';
import {setCommentTagListLoader} from "../../../../actions/FOI/foiRequestActions";
import RequestFlag from '../../customComponents/RequestFlag';

const RequestHeader = React.memo(({
    requestDetails,
    userDetail,
    handleMinistryAssignedToValue,
    setSaveMinistryRequestObject,
    ministryAssigneeValue,
    isMinistry,
}) => {
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
      else{
        dispatch(setCommentTagListLoader(false));
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

    const isMinistryRestrictedFileManager = () => {
        return userDetail?.role?.includes("MinistryRestrictedFilesManager");
    }
    const isRestricted = () => {
        return requestDetails?.ministryrestricteddetails?.isrestricted;
    }
    const [isMinistryRestrictedRequest, setIsMinistryRestrictedRequest] = useState( isRestricted() );
    const [disableHeaderInput, setDisableHeaderInput] = useState( isRestricted() && !isMinistryRestrictedFileManager() );
    const [isLoaded, setIsLoaded] = useState(false);
    const requestWatchers = useSelector((state) => state.foiRequests.foiWatcherList);

    const watcherBox = (
        requestState?.toLowerCase() == StateEnum.closed.name.toLowerCase() ?
        (<></>)
        :
        (
            <Watcher
                watcherFullList={ministryAssignedToList}
                ministryId={ministryId}
                userDetail={userDetail}
                disableInput={disableHeaderInput}
                isIAORestrictedRequest={false}
                setIsLoaded={setIsLoaded}
                isMinistryRestrictedRequest={isMinistryRestrictedRequest}
                assigneeDetails={_.pick(requestDetails, ['assignedministrygroup','assignedministryperson','assignedministrypersonFirstName','assignedministrypersonLastName'])}
                requestWatchers={requestWatchers}
            />
        )
      );

      const requestFlagsBox = (
        <div>
            <RequestFlag
              type="oipcreview"
              requestDetails={requestDetails}
              isActive={requestDetails.isoipcreview}
              isDisabled={isMinistry}
            />
            <RequestFlag
              type="consult"
              requestDetails={requestDetails}
              isActive={requestDetails.isconsultflag}
              showFlag={requestDetails.isconsultflag === true}
              isDisabled={true}
            />
            <RequestFlag
              type="phasedrelease"
              requestDetails={requestDetails}
              isActive={requestDetails.isphasedrelease}
              isDisabled={true}
            />
        </div>
      );
    return (
        <>
        <div className="row">
            <div className="col-lg-6">
                <div className="foi-request-review-header-col1-row axis-request-id">
                    <Link href="#" onClick={preventDefault}>
                        <h1 className="foi-review-request-text foi-ministry-requestheadertext">{headerText}</h1>
                    </Link>
                </div>
            </div>
            <div className="col-lg-6">
                <div className="foi-assignee-dropdown">
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
            </div>
        </div>
        <div className="row">
            <div className="col-lg-6">
                <Grid container columns={16}>
                    <Grid>
                        {watcherBox}
                        {
                            (isLoaded && (isRequestWatcherOrMinistryAssignee(requestWatchers,ministryAssigneeValue,userDetail?.preferred_username) || 
                                isMinistryRestrictedFileManager())) &&
                            <RequestMinistryRestriction 
                                isministryrestricted={isRestricted()}
                                isMinistryRestrictedFileManager={isMinistryRestrictedFileManager()}
                                requestDetails={requestDetails}
                            />
                        }
                    </Grid>
                    <Grid>
                        <div className="foi-request-review-header-col1-row">
                            {requestFlagsBox}
                        </div>
                    </Grid>
                </Grid>
            </div>
            <div className="col-lg-6">
                <div className="foi-assignee-dropdown">
                    <MinistryAssignToDropdown requestState={requestState} requestDetails={_requestDetails} 
                    ministryAssignedToList={ministryAssignedToList} 
                    handleMinistryAssignedToValue={handleMinistryAssignedToValue} 
                    isMinistryCoordinator={true} requestId={requestId} ministryId={ministryId} 
                    setSaveMinistryRequestObject={setSaveMinistryRequestObject}
                    disableInput={disableHeaderInput} 
                    isRestricted= {isRestricted()} 
                    requestWatchers={requestWatchers}/>
                </div>
            </div>
        </div>
        </>
    );
})

export default RequestHeader