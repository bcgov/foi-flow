import React from 'react';
import './ministriescanvassed.scss';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
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

  const tableData = selectedMinistries?.map(function(ministry,index) {
    return (
      <tr key ={index}>
        <td >{ministry.name}</td>
        <td >Request Id here</td>
      </tr>
    )
   });





 return( 
    <div className="dialog-style">     
    {/* {requestDetails &&    */}
    <Dialog className={classes.root} open={openModal} id="dialog-style"
      onClose={handleClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={'md'}
      fullWidth={true}>
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Ministries Canvassed</h2>
          <IconButton
              className="title-col3"
              onClick={handleClose}>
              <CloseIcon />
          </IconButton>
      </DialogTitle>
      <DialogContent>
        {/* <DialogContentText id="state-change-description" component={'span'}> */}
        <div className='ministries-canvassed'>
        <Table bordered className='w-auto '>
        <tbody>
          {tableData}
        </tbody>
        </Table>
        </div>
        {/* </DialogContentText> */}
      </DialogContent>
      <DialogActions>
      </DialogActions>
    </Dialog>
  {/* } */}
  </div>
  )
}

export default MinistriesCanvassed;
