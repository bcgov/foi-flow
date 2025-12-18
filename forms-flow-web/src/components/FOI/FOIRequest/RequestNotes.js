import React, { useEffect, useState }  from 'react';
import './requestnotes.scss';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
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
const RequestNotes = React.memo((_props) => {
    const classes = useStyles();

     return (
    <div className={classes.root}>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography className={classes.heading}>REQUEST NOTES</Typography>
        </AccordionSummary>
        <AccordionDetails>
        
        </AccordionDetails>
      </Accordion>
     

    </div>
    );
  });

export default RequestNotes;