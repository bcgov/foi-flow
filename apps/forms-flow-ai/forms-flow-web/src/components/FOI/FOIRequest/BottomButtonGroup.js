import React, { useState } from 'react';
import './bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import {saveRequestDetails, openRequestDetails} from "../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import { ConfirmationModal } from '../customComponents';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

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
  hasStatusRequestSaved
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

    const returnToQueue = (e) => {
      e.preventDefault();
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        window.location.href = '/foi/dashboard';
      }
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
            const _state = currentSelectedStatus ? currentSelectedStatus : (requestState ? requestState : (urlIndexCreateRequest > -1 ? "Intake in Progress" : ""));
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
            handleSaveRequest(currentSelectedStatus, true, res.id);
        }
      }));      
    }

    const alertUser = e => {
      e.preventDefault();
      if (unSavedRequest) {
        e.returnValue = '';
      }
    }

    React.useEffect(() => {
      const handleOnHashChange = (e) => {       
        returnToQueue(e);
      };  
            
      if(currentSelectedStatus == "Open" && !isValidationError)
      {
        saveRequestObject.requeststatusid = 1 // Need to take from ENUM
        openRequest();
        hasStatusRequestSaved(true,"Open")
      }
      else if (currentSelectedStatus !== "" && currentSelectedStatus.toLowerCase() !== FOI_COMPONENT_CONSTANTS.INTAKEINPROGRESS.toLowerCase() && !isValidationError){
        saveRequestModal();
      }
      
      
      

      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener('popstate', handleOnHashChange);
      window.addEventListener('beforeunload', alertUser);
      window.addEventListener('unload', handleOnHashChange);   
      
      return () => {
        window.removeEventListener('popstate', handleOnHashChange);
        window.removeEventListener('beforeunload', alertUser);
        window.removeEventListener('unload', handleOnHashChange);
        
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

    const handleModal = (value) => {
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

    const handleSaveModal = (value) => {      
      setsaveModal(false);
      if (value) {
        if(currentSelectedStatus == "Closed" && !isValidationError)
        {
          saveRequestObject.requeststatusid = 3 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == "Call For Records" && !isValidationError)
        {        
          saveRequestObject.requeststatusid = 2 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }  
        else if(currentSelectedStatus == "Redirect" && !isValidationError)
        {        
          saveRequestObject.requeststatusid = 4 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == "Open" && !isValidationError)
        {
          saveRequestObject.requeststatusid = 1 // Need to take from ENUM, -1 if not yet opened - RAW REQUEST
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == "Intake in Progress" && !isValidationError)
        {
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
      }
    }

  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={openModal} handleModal={handleModal} state={"Open"} saveRequestObject={saveRequestObject} />  
      <ConfirmationModal openModal={opensaveModal} handleModal={handleSaveModal} state={currentSelectedStatus} saveRequestObject={saveRequestObject}/>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError} onClick={saveRequest}>Save</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;