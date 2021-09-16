import React from 'react';
import './requestDescriptionHistory.scss';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

const AccordionItem = React.memo(({details, index, expanded, handleChange}) => {
    
     return (
        <Accordion expanded={expanded === `panel${index+1}`} onChange={handleChange(`panel${index+1}`)}>
            <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1a-content"
            id="acc-header"            
            >
                <Typography className="acc-request-description">{`${details.type.toLowerCase() === "original" ? "ORIGINAL ": ""}REQUEST DESCRIPTION`}</Typography>
                <Typography>{details.createdBy} - {details.createdDate}</Typography>
            </AccordionSummary>
            <AccordionDetails className="acc-details">
                <div className="acc-details-1">
                    <div className="acc-request-description-row">
                        <Typography className="acc-daterange-heading"><b>Date Range for Record Search</b></Typography>
                        <div className="acc-request-dates">
                            <Typography className="acc-start-date"><b>Start Date: </b>{details.startDate}</Typography>
                            <Typography><b>End Date: </b>{details.endDate}</Typography>
                        </div>                                                              
                    </div>
                    <Typography className="acc-bottom-request-description-header"><b>Request Description</b></Typography>
                    <Typography>
                    {details.description}
                    </Typography>
                </div>
            </AccordionDetails>
        </Accordion>         
    );
  });

export default AccordionItem;