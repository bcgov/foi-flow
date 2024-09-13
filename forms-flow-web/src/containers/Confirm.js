import React from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({

    dialogPaper: {
        width: '700px',
        maxWidth: '850px',
        height: '200px'
    },
    dialogContent: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
    }
}));

const Confirm = React.memo((props)=>{
    const { modalOpen=false, onYes, onNo, message, yesText = 'Yes', noText = 'No' } = props;
    const classes = useStyles();
    // return (
    //   <>
    //       <Modal show={modalOpen}>
    //           <Modal.Header>
    //              <Modal.Title>Delete Confirmation</Modal.Title>
    //           </Modal.Header>
    //           <Modal.Body>{message}</Modal.Body>
    //           <Modal.Footer>
    //           <Button type="button" className="btn btn-default" onClick={onYes}>{yesText}</Button>
    //           <Button type="button" className="btn btn-danger mr-3" onClick={onNo}>{noText}</Button>
    //           </Modal.Footer>
    //       </Modal>
    //     </>
    // )

    return (  
        <>
        <div className="state-change-dialog">
            <Dialog
            open={modalOpen}
            onClose={onNo}
            aria-labelledby="state-change-dialog-title"
            //aria-describedby="restricted-modal-text"
            maxWidth={false}
            //fullWidth={true}
            PaperProps={{
                className: classes.dialogPaper,
            }}
            >
            {/* <DialogTitle disableTypography id="state-change-dialog-title">
                <h2 className="state-change-header">Restricted File</h2>
                <IconButton className="title-col3" onClick={onNo}>
                    <i className="dialog-close-button">Close</i>
                    <CloseIcon />
                </IconButton>
            </DialogTitle> */}
            <DialogContent className={classes.dialogContent}>
                {/* <div className="modal-msg"> */}
                    {/* <div className="confirmation-message">
                        {message}
                    </div> */}
                    <div className='modal-msg-description'>
                        {message}
                    </div>
                {/* </div> */}
            </DialogContent>
            <DialogActions>
                <button
                className='btn-bottom btn-save btn'
                //{classes.btnBottom}
                style={{marginTop:'0px'}}
                onClick={onYes}
                >
                {yesText}
                </button>
                <button className='btn-cancel' onClick={onNo}>
                {noText}
                </button>
            </DialogActions>
            </Dialog>
        </div>
        </>
    );
})

export default Confirm;
