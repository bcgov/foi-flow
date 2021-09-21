import React from 'react';
import './requestDescriptionHistory.scss';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { makeStyles } from '@material-ui/core/styles';
import AccordionItem from './AccordionItem';

const useStyles = makeStyles((theme) => ({
    root: {
      width: '100%',
      marginTop:'20px'
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
  }));
const RequestDescriptionHistory = React.memo(({requestDescriptionHistoryList, openModal, handleModalClose}) => {  

    const [expanded, setExpanded] = React.useState('panel1');
    const handleChange = (panel) => (event, newExpanded) => {
        setExpanded(newExpanded ? panel : false);
    };
    console.log(`requestDescriptionHistoryList = ${JSON.stringify(requestDescriptionHistoryList)}`);
    const classes = useStyles();
   
     return (
    <div className={classes.root}>
        <Dialog
          open={openModal}
          onClose={handleModalClose}
          aria-labelledby="request-history-dialog-title"
          aria-describedby="request-history-dialog-description"
          fullWidth
          maxWidth={'md'}
        >
            <DialogTitle id="request-history-dialog-title">Request History</DialogTitle>
            <DialogContent>
                {requestDescriptionHistoryList.map((details, index) => 
                     <AccordionItem details={details} index={index} key={details.type} expanded={expanded} handleChange={handleChange} />                    
            )}                
            </DialogContent>
      </Dialog>
    </div>
    );
  });

export default RequestDescriptionHistory;