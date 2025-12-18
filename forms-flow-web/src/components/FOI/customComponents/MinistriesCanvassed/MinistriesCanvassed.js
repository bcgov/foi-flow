import React from 'react';
import './ministriescanvassed.scss';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { Table } from 'react-bootstrap';
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import { makeStyles } from '@material-ui/styles';

const useStyles = makeStyles({
  root: {
    zIndex: '1500 !important'
  },
});


const MinistriesCanvassed = ({openModal,selectedMinistries, setModal} ) => {

  const classes = useStyles();

  const handleClose = () => {
    setModal(false);
  };

  const redirectUrl =(ministry) => {
    let url=`/foi/foirequests/${ministry.requestid}/ministryrequest/${ministry.ministryrequestid}`;
    window.location.href=url;
  }

  const tableData = selectedMinistries?.map(function(ministry,index) {
    return (
      <tr key ={index}>
        <td className='ministry-name'>{ministry.name}</td>
       <td className='ministry-requestid' onClick={() => redirectUrl(ministry)} >{(ministry.axisrequestid?ministry.axisrequestid:ministry.filenumber)}</td>
      </tr>
    )
   });


 return( 
    <div data-testid="MinistriesCanvassed">     
    <Dialog className={classes.root} open={openModal} id="dialog-style"
      onClose={handleClose}
      maxWidth={'md'}
      fullWidth={true}>
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Ministries Canvassed</h2>
          <IconButton aria-label= "close"
              className="title-col3"
              onClick={handleClose}>
              <CloseIcon />
          </IconButton>
      </DialogTitle>
      <DialogContent>
      <div className='ministries-canvassed'>
      <Table bordered className='w-auto'>
      <tbody>
        {tableData}
      </tbody>
      </Table>
      </div>
      </DialogContent>
      <DialogActions>
      </DialogActions>
    </Dialog>
  </div>
  )
}

export default MinistriesCanvassed;
