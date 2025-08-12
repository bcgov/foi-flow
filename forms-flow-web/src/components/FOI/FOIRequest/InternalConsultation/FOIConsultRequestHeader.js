import React, { useEffect, useState } from 'react';
import Link from '@material-ui/core/Link';
import { useSelector, useDispatch } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import "./foiconsultrequestheader.scss";
import TextField from '@material-ui/core/TextField';
import { getMenuItems, getAssignedTo, getConsultMenuItems, getConsultAssignedTo, getStatus, getFullName} from "../FOIRequestHeader/utils";
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../../constants/FOI/foiComponentConstants';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { calculateDaysRemaining, isRequestWatcherOrAssignee } from "../../../../helper/FOI/helper";
import { Watcher } from '../../customComponents';
import { createAssigneeDetails } from '../utils'
import {
  saveAssignee, 
  saveConsultAssignee,
} from "../../../../apiManager/services/FOI/foiAssigneeServices";
import {
  fetchRestrictedRequestCommentTagList,  
  updateSpecificRequestSection,
} from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from "react-toastify";
import _ from 'lodash';
import clsx from 'clsx';
import RequestRestriction from "../../customComponents/RequestRestriction";
import ConfirmModal from "../../customComponents/ConfirmModal";
import RequestFlag from '../../customComponents/RequestFlag';
import { Grid } from '@material-ui/core';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import { ConsultTypes } from '../../../../helper/consult-helper';
import { Chip } from '@mui/material';
import InputAdornment from "@material-ui/core/InputAdornment";
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

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
    blankrow: {
      padding: 25
    },
    showConsultAssigneeFieldValidation: {
      color: "#CE3E39",
      fontStyle: 'italic',
      fontSize: '13px !important', 
    },
    hideConsultAssigneeFieldValidation: { 
      visibility: 'hidden'
    },
    showIcon: {
      color: "#CE3E39 !important",
      backgroundColor: "#fff !important",
      position: 'absolute !important',
      right: 45,
      pointerEvents: 'none !important',
    },
    hideIcon: {
      visibility: 'hidden !important',
    },
    warningAmberIcon : {
      color: "#CE3E39 !important",
      width: "20px !important",
      transform: "translateY(-1%) !important",
      fontSize: "medium !important",
      marginRight: "-45px !important",
    }
  }));
