import React from 'react';
import {Row,Col} from 'react-bootstrap';
import './divisionaltracking.scss';
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';


const DivisionalTracking = React.memo(({divisions}) => {

    const useStyles = makeStyles({
        heading: {
          color: '#FFF',
          fontSize: '16px !important',
          fontWeight: 'bold !important'
        },
        accordionSummary: {
          flexDirection: 'row-reverse'
        }
      });
      const classes = useStyles();

    const displayDivisions = divisions?.map((division, index) =>
        <Row key={index} className='divisions-row'>
            <Col className='text-right'>{division.divisionname}</Col>
            <Col style={{marginTop: '-4px'}}>
              <div className='arrow'>
                <div className='line'></div>
                <div className='point'></div>
             </div>
             </Col>
            <Col className='text-left'>{division.stagename}</Col>
        </Row>
    );

    return (
        <div className='request-accordian' >
            <Accordion defaultExpanded={true}>
            <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} aria-controls="divisionalTracking" id="divisionalTracking-header">
            <Typography className={classes.heading}>DIVISIONAL TRACKING</Typography>
            </AccordionSummary>
            <AccordionDetails>
                {displayDivisions}
            </AccordionDetails>
            </Accordion>
        </div>
    );
});
export default DivisionalTracking;