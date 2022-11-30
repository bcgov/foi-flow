import React from 'react';
import './requestDescriptionHistory.scss';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { makeStyles } from '@material-ui/core/styles';
import AccordionItem from './AccordionItem';

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%'
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
  }));
const RequestDescriptionHistory = React.memo(({requestDescriptionHistoryList, openModal, handleModalClose}) => {  

    const [expanded, setExpanded] = React.useState('panel1');
    const handleChange = (panel) => (_event, newExpanded) => {
        setExpanded(newExpanded ? panel : false);
    };
    
    const classes = useStyles();
   
     return (
    <div className={classes.root}>
        <Dialog
          open={openModal}
          onClose={handleModalClose}
          aria-labelledby="request-history-dialog-title"
          aria-description="request-history-dialog-description"
          fullWidth
          maxWidth={'md'}
        >
            <DialogTitle disableTypography id="request-history-dialog-title">
              <h2 className="request-history-header">Request History            </h2>
              <IconButton onClick={handleModalClose} value="close">
                <i className="dialog-close-button">Close</i>
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent id="request-history-content">
                {requestDescriptionHistoryList.map((details, index) => 
                     <AccordionItem key={index} details={details} index={index} expanded={expanded} handleChange={handleChange} />                    
            )}                
            </DialogContent>
      </Dialog>
    </div>
    );
  });

export default RequestDescriptionHistory;