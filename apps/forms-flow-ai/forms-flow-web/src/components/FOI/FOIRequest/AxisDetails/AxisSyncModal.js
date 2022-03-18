import React, {useEffect, useContext} from 'react';
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
import { fetchRequestDataFromAxis,
  saveRequestDetails 
} from '../../../../apiManager/services/FOI/foiRequestServices';
import {getRequestState} from "../BottomButtonGroup/utils";
import {StateEnum} from "../../../../constants/FOI/statusEnum";
import { toast } from "react-toastify";
import { createRequestDetailsObjectFunc } from "../utils";
import { formatDate } from "../../../../helper/FOI/helper";
//import { ActionContext } from "./ActionContext";

const useStyles = makeStyles({
 
  heading: {
    color: '#38598A',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  }
});

const AxisSyncModal = ({ axisSyncModalOpen, setAxisSyncModalOpen, saveRequestObject, 
  urlIndexCreateRequest, handleSaveRequest, currentSelectedStatus,
  hasStatusRequestSaved, requestState, requestId, ministryId,
}) => {

    const classes = useStyles();
    const [displayedReqObj, setDisplayedReqObj] = React.useState({});
    const [updatedSaveReqObj, setUpdatedSaveReqObj] = React.useState({});
    let requestDetailsFromAxis ={};
    const dispatch = useDispatch();
    const extensions = useSelector((state) => state.foiRequests.foiRequestExtesions);

    // const {
    //   axisSyncModalOpen, setAxisSyncModalOpen, saveRequestObject, 
    //   urlIndexCreateRequest, handleSaveRequest, currentSelectedStatus,
    //   hasStatusRequestSaved, requestState, requestId, ministryId,
    // } = useContext(ActionContext);

    useEffect(()=>{
      dispatch(fetchRequestDataFromAxis(saveRequestObject.axisRequestId, true, (err, data) => {
        if(!err){
            if(Object.entries(data).length !== 0){
              requestDetailsFromAxis = data;
              compareFields();  
            }
        }
      }));
    },[])


    const compareFields = () => {
      let updatedObj = {};
      let saveReqCopy = { ...saveRequestObject};
      for(let key of Object.keys(requestDetailsFromAxis)){
        var updatedField = isAxisSyncDisplayField(key);
        if(updatedField){
          if(key === 'Extensions' && requestDetailsFromAxis[key] != extensions || ((saveRequestObject[key] || requestDetailsFromAxis[key]) && saveRequestObject[key] !== requestDetailsFromAxis[key])){
            assignDisplayedReqObj(key, updatedObj, updatedField);
            if(key !== 'Extensions')
              saveReqCopy= createRequestDetailsObjectFunc(saveReqCopy, requestDetailsFromAxis, requestId, key, requestDetailsFromAxis[key], "");
          }
        }
      }
      setDisplayedReqObj(updatedObj);
      setUpdatedSaveReqObj(saveReqCopy);
    };

    const isAxisSyncDisplayField = (field) => {
      return Object.entries(AXIS_SYNC_DISPLAY_FIELDS).find(([key]) => key === field)?.[1];
    };

    const assignDisplayedReqObj = (key,updatedObj, updatedField) => {      
      switch (key) {
        case 'selectedMinistries':
          const ministryCodes = requestDetailsFromAxis[key].map(({code}) => code).join(', ');
          if(ministryCodes !== saveRequestObject[key].map(({code}) => code).join(', '))
            updatedObj[updatedField] = ministryCodes;
          break;
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
                    const property = <>{obj.extensionstatus+" - "+obj.extensionreson+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
                    extensionsArr.push(property);
                  }
                })
            });
          }
          else{
            requestDetailsFromAxis[key].forEach(obj => {
              const property = <>{obj.extensionstatus+" - "+obj.extensionreson+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
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