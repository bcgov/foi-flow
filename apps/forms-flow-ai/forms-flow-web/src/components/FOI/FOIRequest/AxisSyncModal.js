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
import AXIS_SYNC_DISPLAY_FIELDS from '../../../constants/FOI/axisSyncDisplayFields';
import { useDispatch} from "react-redux";
import { fetchRequestDataFromAxis } from '../../../apiManager/services/FOI/foiRequestServices';

const useStyles = makeStyles({
 
  heading: {
    color: '#38598A',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  }
});


const AxisSyncModal = ({requestId, ministryId, axisSyncModalOpen, setAxisSyncModalOpen, saveRequest, saveRequestObject}) => {

    const classes = useStyles();
    const [updatedFields, setUpdatedFields] = React.useState({});
    let requestDetailsValue ={};
    const dispatch = useDispatch();

    useEffect(()=>{
      dispatch(fetchRequestDataFromAxis(saveRequestObject.axisRequestId, true, (err, data) => {
        if(!err){
            if(Object.entries(data).length !== 0){
              requestDetailsValue = data;
              console.log("Sample Data:", requestDetailsValue);
              saveExtensions(requestDetailsValue?.Extension);
              compareFields();  
            }
        }
    }));
      
    },[])

    const saveExtensions = (extensions) => {
      console.log(`extensions === ${extensions}`);
    }

    const compareFields = () => {
      let updatedObj = {};
        for(let key of Object.keys(saveRequestObject)){
          if(isAxisSyncDisplayField(key)){
            if(saveRequestObject[key] !== requestDetailsValue[key]){
              if(key === 'selectedMinistries'){
                const ministryCodes = requestDetailsValue[key].map(({code}) => code).join(', ');
                updatedObj[key] = ministryCodes;
              }
              else if(key ==='additionalPersonalInfo'){
                let additionalPersonalInfo = saveRequestObject[key];
                for(let key1 of Object.keys(additionalPersonalInfo)){
                  updatedObj[key1] = additionalPersonalInfo[key];
                }
              }
              else
                updatedObj[key] = requestDetailsValue[key];
            }
          }
          }
          console.log(updatedObj);
          setUpdatedFields(updatedObj);
    };

    const isAxisSyncDisplayField = (field) => {
      return Object.values(AXIS_SYNC_DISPLAY_FIELDS).some((group) => group == field);
    };

    const handleClose = () => {
        setAxisSyncModalOpen(false);
    };

    const saveAxisData = () => {
      //setSaveRequestObject(requestDetailsValue);
      saveRequest();
    }


    return  Object.entries(updatedFields).length > 0 && (
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
                {Object.entries(updatedFields).map(([key, val]) => 
                <tr>
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