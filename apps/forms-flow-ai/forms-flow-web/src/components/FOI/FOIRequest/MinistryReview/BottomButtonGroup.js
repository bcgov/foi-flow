import React, { useState } from 'react';
import '../bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import { saveRequestDetails, saveMinistryRequestDetails } from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import { ConfirmationModal } from '../../customComponents';
import { StateEnum } from '../../../../constants/FOI/statusEnum';

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
    // btnsecondaryenabled: {
    //   border: '1px solid #38598A',
    //   backgroundColor: '#FFFFFF',
    //   color: '#38598A'
    // }
  }));

const BottomButtonGroup = React.memo(({
  isValidationError,
  saveRequestObject,
  saveMinistryRequestObject,
  unSavedRequest,
  handleSaveRequest,
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
    
    const [opensaveModal, setsaveModal] = useState(false);

    const returnToQueue = (e) => {
      e.preventDefault();
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        window.location.href = '/foi/dashboard';
      }
    }
 
    const saveRequest = async () => {
      dispatch(saveRequestDetails(saveRequestObject, 0, requestId, ministryId, (err, res) => {
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
            const _state = currentSelectedStatus ? currentSelectedStatus : (requestState ? requestState: StateEnum.callforrecords.name);
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

    const saveMinistryRequest = async () => {
      dispatch(saveMinistryRequestDetails(saveMinistryRequestObject, requestId, ministryId, (err, res) => {
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
            handleSaveRequest(currentSelectedStatus, false, res.id);
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
      e.preventDefault();
      if (unSavedRequest) {
        e.returnValue = '';
      }
    }

    React.useEffect(() => {
      const handleOnHashChange = (e) => {       
        returnToQueue(e);
      };  
            
      if (currentSelectedStatus !== "" && !isValidationError){
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
    
   
    const saveRequestModal =()=>{
      setsaveModal(true);
    }

    const handleSaveModal = (value) => {      
      setsaveModal(false);      
      if (value) {
        if(currentSelectedStatus == StateEnum.review.name && !isValidationError)
        {
          saveRequestObject.requeststatusid = StateEnum.review.id;
          saveRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        //else if(currentSelectedStatus == StateEnum.response.name && !isValidationError) {}
      }
    }

  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={opensaveModal} handleModal={handleSaveModal} state={currentSelectedStatus} saveRequestObject={saveRequestObject}/>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError} onClick={saveMinistryRequest}>Save</button>
      {/* <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>       */}
      </div>
    </div>
    );
  });

export default BottomButtonGroup;