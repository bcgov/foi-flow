import { useState } from 'react';
import OIPCDetailsList from "./OIPCDetailsList";
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { makeStyles } from '@material-ui/styles';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCirclePlus } from '@fortawesome/free-solid-svg-icons';

const OIPCDetails = (props) => {
  //Local State
  const createOIPCId = (oipcData) => {
    if (oipcData.length > 0) {
      return oipcData.map((item, index) => {
        item.id = index;
        return item;
      });
    }
  }
    const [oipcData, setOipcData] = useState(createOIPCId([
      { oipcNumber: "F23-12345", reviewType: "Complaint", reason: "Extension", status: "Inquiry", isInquiry: false, inquiryDate: null, receivedDate: "2022-05-08", investigator: "Filip Forsberg", outcome: "Withdrawn", isJudicalReview: false, isSubAppeal: false }, 
      { oipcNumber: "F23-12346", reviewType: "Review", reason: "Other", status: "Mediation", isInquiry: false, inquiryDate: null, receivedDate: "2022-09-08", investigator: "Peter Forsberg", outcome: "Closed", isJudicalReview: false, isSubAppeal: true },
  ]));

    //Styling
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

    //Functions
    const addOIPC = () => {
      setOipcData((prev) => {
        return [...prev, {
          id: oipcData.length > 0 ? oipcData[oipcData.length - 1].id + 1 : 0,
          oipcNumber: "", 
          reviewType: "", 
          reason: "", 
          status: "", 
          isInquiry: false, 
          receivedDate: "", 
          investigator: "", 
          outcome: "", 
          isJudicalReview: false, 
          isSubAppeal: false
        }];
      })
    }
    const removeOIPC = (oipcId) => {
      setOipcData((prev) => {
        const previousOIPCData = [...prev];
        return previousOIPCData.filter(oipc => oipcId !== oipc.id);
      });
    }
    const updateOIPC = (newOIPCObj) => {
      setOipcData((prev) => {
        const previousOIPCData = [...prev];
        return previousOIPCData.map((oipc) => {
          if (oipc.id === newOIPCObj.id) {
            return newOIPCObj;
          } else {
            return oipc;
          }
        });
      });
    }
      
    return (
        <div className='request-accordian' >
            <Accordion defaultExpanded={true}>
            <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />}>
            <Typography className={classes.heading}>OIPC DETAILS</Typography>
            </AccordionSummary>
            <AccordionDetails>
                <OIPCDetailsList oipcData={oipcData} removeOIPC={removeOIPC} updateOIPC={updateOIPC} />
                <div style={{display: "flex", flexDirection: "row", alignItems: "center", margin: "7px 0px 7px 0px"}}>
                    <button onClick={() => addOIPC()} style={{ border: "none", background: "none" }}>
                        <FontAwesomeIcon icon={faCirclePlus}  size="lg" color="#38598A" />
                    </button>
                    <p style={{fontWeight: "bold", color: "#38598A"}}>Add Additional OIPC Complaint</p>
                </div>
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