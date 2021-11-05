import React, { useState } from 'react';
import '../bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import {push} from "connected-react-router";
import { saveMinistryRequestDetails, getOSSHeaderDetails, saveFilesinS3 } from "../../../../apiManager/services/FOI/foiRequestServices";
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
  saveMinistryRequestObject,
  unSavedRequest,
  handleSaveRequest,
  currentSelectedStatus,
  hasStatusRequestSaved,
  setUnSavedRequest
  }) => {
  /**
   * Bottom Button Group of Review request Page
   * Button enable/disable is handled here based on the validation
   */
    const {requestId, ministryId, requestState} = useParams();  
    const classes = useStyles();
    const dispatch = useDispatch();
    
    const [opensaveModal, setsaveModal] = useState(false);

    const [hasUnSaved, setHasUnSaved] = useState();

    const disableSave = isValidationError || requestState.toLowerCase() != StateEnum.callforrecords.name.toLowerCase();

    const returnToQueue = (e) => {
      if (!hasUnSaved || (hasUnSaved && window.confirm("Are you sure you want to leave? Your changes will be lost."))) {
        e.preventDefault();
        setUnSavedRequest(false);
        window.location.href = '/foi/dashboard';
      }
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
            const _state = currentSelectedStatus ? currentSelectedStatus : requestState;
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
      if (hasUnSaved) {
        e.preventDefault();
        e.returnValue = '';
      }
    }

    const handleOnHashChange = (e) => {       
      returnToQueue(e);
    };  

    React.useEffect(() => {
      setHasUnSaved(unSavedRequest);
    }, [unSavedRequest]);

    React.useEffect(() => {

      if (currentSelectedStatus !== "" && !isValidationError){
        saveRequestModal();
      }

      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener('popstate', handleOnHashChange);
      window.addEventListener('beforeunload', alertUser);
      // window.addEventListener('unload', handleOnHashChange);   
      
      return () => {
        window.removeEventListener('popstate', handleOnHashChange);
        window.removeEventListener('beforeunload', alertUser);
        // window.removeEventListener('unload', handleOnHashChange);
      }
    });
    
   
    const saveRequestModal =()=>{
      setsaveModal(true);
    }

    const [successCount, setSuccessCount] = useState(0);
    const [fileCount, setFileCount] = useState(0);
    const [documents, setDocuments] = useState([]);

    const saveStatusId = () => {
      if (currentSelectedStatus) {
        switch(currentSelectedStatus.toLowerCase()) {
          case StateEnum.review.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.review.id;
            break;
          case StateEnum.feeassessed.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.feeassessed.id;
            break;
          case StateEnum.deduplication.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.deduplication.id;
            break;
          case StateEnum.harms.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.harms.id;
            break;
          case StateEnum.signoff.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.signoff.id;
            break;
        }
      }
    }

    React.useEffect(() => {
      if (successCount === fileCount && successCount !== 0) {
          setsaveModal(false);
          saveStatusId();
          saveMinistryRequestObject.documents = documents;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
      }
    },[successCount])

    const handleSaveModal = (value, fileInfoList, files) => {
      setsaveModal(false);
      setFileCount(files.length);
      if (value) {
        if(!isValidationError)
        {
          if (files.length !== 0) {
            dispatch(getOSSHeaderDetails(fileInfoList, (err, res) => {         
              let _documents = [];
              if (!err) {
                res.map((header, index) => {
                  const _file = files.find(file => file.name === header.filename);
                  const documentpath = {documentpath: header.filepath};
                  _documents.push(documentpath);
                  setDocuments(_documents);
                  dispatch(saveFilesinS3(header, _file, (err, res) => {

                    if (res === 200) {

                      setSuccessCount(index+1);
                    }
                    else {
                      setSuccessCount(0);
                    }
                  }));
                });
              }
            }));
          }
          else {
            saveStatusId();         
            saveMinistryRequest();
            hasStatusRequestSaved(true,currentSelectedStatus)
          }
        }
        else if(currentSelectedStatus == StateEnum.deduplication.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.deduplication.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.feeassessed.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.feeassessed.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.response.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.response.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.callforrecords.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.callforrecords.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.signoff.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.signoff.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.harms.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.harms.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
        else if(currentSelectedStatus == StateEnum.review.name && !isValidationError)
        {
          saveMinistryRequestObject.requeststatusid = StateEnum.review.id;
          saveMinistryRequest();
          hasStatusRequestSaved(true,currentSelectedStatus)
        }
      }
    }

  return (
    <div className={classes.root}>
      <ConfirmationModal openModal={opensaveModal} handleModal={handleSaveModal} state={currentSelectedStatus} saveRequestObject={saveMinistryRequestObject}/>
      <div className="foi-bottom-button-group">
      <button type="button" className={`btn btn-bottom ${disableSave ? classes.btndisabled : classes.btnenabled}`} disabled={disableSave} onClick={saveMinistryRequest}>Save</button>
      {/* <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>       */}
      </div>
    </div>
    );
  });

export default BottomButtonGroup;