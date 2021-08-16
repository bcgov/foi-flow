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
  handleOpenRequest 
  }) => {
  /**
   * Bottom Button Group of Review request Page
   * Button enable/disable is handled here based on the validation
   */
    const {requestId, ministryId} = useParams();  
    const classes = useStyles();
    const dispatch = useDispatch();

    const returnToQueue = (e) => {
      e.preventDefault();
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        dispatch(push(`/foi/dashboard`));
      }
    }
    const saveRequest = async () => {      
      dispatch(saveRequestDetails(saveRequestObject, urlIndexCreateRequest, requestId, (err, res) => {
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
            handleSaveRequest("Intake in progress", false);
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
            handleSaveRequest("Unopened", true);
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
    const [openModal, setOpenModal] = useState(false);
   
    const openRequest = () => {
      saveRequestObject.id = saveRequestObject.id ? saveRequestObject.id :requestId; 
      setOpenModal(true);     
    }
    const handleModal = (value) => {
      setOpenModal(false);
      if (value) {
        dispatch(openRequestDetails(saveRequestObject, (err, res) => {
          if(!err) {
            console.log(res);
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
            handleOpenRequest("","",true);
          }
        })); 
      }
    }
  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={openModal} handleModal={handleModal}/>  
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError} onClick={saveRequest}>Save</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 || ministryId ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError} onClick={openRequest}>Open Request</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 || ministryId ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError}>Split Request</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 || ministryId ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError}>Redirect in Full</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;