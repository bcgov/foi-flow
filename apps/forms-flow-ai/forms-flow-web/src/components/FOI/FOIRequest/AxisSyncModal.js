import React from 'react';
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

const useStyles = makeStyles({
  root: {
    zIndex: '1500 !important'
  },
});


const AxisSyncModal = ({axisSyncModalOpen, setAxisSyncModalOpen}) => {

    const classes = useStyles();

    const handleClose = () => {
        setAxisSyncModalOpen(false);
    };

    let selectedMinistries = [{"field" : "IAO Assigned To", "value": "Username"}, {"field" : "Applicant Last Name", "value": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."}];
    const tableData = selectedMinistries?.map(function(ministry,index) {
        return (
          <tr key ={index}>
            <td className='axis-updated-fields'>{ministry.field}</td>
           <td>{ministry.value}</td>
          </tr>
        )
    });

    return( 
        <div className='axis-sync'>     
        <Dialog className={classes.root} open={axisSyncModalOpen} id="dialog-style"
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
          <div style={{textAlign: 'center'}}>
              <p>Are you sure you want to sync Request with AXIS? </p>
              <p>This is update all fields in Request based on changes made in AXIS</p>
          </div>
          <Accordion style={{margin: '30px'}} >
            <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography className={classes.heading}>Review Changes from AXIS</Typography>
            </AccordionSummary>
            <AccordionDetails>
            <div className='axis-accordian-detail'>
                <Table bordered className='w-auto'>
                <tbody>
                    {tableData}
                </tbody>
                </Table>
            </div>
            </AccordionDetails>
          </Accordion>
          <div className='axis-modal-actions'>
            <button type="button" style={{width: '48%'}}
                className="btn btn-bottom">
                Save Changes
            </button>
            <button type="button" className='axis-modal-action-cancel'>
                Cancel
            </button>
          </div>
          </DialogContent>
          <DialogActions>
          
          </DialogActions>
        </Dialog>
      </div>
      )

}

export default AxisSyncModal;