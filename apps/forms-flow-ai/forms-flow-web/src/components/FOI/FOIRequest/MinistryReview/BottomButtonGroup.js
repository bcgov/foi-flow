import React, { useState } from 'react';
import '../BottomButtonGroup/bottombuttongroup.scss';
import { makeStyles } from '@material-ui/core/styles';
import { useDispatch } from "react-redux";
import { getOSSHeaderDetails, saveFilesinS3 } from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveMinistryRequestDetails } from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import { ConfirmationModal } from '../../customComponents';
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { ConditionalComponent } from "../../../../helper/FOI/helper";
import clsx from 'clsx';

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
  attachmentsArray,
  stateChanged
  }) => {
  /**
   * Bottom Button Group of Review request Page
   * Button enable/disable is handled here based on the validation
   */
    const {requestId, ministryId, requestState} = useParams();  
    const classes = useStyles();
    const dispatch = useDispatch();
    
    const [opensaveModal, setsaveModal] = useState(false);

    const disableSave = isValidationError || requestState.toLowerCase() != StateEnum.callforrecords.name.toLowerCase();

    const returnToQueue = (e) => {
      if (
        !unSavedRequest ||
        window.confirm(
          "Are you sure you want to leave? Your changes will be lost."
        )
      ) {
        e.preventDefault();
        window.removeEventListener("beforeunload", alertUser);
        window.location.href = "/foi/dashboard";
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
      if (unSavedRequest) {
        e.preventDefault();
        e.returnValue = '';
      }
    }

    const handleOnHashChange = (e) => {       
      returnToQueue(e);
    };  

    React.useEffect(() => {

      if (stateChanged && currentSelectedStatus !== "" && !isValidationError){
        saveRequestModal();
      }     
    }, [currentSelectedStatus, stateChanged]);

    React.useEffect(() => {
      window.history.pushState(null, null, window.location.pathname);
      window.addEventListener('popstate', handleOnHashChange);
      window.addEventListener('beforeunload', alertUser);
      
      return () => {
        window.removeEventListener('popstate', handleOnHashChange);
        window.removeEventListener('beforeunload', alertUser);
      }
    });
    
   
    const saveRequestModal =()=>{
      if (currentSelectedStatus !== saveMinistryRequestObject?.currentState)
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
          case StateEnum.response.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.response.id;
            break;
          case StateEnum.callforrecords.name.toLowerCase(): 
            saveMinistryRequestObject.requeststatusid = StateEnum.callforrecords.id;
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
          hasStatusRequestSaved(currentSelectedStatus);
      }
    },[successCount])

    const handleSaveModal = (value, fileInfoList, files) => {
      setsaveModal(false);
      setFileCount(files?.length);

      if (!value) {
        handleSaveRequest(requestState, true, "");
        return;
      }

      if (isValidationError) {
        return;
      }

      if(!files || files.length < 1) {
        saveStatusId();
        saveMinistryRequest();
        hasStatusRequestSaved(currentSelectedStatus);
        return
      }

      dispatch(
        getOSSHeaderDetails(fileInfoList, (err, res) => {
          let _documents = [];
          if (!err) {
            res.map((header, index) => {
              const _file = files?.find(
                (file) => file.name === header.filename
              );
              const documentpath = {
                documentpath: header.filepath,
                filename: header.filename,
                category: header.filestatustransition,
              };
              _documents.push(documentpath);
              setDocuments(_documents);
              dispatch(
                saveFilesinS3(header, _file, (_err, _res) => {
                  let count = 0;
                  if (_res === 200) {
                    count = index + 1;
                  }
                  setSuccessCount(count);
                })
              );
            });
          }
        })
      );      
    };

  return (
    <div className={classes.root}>
      <ConditionalComponent condition={opensaveModal}>
        <ConfirmationModal
          attachmentsArray={attachmentsArray}
          openModal={opensaveModal}
          handleModal={handleSaveModal}
          state={currentSelectedStatus}
          saveRequestObject={saveMinistryRequestObject}
        />
      </ConditionalComponent>
      <div className="foi-bottom-button-group">
        <button
          type="button"
          className={clsx("btn", "btn-bottom", {
            [classes.btndisabled]: disableSave,
            [classes.btnenabled]: !disableSave,
          })}
          disabled={disableSave}
          onClick={saveMinistryRequest}
        >
          Save
        </button>
        {/* <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>       */}
      </div>
    </div>
  );
  });

export default BottomButtonGroup;