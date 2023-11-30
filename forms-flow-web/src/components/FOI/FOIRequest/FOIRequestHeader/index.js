import React, { useEffect, useState } from 'react';
import Link from '@material-ui/core/Link';
import { useSelector, useDispatch } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./foirequestheader.scss";
import TextField from '@material-ui/core/TextField';
import { getMenuItems, getAssignedTo, getStatus, getFullName} from "./utils";
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { calculateDaysRemaining, isRequestWatcherOrAssignee } from "../../../../helper/FOI/helper";
import { Watcher } from '../../customComponents';
import { createAssigneeDetails } from '../utils'
import {
  saveAssignee
} from "../../../../apiManager/services/FOI/foiAssigneeServices";
import {
  fetchRestrictedRequestCommentTagList
} from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from "react-toastify";
import _ from 'lodash';
import RequestRestriction from "../../customComponents/RequestRestriction";
import ConfirmModal from "../../customComponents/ConfirmModal";
import RequestFlag from '../../customComponents/RequestFlag';

const useStyles = makeStyles((theme) => ({
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    item: {
        paddingLeft: theme.spacing(3),
    },
    group: {
        fontWeight: theme.typography.fontWeightBold,
        opacity: 1,
    },
  }));
const FOIRequestHeader = React.memo(
  ({
    headerValue,
    headerText,
    requestDetails,
    handleAssignedToInitialValue,
    handleAssignedToValue,
    createSaveRequestObject,
    handlestatusudpate,
    userDetail,
    disableInput,
    isAddRequest,
    handleOipcReviewFlagChange,
    showOipcReviewFlag
  }) => {
    /**
     *  Header of Review request in the UI
     *  AssignedTo - Mandatory field
     */
    const classes = useStyles();
    const dispatch = useDispatch();
    const { requestId, ministryId } = useParams();
    //get the assignedTo master data
    const assignedToList = useSelector(
      (state) => state.foiRequests.foiAssignedToList
    );
    const [isIAORestrictedRequest,setIsIAORestrictedRequest] = useState(false);
    let assigneeDetails = _.pick(requestDetails, ['assignedGroup', 'assignedTo','assignedToFirstName','assignedToLastName',
    'assignedministrygroup','assignedministryperson','assignedministrypersonFirstName','assignedministrypersonLastName']);
    const [assigneeObj, setAssigneeObj] = useState(assigneeDetails);

    const isIAORestrictedFileManager = () => {
      return userDetail?.role?.includes("IAORestrictedFilesManager");
    }

    const isRestricted = () => {
      if(ministryId){
        return requestDetails?.iaorestricteddetails?.isrestricted;
      } 
      else
        return requestDetails?.isiaorestricted;
    }

    const [disableHeaderInput, setDisableHeaderInput] = useState(disableInput || (isRestricted() && !isIAORestrictedFileManager()));
    //handle default value for the validation of required fields
    React.useEffect(() => {
      let _daysRemaining = calculateDaysRemaining(requestDetails.dueDate);
      let _status = getStatus({ headerValue, requestDetails });
      const _cfrDaysRemaining = requestDetails.cfrDueDate
        ? calculateDaysRemaining(requestDetails.cfrDueDate)
        : "";
      handlestatusudpate(_daysRemaining, _status, _cfrDaysRemaining);
      setIsIAORestrictedRequest(isRestricted());
      setDisableHeaderInput(disableInput || (isRestricted() && !isIAORestrictedFileManager()));
    }, [requestDetails, handleAssignedToInitialValue, handlestatusudpate]);
    useEffect(() => {
      setAssignedTo(getAssignedTo(assigneeObj));
    }, [assigneeObj]);
  
    const [menuItems, setMenuItems] = useState([]);
 
    const [selectedAssignedTo, setAssignedTo] = React.useState(() => getAssignedTo(assigneeDetails));

    const preventDefault = (event) => event.preventDefault();

    const requestWatchers = useSelector((state) => state.foiRequests.foiWatcherList);
    const [showModal, setShowModal] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);
    const [assigneeVal, setAssigneeVal]= useState("");
    const [assigneeName,setAssigneeName] = useState("");
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
      // handle case where assigned user was removed from group
      if (assignedToList && assignedToList.length > 0) {
        let assignedTeam = assignedToList.find(team => team.name === requestDetails.assignedGroup);
        if (assignedTeam && requestDetails.assignedTo && !assignedTeam.members.find(member => member.username === requestDetails.assignedTo)) {
          setAssignedTo("|Unassigned");
          handleAssignedToValue("|Unassigned");
        }
      }
    }, [assignedToList]);

    useEffect(() => {
      setMenuItems(
        getMenuItems({ classes, assignedToList, selectedAssignedTo, isIAORestrictedRequest })
      );
    }, [selectedAssignedTo, assignedToList]);

    const handleAssigneeUpdate = (event) => {
      let AssigneeValue = event?.target?.value;
      let [groupName, username, firstName, lastName] = AssigneeValue.split('|');
      let fullName = firstName !== "" ? `${lastName}, ${firstName}` : username;
      setAssigneeVal(AssigneeValue);
      setAssigneeName(fullName);

      if(isIAORestrictedRequest){
        setModalMessage(<span>Are you sure you want to assign <b>{fullName}</b> to this request?</span>);
        setModalDescription(<span><i>This will allow them to have access to this restricted request content.</i></span>);
        setShowModal(true);
      }
      else
        saveAssigneeDetails(AssigneeValue, fullName);
    }
    
    const resetModal = () => {
      setShowModal(false);
    }

    const saveAssigneeDetails = (assigneeVal, assigneeName) => {
      setAssignedTo(assigneeVal);
      if (isAddRequest) {
        //event bubble up - to validate required fields
        handleAssignedToValue(assigneeVal);
        createSaveRequestObject(
          FOI_COMPONENT_CONSTANTS.ASSIGNED_TO,
          assigneeVal,
          assigneeName
        );
      } else {
        setAssigneeObj(createAssigneeDetails(assigneeVal, assigneeName));  
        assigneeDetails = createAssigneeDetails(assigneeVal, assigneeName);
        dispatch(
          saveAssignee(assigneeDetails, requestId, ministryId, false, (err, _res) => {
            if(!err) {
              toast.success("Assignee has been saved successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
              createSaveRequestObject(
                FOI_COMPONENT_CONSTANTS.ASSIGNED_TO,
                assigneeVal,
                assigneeName
              );
              //event bubble up - to validate required fields
              handleAssignedToValue(assigneeVal);
              requestDetails.assignedGroup = assigneeDetails.assignedGroup;
              requestDetails.assignedTo = assigneeDetails.assignedTo;
              requestDetails.assignedToFirstName = assigneeDetails.assignedToFirstName;
              requestDetails.assignedToLastName = assigneeDetails.assignedToLastName;
              requestDetails.assignedToName = assigneeDetails.assignedToName
              if(isRestricted())
                dispatch(fetchRestrictedRequestCommentTagList(requestId, ministryId));
            } else {
              toast.error(
                "Temporarily unable to save the assignee. Please try again in a few minutes.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
            }
          })
        )
      }
      
    }

    const status = getStatus({ headerValue, requestDetails });

    const showMinistryAssignedTo =
      status.toLowerCase() === StateEnum.callforrecords.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.closed.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.deduplication.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.harms.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.review.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.feeassessed.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.consult.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.signoff.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.onhold.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.response.name.toLowerCase() ||
      (ministryId && status.toLowerCase() === StateEnum.peerreview.name.toLowerCase());

    const getMinistryAssignedTo = () => {
      if (assigneeDetails?.assignedministryperson)
        return getFullName(assigneeDetails?.assignedministrypersonLastName, assigneeDetails?.assignedministrypersonFirstName, assigneeDetails?.assignedministryperson);
      return assigneeDetails.assignedministrygroup;
    }
    const ministryAssignedTo = getMinistryAssignedTo();
    const watcherList = assignedToList.filter(assignedTo => assignedTo.type === 'iao');

    return (
      <>
      <div className='row'>
        <div className="col-lg-6">
          <div className='axis-request-id'>
              <Link href="#" onClick={preventDefault}>
                <h3 className="foi-review-request-text">{headerText}</h3>
              </Link>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="foi-assignee-dropdown">
              <TextField
                id="assignedTo"
                label={showMinistryAssignedTo ? "IAO Assigned To" : "Assigned To"}
                inputProps={{ "aria-labelledby": "assignedTo-label"}}
                InputLabelProps={{ shrink: true }}
                select
                value={selectedAssignedTo}
                onChange={handleAssigneeUpdate}
                input={<Input />}
                variant="outlined"
                fullWidth
                required
                disabled={disableHeaderInput}
                error={selectedAssignedTo.toLowerCase().includes("unassigned")}
              >
                {menuItems}
              </TextField>
            </div>
        </div>
      </div>
      <div className='row'>
        <div className="col-lg-3">
          {window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) ===
              -1 && (
                <Watcher
                  watcherFullList={watcherList}
                  requestId={requestId}
                  ministryId={ministryId}
                  userDetail={userDetail}
                  disableInput={disableHeaderInput}
                  isIAORestrictedRequest={isIAORestrictedRequest}
                  setIsLoaded={setIsLoaded}
                />
            )}
          {!isAddRequest && status.toLowerCase() !== StateEnum.unopened.name.toLowerCase() && (isIAORestrictedFileManager() ||
            (isLoaded && isRequestWatcherOrAssignee(requestWatchers,assigneeObj,userDetail?.preferred_username))) && 
          <RequestRestriction 
            isiaorestricted= {isRestricted()}
            isIAORestrictedFileManager={isIAORestrictedFileManager()}
            requestDetails={requestDetails}
            />
          }
        </div>
        <div className="col-lg-3">
          <RequestFlag
            type="oipcreview"
            requestDetails={requestDetails}
            isActive={requestDetails.isoipcreview}
            handleSelect={handleOipcReviewFlagChange}
            showFlag={showOipcReviewFlag}
          />
          {/* <RequestFlag
            type="phasedrelease"
            requestDetails={requestDetails}
            isActive={requestDetails.isphasedrelease}
            handleSelect={handleOipcReviewFlagChange}
          /> */}
        </div>
        <div className="col-lg-6">
          <div className="foi-assignee-dropdown">
            {showMinistryAssignedTo && (
                  <>
                  <TextField
                      id="ministryAssignedTotxt"
                      label="Ministry Assigned To"
                      InputLabelProps={{ shrink: true }}
                      value={ministryAssignedTo}
                      variant="outlined"
                      fullWidth
                      disabled={true}
                    />
                  </>
                )}
          </div>
        </div>
      </div>

      <ConfirmModal 
          modalMessage= {modalMessage}
          modalDescription= {modalDescription} 
          showModal={showModal}
          saveAssigneeDetails = {saveAssigneeDetails}
          assigneeVal={assigneeVal}
          assigneeName ={assigneeName}
          resetModal = {resetModal} />
      </>
    );
    
  }
);

export default FOIRequestHeader;