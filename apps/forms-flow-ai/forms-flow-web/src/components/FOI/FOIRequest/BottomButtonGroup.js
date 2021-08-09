import React from 'react';
import './bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import {saveRequestDetails} from "../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';

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

const BottomButtonGroup = React.memo(({isValidationError, urlIndexCreateRequest, saveRequestObject, unSavedRequest }) => {
  /**
   * Bottom Button Group of Review request Page
   * Button enable/disable is handled here based on the validation
   */
    const classes = useStyles();
    const dispatch = useDispatch();

    const returnToQueue = (e) => {
      e.preventDefault();
      if (!unSavedRequest || (unSavedRequest && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        dispatch(push(`/foi/dashboard`));
      }
    }
    const saveRequest = async () => {      
      dispatch(saveRequestDetails(saveRequestObject, urlIndexCreateRequest, (err, res) => {
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
            unSavedRequest = false;
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
            unSavedRequest = true;
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

  return (
    <div className={classes.root}>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${isValidationError  ? classes.btndisabled : classes.btnenabled}`} disabled={isValidationError} onClick={saveRequest}>Save</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError}>Open Request</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError}>Split Request</button>
      <button type="button" className={`btn btn-bottom ${isValidationError || urlIndexCreateRequest > -1 ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isValidationError}>Redirect in Full</button>
      <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>      
      </div>
    </div>
    );
  });

export default BottomButtonGroup;