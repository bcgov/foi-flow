import React from 'react';
import {Row,Col} from 'react-bootstrap';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';


const RedactionSummary = React.memo(({sections, isoipcreview}) => {
  const useStyles = makeStyles({
        heading: {
          color: '#FFF',
          fontSize: '16px !important',
          fontWeight: 'bold !important'
        },
        accordionSummary: {
          flexDirection: 'row-reverse'
        },
        sectionsHeading: {
          fontFamily: '"BCSans-Bold", sans-serif !important',
          fontSize: '16px !important',
        }
      });
      const classes = useStyles();


    return (
        <div className='request-accordian' >
            <Accordion defaultExpanded={true}>
            <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} aria-controls="redactionSummary" id="redactionSummary-header">
            <Typography className={classes.heading}>SUMMARY OF REDACTIONS</Typography>
            </AccordionSummary>
            <AccordionDetails>

              
                {sections?.Redline !== "" && (
                <div style={{margin: "0 20px"}}>
                <Typography className={classes.sectionsHeading}>
                  <b>Redaction Sections Applied</b>
                </Typography>
                <span>{sections?.Redline}</span>
                </div>
                )}
                {(isoipcreview && sections.OIPC && sections?.OIPC !== "") && (
                <div style={{margin: "0 20px", paddingTop:"20px"}}>
                <Typography className={classes.sectionsHeading}>
                  <b>OIPC Redaction Sections Applied</b>
                </Typography>
                <span>{sections?.OIPC}</span>
                </div>
                )}
              
            </AccordionDetails>
            </Accordion>
        </div>
    );
});
export default RedactionSummary;