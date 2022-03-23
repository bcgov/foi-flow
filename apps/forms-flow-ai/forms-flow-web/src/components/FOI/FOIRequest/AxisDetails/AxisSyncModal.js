import React, {useEffect} from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { Table } from 'react-bootstrap';
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import './axissyncmodal.scss';
import AXIS_SYNC_DISPLAY_FIELDS from '../../../../constants/FOI/axisSyncDisplayFields';
import { useDispatch, useSelector} from "react-redux";
import { saveRequestDetails } from '../../../../apiManager/services/FOI/foiRequestServices';
import {
  addAXISExtensions
} from '../../../../apiManager/services/FOI/foiExtensionServices';
import {getRequestState} from "../BottomButtonGroup/utils";
import {StateEnum} from "../../../../constants/FOI/statusEnum";
import { toast } from "react-toastify";
import { createRequestDetailsObjectFunc } from "../utils";
import { formatDate } from "../../../../helper/FOI/helper";
import MANDATORY_FOI_REQUEST_FIELDS from "../../../../constants/FOI/mandatoryFOIRequestFields";

const useStyles = makeStyles({
 
  heading: {
    color: '#38598A',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  }
});

const AxisSyncModal = ({ axisSyncModalOpen, setAxisSyncModalOpen, saveRequestObject, 
  urlIndexCreateRequest, handleSaveRequest, currentSelectedStatus,
  hasStatusRequestSaved, requestState, requestId, ministryId, axisSyncedData
}) => {

    const classes = useStyles();
    const [displayedReqObj, setDisplayedReqObj] = React.useState({});
    const [updatedSaveReqObj, setUpdatedSaveReqObj] = React.useState({});
    let requestDetailsFromAxis ={...axisSyncedData};
    const [axisExtensions, setAxisExtension] = React.useState([]);
    const dispatch = useDispatch();
    const extensions = useSelector((state) => state.foiRequests.foiRequestExtesions);

    useEffect(()=>{
        if(Object.entries(requestDetailsFromAxis).length !== 0){
          setAxisExtension(requestDetailsFromAxis?.Extensions); 
          compareFields();  
        }
    },[requestDetailsFromAxis])

    const saveExtensions = () => {
      dispatch(addAXISExtensions(axisExtensions, ministryId));
    }

    const compareFields = () => {
      let updatedObj = {};
      let saveReqCopy = { ...saveRequestObject};
      saveReqCopy.axisSyncDate = requestDetailsFromAxis.axisSyncDate;
      saveReqCopy.requestPageCount = requestDetailsFromAxis.requestPageCount;      
      for(let key of Object.keys(requestDetailsFromAxis)){
        var updatedField = isAxisSyncDisplayField(key);
        if(updatedField){
          var updateNeeded= checkValidation(key);
          if(updateNeeded){
            assignDisplayedReqObj(key, updatedObj, updatedField);
            if(key !== 'Extensions')
              saveReqCopy= createRequestDetailsObjectFunc(saveReqCopy, requestDetailsFromAxis, requestId, 
                key, requestDetailsFromAxis[key], "");
          }
        }
      }
      setDisplayedReqObj(updatedObj);
      setUpdatedSaveReqObj(saveReqCopy);
    };

    const isAxisSyncDisplayField = (field) => {
      return Object.entries(AXIS_SYNC_DISPLAY_FIELDS).find(([key]) => key === field)?.[1];
    };

    const isMandatoryField = (field) => {
      return Object.entries(MANDATORY_FOI_REQUEST_FIELDS).find(([key]) => key === field)?.[1];
    };

    const checkValidation = (key) => {
      var mandatoryField = isMandatoryField(key);
      if(mandatoryField && requestDetailsFromAxis[key])
        return true;
      else if(!mandatoryField){
        if((key === 'Extensions' && requestDetailsFromAxis[key] != extensions))
          return true;
        if((saveRequestObject[key] || requestDetailsFromAxis[key]) && saveRequestObject[key] !== requestDetailsFromAxis[key])
          return true;
      }
      return false;
    }

    const assignDisplayedReqObj = (key,updatedObj, updatedField) => {      
      switch (key) {
        case 'dueDate':
        case 'axisSyncDate':
        case 'fromDate': 
        case 'toDate':
        case 'originalDueDate':{
          updatedObj[updatedField] =formatDate(requestDetailsFromAxis[key], "MMM dd yyyy");
          break;
        }
        case 'receivedDateUF':{
          console.log("Inside receivedDateUF : ", formatDate(requestDetailsFromAxis['receivedDate'], "MMM dd yyyy"))
          updatedObj['receivedDate'] =formatDate(requestDetailsFromAxis['receivedDate'], "MMM dd yyyy");
          break;
        }
        case 'Extensions':
            let extensionsArr = [];
            if(extensions.length > 0){
              requestDetailsFromAxis[key].forEach(obj => {
                  extensions?.forEach(obj1 => {
                    if(obj !== obj1){
                      const property = <>{obj.extensionstatus+" - "+obj.extensionreason+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
                      extensionsArr.push(property);
                    }
                  })
              });
          }
          else{
            requestDetailsFromAxis[key].forEach(obj => {
              const property = <>{obj.extensionstatus+" - "+obj.extensionreason+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
              extensionsArr.push(property);
            });
          }
            updatedObj[key] = extensionsArr;
          break;
        default:
          updatedObj[updatedField] = requestDetailsFromAxis[key];
          break;
      }
      
    }

    const handleClose = () => {
        setAxisSyncModalOpen(false);
    };


    const saveAxisData = async () => {
      if (urlIndexCreateRequest > -1)
        updatedSaveReqObj.requeststatusid = StateEnum.intakeinprogress.id;
      dispatch(saveRequestDetails(updatedSaveReqObj, urlIndexCreateRequest,requestId,ministryId,
          (err, res) => {
            if (!err) {
              toast.success("The request has been saved successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
              saveExtensions();
              const _state = getRequestState({
                currentSelectedStatus,
                requestState,
                urlIndexCreateRequest,
                saveRequestObject,
              });
              handleSaveRequest(_state, false, res.id);
              hasStatusRequestSaved(currentSelectedStatus);
            } else {
              toast.error(
                "Temporarily unable to save your request. Please try again in a few minutes.",
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
              handleSaveRequest(requestState, true, "");
            }
          }
        )
      );
    };


    return  Object.entries(displayedReqObj).length > 0 && (
        <>
        <Dialog className={`axis-sync ${classes.root}`}  open={axisSyncModalOpen} id="dialog-style"
          onClose={handleClose}
          aria-labelledby="state-change-dialog-title"
          aria-describedby="state-change-dialog-description"
          maxWidth={'md'}
          fullWidth={true}>
          <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Sync with AXIS</h2>
              <IconButton className="title-col3" onClick={handleClose}>
                  <CloseIcon />
              </IconButton>
          </DialogTitle>
          <DialogContent>
          <div className="confirmation-msg">
              <span>Are you sure you want to sync Request #{saveRequestObject.axisRequestId} with AXIS?</span><br/>
              <span>This will update all fields in Request based on changes made in AXIS</span>
          </div>
          <Accordion style={{margin: '30px'}} >
            <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography className={classes.heading}>Review Changes from AXIS</Typography>
            </AccordionSummary>
            <AccordionDetails>
            <div className='axis-accordian-detail'>
                <Table bordered className='updated-contents-table'>
                <tbody>
                {Object.entries(displayedReqObj).map(([key, val]) => 
                <tr key= {key}>
                    <td className='axis-updated-fields'>{key}</td>
                    <td>{val}</td>
                  </tr>
                )}
                </tbody>
                </Table>
            </div>
            </AccordionDetails>
          </Accordion>
          <div className='axis-modal-actions'>
            <button type="button" style={{width: '48%'}}
                className="btn btn-bottom" onClick={saveAxisData}>
                Save Changes
            </button>
            <button type="button" onClick={handleClose} className='axis-modal-action-cancel'>
                Cancel
            </button>
          </div>
          </DialogContent>
          <DialogActions>
          
          </DialogActions>
        </Dialog>
      </>
      )
}

export default AxisSyncModal;