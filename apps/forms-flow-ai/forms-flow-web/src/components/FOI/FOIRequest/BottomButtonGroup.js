import React, { useState } from 'react';
import './bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import {saveRequestDetails, openRequestDetails} from "../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import { ConfirmationModal } from '../customComponents';

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
    const {requestId, ministryId} = useParams();  
    const classes = useStyles();
    const dispatch = useDispatch();
    
    const [openModal, setOpenModal] = useState(false);
    const [opensaveModal, setsaveModal] = useState(false);

    const returnToQueue = (e) => {
      e.preventDefault();
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        //dispatch(push(`/foi/dashboard`));
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
            handleSaveRequest("Intake in progress", false, res.id);
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
            handleSaveRequest("Unopened", true, res.id);
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
        hasStatusRequestSaved(true)
      }
      else if (currentSelectedStatus !="" && !isValidationError){
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
      setOpenModal(false);
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
    }

    const handleSaveModal = (value) => {      
      setsaveModal(false);
      if (value) {
        if(currentSelectedStatus == "Closed" && !isValidationError)
        {
          saveRequestObject.requeststatusid = 3 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true)
        }
        else if(currentSelectedStatus == "Call For Records" && !isValidationError)
        {        
          saveRequestObject.requeststatusid = 2 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true)
        }  
        else if(currentSelectedStatus == "Redirect" && !isValidationError)
        {        
          saveRequestObject.requeststatusid = 4 // Need to take from ENUM
          saveRequest();
          hasStatusRequestSaved(true)
        }
        else if(currentSelectedStatus == "Open" && !isValidationError)
        {
          saveRequestObject.requeststatusid = 1 // Need to take from ENUM, -1 if not yet opened - RAW REQUEST
          saveRequest();
          hasStatusRequestSaved(true)
        }
        else if(currentSelectedStatus == "Intake in Progress" && !isValidationError)
        {
          saveRequest();
          hasStatusRequestSaved(true)
        }
      }
    }

  console.log(`is validation bottom ${isValidationError}`);  
  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={openModal} handleModal={handleModal} state={"Open"}/>  
      <ConfirmationModal openModal={opensaveModal} handleModal={handleSaveModal} state={currentSelectedStatus}/>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError} onClick={saveRequest}>Save</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;