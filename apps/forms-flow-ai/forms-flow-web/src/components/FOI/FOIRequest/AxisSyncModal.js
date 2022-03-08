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

const useStyles = makeStyles({
 
  heading: {
    color: '#38598A',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  }
});


const AxisSyncModal = ({axisSyncModalOpen, setAxisSyncModalOpen, saveRequest, saveRequestObject}) => {

    const classes = useStyles();
    const [updatedFields, setUpdatedFields] = React.useState({});
    let sampleRequestDetails ={};

    useEffect(()=>{
      sampleRequestDetails = {"axisRequestId":"EDU-2015-50012","axisSyncDate":"2022-03-03T13:59:18Z",
      "description":"Copies of all my school records when taught by Miss Stacey at the Avonlea School.","fromDate":null,
      "toDate":null,"requestType":"personal","receivedDate":"2015-02-19","receivedDateUF":"2015-02-19T00:00:00Z",
      "requestProcessStart":"2015-02-19","dueDate":"2015-04-09","originalDueDate":null,"category":"Individual","receivedMode":"Email",
      "deliveryMode":"Secure File Transfer","ispiiredacted":true,"firstName":"Anne","middleName":"","lastName":"Shirely",
      "businessName":"Rollings Reliables","email":"redhairedanne@greengables.ca","address":"Green Gables","addressSecondary":"",
      "city":"Avonlea","province":"Prince Edward Island","country":"Canada","postal":"K9K 9K9","phonePrimary":"250-998-8956",
      "phoneSecondary":"250-153-1864","workPhonePrimary":"250-545-2454","workPhoneSecondary":"","correctionalServiceNumber":null,
      "publicServiceEmployeeNumber":null,"selectedMinistries":[{"code":"EDUC"}],"additionalPersonalInfo":{"birthDate":null,
      "anotherFirstName":"","anotherMiddleName":"","anotherLastName":"","personalHealthNumber":""}};
      compareFields();
    },[])


    const compareFields = () => {
      let updatedObj = {};
        for(let key of Object.keys(saveRequestObject)){
          if(isAxisSyncDisplayField(key)){
            if(saveRequestObject[key] !== sampleRequestDetails[key]){
              if(key === 'selectedMinistries'){
                const ministryCodes = sampleRequestDetails[key].map(({code}) => code).join(', ');
                updatedObj[key] = ministryCodes;
              }
              else if(key ==='additionalPersonalInfo'){
                let additionalPersonalInfo = saveRequestObject[key];
                for(let key1 of Object.keys(additionalPersonalInfo)){
                  updatedObj[key1] = additionalPersonalInfo[key];
                }
              }
              else
                updatedObj[key] = sampleRequestDetails[key];
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
                className="btn btn-bottom" onClick={saveRequest}>
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