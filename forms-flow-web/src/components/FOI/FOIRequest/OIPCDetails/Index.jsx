import OIPCDetailsList from "./OIPCDetailsList";
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { makeStyles } from '@material-ui/styles';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCirclePlus } from '@fortawesome/free-solid-svg-icons';
import OIPCDetailsMinistry from "./OIPCDetailsMinistry";

const OIPCDetails = (props) => {
  const { oipcData, addOIPC, removeOIPC, updateOIPC, isMinistry } = props;

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
  
  return (
    <>  
    {isMinistry ? 
      <OIPCDetailsMinistry oipcData={oipcData}/> :
      <div className='request-accordian'>
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
    }
    </>
  );
}

export default OIPCDetails;