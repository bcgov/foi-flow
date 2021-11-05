import React, { useState } from 'react';
import './bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import {saveRequestDetails, openRequestDetails} from "../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import { ConfirmationModal } from '../customComponents';
import { addBusinessDays, formatDate, calculateDaysRemaining } from "../../../helper/FOI/helper";
import { StateEnum } from '../../../constants/FOI/statusEnum';

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%',
      marginTop:'30px',
      marginBottom:'50px'
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
    btndisabled: {
      border: 'none',
      backgroundColor: '#eceaea',
      color: '#FFFFFF'
    },
    btnenabled: {
      border: 'none',
      backgroundColor: '#38598A',
      color: '#FFFFFF'
    },
    btnsecondaryenabled: {
      border: '1px solid #38598A',
      backgroundColor: '#FFFFFF',
      color: '#38598A'
    }
  }));

const BottomButtonGroup = React.memo(({
  isValidationError, 
  urlIndexCreateRequest, 
  saveRequestObject, 
  unSavedRequest,
  handleSaveRequest,
  handleOpenRequest,
  currentSelectedStatus,
  hasStatusRequestSaved,
  disableInput
  }) => {
  /**
   * Bottom Button Group of Review request Page
   * Button enable/disable is handled here based on the validation
   */
    const {requestId, ministryId, requestState} = useParams();  

    const classes = useStyles();
    const dispatch = useDispatch();
    
    const [openModal, setOpenModal] = useState(false);
    const [opensaveModal, setsaveModal] = useState(false);

    const [closingDate, setClosingDate] = useState( formatDate(new Date()) );
    const [closingReasonId, setClosingReasonId] = useState();

    const handleClosingDateChange = (cDate) => {
      setClosingDate(cDate);
    }

    const handleClosingReasonChange = (cReasonId) => {
      setClosingReasonId(cReasonId);
    }

    const returnToQueue = (e) => {
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        e.preventDefault();
        window.removeEventListener('beforeunload', alertUser);
        window.location.href = '/foi/dashboard';
      }
    }
    const dueDateCalculation = (dateText, noOfBusinessDays) => {
      return dateText? addBusinessDays(dateText, noOfBusinessDays) : "";
    }
    const saveRequest = async () => {
      dispatch(saveRequestDetails(saveRequestObject, urlIndexCreateRequest, requestId, ministryId, (err, res) => {
        if (!err) {
          toast.success('The request has been saved successfully.', {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            });
            const _state = currentSelectedStatus ? currentSelectedStatus : ((requestState && requestState === StateEnum.unopened.name && saveRequestObject.sourceOfSubmission === 'onlineform') || urlIndexCreateRequest > -1 ? StateEnum.intakeinprogress.name : requestState);
            handleSaveRequest(_state, false, res.id);
        } else {
          toast.error('Temporarily unable to save your request. Please try again in a few minutes.', {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            });
            handleSaveRequest(currentSelectedStatus, true, "");
        }
      }));      
    }

    const alertUser = e => {
      if (unSavedRequest) {
        e.preventDefault();
        e.returnValue = '';
      }
    }

    const handleOnHashChange = (e) => {       
      returnToQueue(e);
    };  

    React.useEffect(() => {
           
      if(currentSelectedStatus == StateEnum.open.name && !isValidationError && (ministryId == undefined || ministryId == null || ministryId == ''))
      {
        saveRequestObject.requeststatusid = StateEnum.open.id;
        openRequest();
        hasStatusRequestSaved(true, StateEnum.open.name)
      }
      else if(currentSelectedStatus == StateEnum.open.name && !isValidationError && (ministryId != undefined || ministryId != null || ministryId != ''))
      {
        console.log("Entered Open!")
        saveRequestObject.requeststatusid = StateEnum.open.id;        
        saveRequestModal();
      }
      else if (currentSelectedStatus !== "" && currentSelectedStatus.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase() && !isValidationError){
        saveRequestModal();
      }
      
      
      

      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener('popstate', handleOnHashChange);
      window.addEventListener('beforeunload', alertUser);
      //window.addEventListener('unload', handleOnHashChange);   
      
      return () => {
        window.removeEventListener('popstate', handleOnHashChange);
        window.removeEventListener('beforeunload', alertUser);
        //window.removeEventListener('unload', handleOnHashChange);
        
      }
    });
    
   
    const openRequest = () => {
      saveRequestObject.id = saveRequestObject.id ? saveRequestObject.id :requestId; 
      saveRequestObject.requeststatusid = 1
      setOpenModal(true);     
    }

    const saveRequestModal =()=>{
      setsaveModal(true);
    }

    const handleModal = (value, fileInfoList) => {
      if (value) {
        dispatch(openRequestDetails(saveRequestObject, (err, res) => {
          if(!err) {
            toast.success('The request has been opened successfully.', {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
              });
            const parentRequestId = res.id;           
            res.ministryRequests.sort(function(a, b) {
              var keyA = a.filenumber,
                  keyB = b.filenumber;             
              if (keyA < keyB) return -1;
              if (keyA > keyB) return 1;
              return 0;
            });
            const firstMinistry = res.ministryRequests[0];
            handleOpenRequest(parentRequestId, firstMinistry.id, false);
          }
          else {
            toast.error('Temporarily unable to open your request. Please try again in a few minutes.', {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
              });
            handleOpenRequest("","",true);
          }
        })); 
      }
      setOpenModal(false);
    }

    const handleSaveModal = (value, fileInfoList) => {      
      setsaveModal(false);      
      if (value) {
        if(currentSelectedStatus == StateEnum.closed.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.closed.id;
          saveRequestObject.closedate = closingDate;
          saveRequestObject.closereasonid = closingReasonId;
          saveRequest();
          hasStatusRequestSaved(true, currentSelectedStatus)
        }
        else if(currentSelectedStatus === StateEnum.callforrecords.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.callforrecords.id;
          if (!('cfrDueDate' in saveRequestObject) || saveRequestObject.cfrDueDate === '') {
            const calculatedCFRDueDate = dueDateCalculation(new Date(), 10);
            saveRequestObject.cfrDueDate = calculatedCFRDueDate;
          }
          else if (saveRequestObject.onholdTransitionDate) {
            const onHoldDays = calculateDaysRemaining(new Date(), saveRequestObject.onholdTransitionDate);            
            const calculatedCFRDueDate = addBusinessDays(saveRequestObject.cfrDueDate, onHoldDays);
            const calculatedRequestDueDate = addBusinessDays(saveRequestObject.dueDate, onHoldDays);            
            saveRequestObject.cfrDueDate = calculatedCFRDueDate;
            saveRequestObject.dueDate = calculatedRequestDueDate;
          }
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }  
        else if(currentSelectedStatus == StateEnum.redirect.name && !isValidationError)
        {        
          saveRequestObject.requeststatusid = StateEnum.redirect.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.open.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.open.id; // Need to take from ENUM, -1 if not yet opened - RAW REQUEST
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.intakeinprogress.name && !isValidationError)
        {
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.review.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.review.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.onhold.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.onhold.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.signoff.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.signoff.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.feeassessed.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.feeassessed.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.consult.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.consult.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.deduplication.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.deduplication.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.harms.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.harms.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.response.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.response.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
      }
    }

  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={openModal} handleModal={handleModal} state={StateEnum.open.name} saveRequestObject={saveRequestObject} />  
      <ConfirmationModal openModal={opensaveModal} handleModal={handleSaveModal} state={currentSelectedStatus} saveRequestObject={saveRequestObject} handleClosingDateChange={handleClosingDateChange} handleClosingReasonChange={handleClosingReasonChange} />
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError || disableInput} onClick={saveRequest}>Save</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;