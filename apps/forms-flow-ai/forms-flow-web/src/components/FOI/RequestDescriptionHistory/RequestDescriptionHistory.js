import React from 'react';
import './requestDescriptionHistory.scss';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { makeStyles } from '@material-ui/core/styles';

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

    const classes = useStyles();
    //<h3 className="foi-review-request-text">Request History</h3>
     return (
    <div className={classes.root}>
        <Dialog
          open={openModal}
          onClose={handleModalClose}
          aria-labelledby="request-history-dialog-title"
          aria-describedby="request-history-dialog-description"
        >
            <DialogTitle id="request-history-dialog-title">Request History</DialogTitle>
            <DialogContent>
                <Accordion>
                    <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls="panel1a-content"
                    id="panel1a-header"
                    >
                    <Typography className={classes.heading}>REQUEST DESCRIPTION</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                    <Typography>
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse malesuada lacus ex,
                        sit amet blandit leo lobortis eget.
                    </Typography>
                    </AccordionDetails>
                </Accordion>
            </DialogContent>
      </Dialog>
    </div>
    );
  });

export default RequestDescriptionHistory;