const FOIConsultRequestHeader = React.memo(
  ({
    headerValue,
    headerText,
    requestDetails,
    handleAssignedToInitialValue,
    handleAssignedToValue,
    createSaveRequestObject,
    createSaveConsultRequestObject,
    handlestatusudpate,
    userDetail,
    disableInput,
    isAddRequest,
    isAddConsultRequest,
    handleOipcReviewFlagChange,
    showFlags,
    isMinistry,
    isHistoricalRequest,
    showConsultFlag,
    handleConsultFlagChange,
    handleConsultTypeFlagChange,
    requestConsults
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
    const [consultAssigneeObj, setConsultAssigneeObj] = useState(assigneeDetails);
    const [isConsultAssignedToValid, setIsConsultAssignedToValid] = React.useState(false);
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
      setConsultAssignedTo(getConsultAssignedTo(consultAssigneeObj));
    }, [consultAssigneeObj]);
  
    const [menuItems, setMenuItems] = useState([]);
 
    // const [selectedConsultAssignedTo, setConsultAssignedTo] = React.useState(() => getConsultAssignedTo(assigneeDetails));
    const [selectedConsultAssignedTo, setConsultAssignedTo] = useState("Unassigned");
    const preventDefault = (event) => event.preventDefault();

    const requestWatchers = useSelector((state) => state.foiRequests.foiWatcherList);
    const [showModal, setShowModal] = useState(false);
    const [modalMessage, setModalMessage] = useState(<></>);    
    const [modalDescription, setModalDescription] = useState(<></>);
    const [consultAssigneeVal, setConsultAssigneeVal]= useState("");
    const [consultAssigneeName,setConsultAssigneeName] = useState("");
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
      // handle case where assigned user was removed from group
      if (assignedToList && assignedToList.length > 0) {
        if (requestConsults) {
          let assignedTeam = assignedToList.find(team => team.name === requestConsults.assignedGroup);
          if (assignedTeam && requestConsults.consultAssignedTo && !assignedTeam.members.find(member => member.username === requestConsults.consultAssignedTo)) {
              setConsultAssignedTo("|Unassigned");
              handleAssignedToValue("|Unassigned");
          }
      } else {
          setConsultAssignedTo("Unassigned");
          handleAssignedToValue("Unassigned");
      }
      }
    }, [assignedToList]);

    // useEffect(() => {
    //   setMenuItems(
    //     getMenuItems({ classes, assignedToList, selectedConsultAssignedTo, isIAORestrictedRequest })
    //   );
    // }, [selectedConsultAssignedTo, assignedToList]);

    useEffect(() => {
      setMenuItems(
        getConsultMenuItems({ classes, assignedToList, selectedConsultAssignedTo, isIAORestrictedRequest })
      );
    }, [selectedConsultAssignedTo, assignedToList]);

    const handleConsultAssigneeUpdate = (event) => {
      let assigneeValue = event?.target?.value;
      let [groupName, username, firstName, lastName] = assigneeValue.split('|');
      let fullName = firstName !== "" ? `${lastName}, ${firstName}` : username;
      setConsultAssigneeVal(assigneeValue);
      setConsultAssigneeName(fullName);
      saveConsultAssigneeDetails(assigneeValue, fullName);
      setIsConsultAssignedToValid(assigneeValue !== null);
    }
    
    const resetModal = () => {
      setShowModal(false);
    }

    const saveConsultAssigneeDetails = (consultAssigneeVal, consultAssigneeName) => {
      setConsultAssignedTo(consultAssigneeVal);
      if (isAddConsultRequest) {
        //event bubble up - to validate required fields
        handleAssignedToValue(consultAssigneeVal);
        createSaveConsultRequestObject(
          FOI_COMPONENT_CONSTANTS.CONSULT_ASSIGNED_TO,
          consultAssigneeVal,
          consultAssigneeName
        );
        toast.success("Assignee was saved successfully.", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
      } else {
        setConsultAssigneeObj(createAssigneeDetails(consultAssigneeVal, consultAssigneeName));  
        assigneeDetails = createAssigneeDetails(consultAssigneeVal, consultAssigneeName);
        dispatch(
          saveConsultAssignee(assigneeDetails, ministryId, requestConsults.id, false, (err, _res) => {
            if(!err) {
              toast.success("Assignee was saved successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
              createSaveConsultRequestObject(
                FOI_COMPONENT_CONSTANTS.CONSULT_ASSIGNED_TO,
                consultAssigneeVal,
                consultAssigneeName
              );
              //event bubble up - to validate required fields
              handleAssignedToValue(consultAssigneeVal);
              requestDetails.assignedGroup = assigneeDetails.assignedGroup;
              requestDetails.assignedTo = assigneeDetails.assignedTo;
              requestDetails.assignedToFirstName = assigneeDetails.assignedToFirstName;
              requestDetails.assignedToLastName = assigneeDetails.assignedToLastName;
              requestDetails.assignedToName = assigneeDetails.assignedToName
              // if(isRestricted())
              //   dispatch(fetchRestrictedRequestCommentTagList(requestId, ministryId));
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
      status.toLowerCase() === StateEnum.recordsreadyforreview.name.toLowerCase() ||
      status.toLowerCase() === StateEnum.onholdother.name.toLowerCase() ||
      (ministryId && status.toLowerCase() === StateEnum.peerreview.name.toLowerCase());

    const getMinistryAssignedTo = () => {
      if (assigneeDetails?.assignedministryperson)
        return getFullName(assigneeDetails?.assignedministrypersonLastName, assigneeDetails?.assignedministrypersonFirstName, assigneeDetails?.assignedministryperson);
      return assigneeDetails.assignedministrygroup;
    }
    const ministryAssignedTo = getMinistryAssignedTo();
    const watcherList = assignedToList.filter(assignedTo => assignedTo.type === 'iao');

    const updateIsPhasedRelease = (isPhasedRelease) => {
      const toastID = toast.loading("Updating phased release status for request...");
      dispatch(
        updateSpecificRequestSection(
          {'isphasedrelease': isPhasedRelease},
          'isphasedrelease',
          requestId,
          ministryId, 
          (err, _res) => {
          if(!err) {
            createSaveRequestObject('isphasedrelease', isPhasedRelease)
            toast.update(toastID, {
              type: "success",
              render: "Request details have been saved successfully.",
              position: "top-right",
              isLoading: false,
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
          } else {
            toast.error(
              "Temporarily unable to update phased release status for request. Please try again in a few minutes.",
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

    const consultTypeMapping = {
      [ConsultTypes.Internal]: true,
      [ConsultTypes.External]: false,
    };
  
    const isRequestConsultFlagActive = requestConsults ? consultTypeMapping[requestConsults.consultTypeId] || null : null;

    return (
      <>
      {/* {isAddConsultRequest? ( */}
        <div className='row'>
        <div className="col-lg-12">
                <Alert className="consultation-alert" icon={false} severity="info">
                <div className="header-content">
                      <svg className="header-icon" xmlns="http://www.w3.org/2000/svg" width="33" height="39" viewBox="0 0 33 39" fill="none">
                      <path d="M2.82129 1.31226C3.58928 1.31226 4.24023 1.95019 4.24023 2.78003V5.12769L5.36719 4.8396L10.3721 3.55835L10.3711 3.55737C12.7629 2.94861 15.2839 3.17595 17.5264 4.198L17.9707 4.41284C21.5877 6.263 25.8479 6.263 29.4648 4.41284L29.4639 4.41187L30.1602 4.05737C31.0253 3.6158 32.0977 4.24411 32.0977 5.30542V23.6414C32.0976 24.2278 31.7645 24.7402 31.2686 24.9763L31.1689 25.0193L28.6514 25.9822L28.6494 25.9832C25.6356 27.1418 22.2998 27.0041 19.3857 25.6121L19.1045 25.4734H19.1035C16.3438 24.0685 13.2 23.6449 10.1846 24.2712L9.58398 24.4109L4.91895 25.6033L4.24023 25.7761V35.9568C4.24023 36.7866 3.58928 37.4236 2.82129 37.4236C2.05336 37.4235 1.40234 36.7866 1.40234 35.9568V2.78003L1.41016 2.62671C1.48434 1.87287 2.10128 1.31233 2.82129 1.31226Z" stroke="#9448BC" stroke-width="1.80556"/>
                      </svg>
                    <AlertTitle><h3 className="consultation-alert-header-text">{headerText}</h3></AlertTitle>
                    <div className="request-flag-container">
                    <RequestFlag
                    type="consulttype"
                    requestDetails={requestDetails}
                    isActive={isRequestConsultFlagActive}
                    handleSelect={handleConsultTypeFlagChange}
                    showFlag={true}
                    isDisabled={!isAddConsultRequest}
                    />
                </div>
                  </div>
                  <div className='header-text'>
                  <span className="consultation-alert-text"> You are creating a new consultation. Enter your original ID number to synchronize data and select consultation type.</span>
                  </div>   
                </Alert>
        </div>
      </div>
      
    {/* ): (
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
            {!isHistoricalRequest ? 
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
            :
              <TextField
                id="assignedTo"
                label={showMinistryAssignedTo ? "IAO Assigned To" : "Assigned To"}
                inputProps={{ "aria-labelledby": "assignedTo-label"}}
                InputLabelProps={{ shrink: true }}
                value={requestDetails.assignedTo}
                input={<Input />}
                variant="outlined"
                fullWidth
                disabled
              >
                {menuItems}
              </TextField>
            }
          </div>
      </div>
    </div>
      )
      }
       */}
      
      <div className='row'>
        <div className="col-lg-6">
          <Grid container columns={16}>
            <Grid>
              <div>
                {(window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDCONSULTREQUEST) > -1) && (handleConsultTypeFlagChange === true) && (
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
                  (isLoaded && isRequestWatcherOrAssignee(requestWatchers,consultAssigneeObj,userDetail?.preferred_username))) && 
                <RequestRestriction 
                  isiaorestricted= {isRestricted()}
                  isIAORestrictedFileManager={isIAORestrictedFileManager()}
                  requestDetails={requestDetails}
                  />

                }
              </div>
            </Grid>
            <Grid>
              <div>
                <RequestFlag
                    type="oipcreview"
                    requestDetails={requestDetails}
                    isActive={requestDetails.isoipcreview}
                    handleSelect={handleOipcReviewFlagChange}
                    showFlag={showFlags}
                    isDisabled={isMinistry}
                />
                <RequestFlag
                    type="consult"
                    requestDetails={requestDetails}
                    isActive={requestDetails.isconsultflag}
                    handleSelect={handleConsultFlagChange}
                    showFlag={showConsultFlag}
                    isDisabled={!isAddRequest}
                />
                <RequestFlag
                  type="phasedrelease"
                  requestDetails={requestDetails}
                  isActive={requestDetails.isphasedrelease}
                  showFlag={showFlags}
                  handleSelect={updateIsPhasedRelease}
                />
              </div>
            </Grid>
          </Grid>
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
                 <TextField
                 id="consultAssignedTo"
                 label={"IAO Assigned To"}
                 inputProps={{ "aria-labelledby": "assignedTo-label"}}
                 InputLabelProps={{ shrink: true }}
                 select
                 value={selectedConsultAssignedTo}
                 onChange={handleConsultAssigneeUpdate}
                 input={<Input />}
                 InputProps={{
                  endAdornment: (
                      <InputAdornment position="end">
                          <Chip
                        icon={
                            <WarningAmberIcon
                            className={clsx(classes.warningAmberIcon)} 
                            />
                        }
                        className={clsx({
                            [classes.showIcon]: !isConsultAssignedToValid,
                            [classes.hideIcon]: isConsultAssignedToValid,
                        })}
                    />
                      </InputAdornment>
                  )
                }}
                 variant="outlined"
                 fullWidth
                 required
                 disabled={disableHeaderInput}
                 error={selectedConsultAssignedTo.toLowerCase().includes("unassigned")}
               >
                 {menuItems}
               </TextField>
               <h5
                  className={clsx({
                    [classes.showConsultAssigneeFieldValidation]: !isConsultAssignedToValid,
                    [classes.hideConsultAssigneeFieldValidation]: isConsultAssignedToValid,
                  })}
               >This field is required</h5>
          </div>
        </div>
      </div>

      <ConfirmModal 
          modalMessage= {modalMessage}
          modalDescription= {modalDescription} 
          showModal={showModal}
          saveAssigneeDetails = {saveConsultAssigneeDetails}
          assigneeVal={consultAssigneeVal}
          assigneeName ={consultAssigneeName}
          resetModal = {resetModal} />
      </>
    );
    
  }
);

export default FOIConsultRequestHeader;