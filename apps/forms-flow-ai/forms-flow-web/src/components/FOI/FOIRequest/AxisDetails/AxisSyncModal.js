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
import { useDispatch, useSelector} from "react-redux";
import { saveRequestDetails, fetchFOIRequestDetailsWrapper, fetchFOIRequestDescriptionList } from '../../../../apiManager/services/FOI/foiRequestServices';
import { fetchFOIRequestAttachmentsList } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRequestNotesList } from "../../../../apiManager/services/FOI/foiRequestNoteServices";
import {
  addAXISExtensions
} from '../../../../apiManager/services/FOI/foiExtensionServices';
import {getRequestState} from "../BottomButtonGroup/utils";
import {StateEnum} from "../../../../constants/FOI/statusEnum";
import { toast } from "react-toastify";
import { createRequestDetailsObjectFunc,
         isAxisSyncDisplayField,
         isMandatoryField } from "../utils";
import { formatDate } from "../../../../helper/FOI/helper";


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
    },[axisSyncedData])

    const saveExtensions = () => {
      dispatch(addAXISExtensions(axisExtensions, ministryId, (_err, _res) => {
        dispatch(fetchFOIRequestDetailsWrapper(requestId, ministryId));
        dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
        dispatch(fetchFOIRequestNotesList(requestId, ministryId));
        dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
      }));
    }

    const compareFields = () => {
      let updatedObj = {};
      let saveReqCopy = { ...saveRequestObject};
      saveReqCopy.axisSyncDate = requestDetailsFromAxis.axisSyncDate;
      saveReqCopy.requestPageCount = requestDetailsFromAxis.requestPageCount;      
      for(let key of Object.keys(requestDetailsFromAxis)){
        let updatedField = isAxisSyncDisplayField(key);
        if(updatedField){
          let updateNeeded= checkValidation(key);
          if(updateNeeded){
            assignDisplayedReqObj(key, updatedObj, updatedField);
          if(key !== 'Extensions' && key !== 'compareReceivedDate' && key !== 'cfrDueDate' ||
              (key === 'cfrDueDate' && requestDetailsFromAxis[key]) ){
              saveReqCopy= createRequestDetailsObjectFunc(saveReqCopy, requestDetailsFromAxis, requestId, 
                key, requestDetailsFromAxis[key], "");
            }
            else if(key === 'compareReceivedDate') 
              saveReqCopy= createRequestDetailsObjectFunc(saveReqCopy, requestDetailsFromAxis, requestId, 
                'receivedDate', requestDetailsFromAxis[key], "");
          }
        }
      }
      setDisplayedReqObj(updatedObj);
      setUpdatedSaveReqObj(saveReqCopy);
    };


    const checkValidation = (key) => {
      let mandatoryField = isMandatoryField(key);
      if(mandatoryField && !requestDetailsFromAxis[key])
        return false;
      else{
        if(key === 'Extensions' || key === 'additionalPersonalInfo')
          return true;
        else if(key === 'compareReceivedDate' && (saveRequestObject['receivedDate'] !== requestDetailsFromAxis[key] && 
                saveRequestObject['receivedDate'] !== requestDetailsFromAxis['receivedDate'])){
          return true;
        }
        else if(key !== 'compareReceivedDate' && (saveRequestObject[key] || requestDetailsFromAxis[key]) && 
          saveRequestObject[key] !== requestDetailsFromAxis[key])
          return true;
      }
      return false;
    }

    const assignDisplayedReqObj = (key,updatedObj, updatedField) => {     
      switch (key) {
        case 'dueDate':
        case 'requestProcessStart':
        case 'fromDate': 
        case 'toDate':
        case 'cfrDueDate':
        case 'originalDueDate':{
          updatedObj[updatedField] =formatDate(requestDetailsFromAxis[key], "MMM dd yyyy");
          break;
        }
        case 'compareReceivedDate':
          updatedObj[updatedField] =formatDate(requestDetailsFromAxis['receivedDate'], "MMM dd yyyy");
          break;
        case 'additionalPersonalInfo':
          if(requestDetailsFromAxis['requestType'] === 'personal'){
            let foiReqAdditionalPersonalInfo = saveRequestObject[key];
            let axisAdditionalPersonalInfo = requestDetailsFromAxis[key];
            for(let axisKey of Object.keys(axisAdditionalPersonalInfo)){
              for(let reqKey of Object.keys(foiReqAdditionalPersonalInfo)){
                updatedObj = compareAdditionalPersonalInfo(axisKey , reqKey, axisAdditionalPersonalInfo, 
                  foiReqAdditionalPersonalInfo, updatedObj);
              }
            }
            for(let reqKey of Object.keys(foiReqAdditionalPersonalInfo)){
                if(!Object.keys(axisAdditionalPersonalInfo).includes(reqKey)){
                  axisAdditionalPersonalInfo[reqKey] = foiReqAdditionalPersonalInfo[reqKey];
                }
            }
          }
          break;
        case 'Extensions':
          let extensionsArr = compareExtensions(key);
          if(extensionsArr?.length > 0 || (extensionsArr?.length === 0 && 
              requestDetailsFromAxis[key].length === 0 && extensions?.length > 0))
            updatedObj[key] = extensionsArr;
          break;
        default:
          updatedObj[updatedField] = requestDetailsFromAxis[key];
          break;
      }
      
    }

    const compareAdditionalPersonalInfo = (axisKey , reqKey, axisAdditionalPersonalInfo, 
      foiReqAdditionalPersonalInfo, updatedObj) => {
      if(axisKey === reqKey){
        if(axisAdditionalPersonalInfo[axisKey] !== foiReqAdditionalPersonalInfo[axisKey] ){
          if(isAxisSyncDisplayField(axisKey)){
            updatedObj[isAxisSyncDisplayField(axisKey)] = (axisKey === 'birthDate' && axisAdditionalPersonalInfo[axisKey]) ? 
            formatDate(axisAdditionalPersonalInfo[axisKey], "MMM dd yyyy") : axisAdditionalPersonalInfo[axisKey];
          }
          else
            updatedObj[axisKey] = axisAdditionalPersonalInfo[axisKey];
        }
      }
      return updatedObj;
    }

    const compareExtensions = (key) => {
      let extensionsArr = [];
      let extensionSet = new Set();
      const axisReasonIds = requestDetailsFromAxis[key].map(x => x.extensionreasonid);
      const foiReqReasonIds = extensions.map(x => x.extensionreasonid);
      const newAxisExtensionReasonIds = axisReasonIds.filter(x => !foiReqReasonIds.includes(x));
      const newFoiExtensionReasonIds = foiReqReasonIds.filter(x => !axisReasonIds.includes(x));
      //Scenario: Additional extension added in FOI system which are not in AXIS.
      if(newFoiExtensionReasonIds?.length > 0 || foiReqReasonIds?.length > axisReasonIds?.length ){
        extensions.forEach(obj => {
          let duplicateFoiExt = foiReqReasonIds.filter((item, index) => foiReqReasonIds.indexOf(item) !== index);
          if(newFoiExtensionReasonIds.includes(obj.extensionreasonid)){
            const property = <><span style={{color: '#f44336'}}>{obj.extensionstatus+" - "+obj.extensionreson+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")+" will be DELETED."}</span><br /></>;
            extensionsArr.push(property);
          }
          else if(duplicateFoiExt.includes(obj.extensionreasonid)){
            requestDetailsFromAxis[key]?.forEach(axisObj => {
              extensionsArr= fieldComparisonOfExtensionObj(axisObj,obj,extensionsArr,true,extensionSet);
            })
          }
        });
      }
      //Scenario: Display only those axis extensions which are not yet synced.
      if(extensions.length > 0 && requestDetailsFromAxis[key]?.length > 0){
            extensionsArr = assignExtensionForDsiplay(key,extensionsArr,newAxisExtensionReasonIds,extensionSet);
      }
      else if(requestDetailsFromAxis[key]?.length > 0){
        requestDetailsFromAxis[key].forEach(obj => {
          const property = <>{obj.extensionstatus+" - "+obj.extensionreason+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
          extensionsArr.push(property);
        });
      }
    return extensionsArr;
    } 

    const fieldComparisonOfExtensionObj = (axisObj,obj,extensionsArr,removeCase, extensionSet) => {
      if(axisObj.extensionreasonid === obj.extensionreasonid){
        if(axisObj.extensionstatusid !== obj.extensionstatusid || axisObj.approvednoofdays !== obj.approvednoofdays ||
          axisObj.extendedduedays  !== obj.extendedduedays ||
          axisObj.extendedduedays !== obj.extendedduedays  || 
          !(obj.decisiondate === axisObj.approveddate || obj.decisiondate === axisObj.denieddate)){
            if(removeCase){
              const property = <><span style={{color: '#f44336'}}>{obj.extensionstatus+" - "+obj.extensionreson+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")+" will be DELETED."}</span><br /></>;
              extensionsArr.push(property);
            }
            else{
              if(!extensionSet.has(axisObj.extensionreasonid)){
                const property = <>{axisObj.extensionstatus+" - "+axisObj.extensionreason+" - "+formatDate(axisObj.extendedduedate, "MMM dd yyyy")}<br /></>;
                extensionsArr.push(property);
                extensionSet.add(axisObj.extensionreasonid);
              }
            }
        }
      }
      return extensionsArr;
    }

    const assignExtensionForDsiplay = (key,extensionsArr,newAxisExtensionReasonIds,extensionSet) => {
      if(newAxisExtensionReasonIds?.length > 0){
        requestDetailsFromAxis[key].forEach(obj => {
          if(newAxisExtensionReasonIds.includes(obj.extensionreasonid)){
            const property = <>{obj.extensionstatus+" - "+obj.extensionreason+" - "+formatDate(obj.extendedduedate, "MMM dd yyyy")}<br /></>;
            extensionsArr.push(property);
          }
        });
      }
      else if(requestDetailsFromAxis[key]?.length >= extensions?.length){
        requestDetailsFromAxis[key].forEach(axisObj => {
            extensions?.forEach(foiReqObj => {
              extensionsArr= fieldComparisonOfExtensionObj(axisObj,foiReqObj,extensionsArr,false,extensionSet);
            })
        });
      }
      else if(extensions?.length > requestDetailsFromAxis[key]?.length){
        extensions?.forEach(foiReqObj => {
          requestDetailsFromAxis[key].forEach(axisObj => {
            extensionsArr= fieldComparisonOfExtensionObj(axisObj,foiReqObj,extensionsArr,false,extensionSet);
          })
        });
      }
      return extensionsArr;
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
          maxWidth={'md'}
          fullWidth={true}>
          <DialogTitle disableTypography id="state-change-dialog-title">
              <h2 className="state-change-header">Sync with AXIS</h2>
              <IconButton aria-label= "close" className="title-col3" onClick={handleClose}>
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