import OIPCDetailsList from "./OIPCDetailsList";
import './oipcdetails.scss';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Button from '@material-ui/core/Button';
import { makeStyles } from '@material-ui/styles';

const OIPCDetails = (props) => {
    const oipcData = [
        { oipcNumber: "F23-12345", reviewType: "Complaint", reason: "Deemed Refusal", status: "Inquiry", isInquiry: false, inquiryDate: null,  investigator: "Filip Forsberg", outcome: "Withdrawn", isJudicalReview: false, isSubAppeal: false }, 
        { oipcNumber: "F23-12346", reviewType: "Review", reason: "Other", status: "Mediation", isInquiry: false, investigator: "Peter Forsberg", outcome: "Closed", isJudicalReview: false, isSubAppeal: true },
        { oipcNumber: "F23-12347", reviewType: "Investigation", reason: "TPN-21", status: "Awaiting Order", isInquiry: false, investigator: "Quinn Hughes", outcome: "Abandoned", isJudicalReview: true, isSubAppeal: true }
    ]

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

    return (
        <div className='request-accordian' >
            <Accordion defaultExpanded={true}>
            <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />}>
            <Typography className={classes.heading}>OIPC Details</Typography>
            </AccordionSummary>
            <AccordionDetails>
                <OIPCDetailsList oipcData={oipcData} />
                <Button>Add Additional OIPC Complaint</Button>
            </AccordionDetails>
            </Accordion>
        </div>
    );
}

export default OIPCDetails;

//IDEA = MasterData is held in a oipcData [{}] state (there is a backend api call to generate the existing oipc data).  This is mapped in OIPCDetailsList where each elm is mapped as a OIPCItem. Each OIPC Item has EDITABLE Fields (unless oipcObj outcome value exists? -> therefore we disable the field)
//EACH OIPCITEM HAS ITS OWN INTERNAL STATE WE CAN change and if changed -> the oipcData state wil change as well
// When add button is clicked, we add a new oipcObj to the oipcData state which then creates a new oipcITEM with its own default state which can be edited.
// if any oipcObjs in the oipcData state are missing any of the mandatory fields -> Save button cannot be selected./is disalbed
// When save button is enabled and clicked -> we send the backend api requeset and save the oipc data in backend by sending the master oipc data over. 