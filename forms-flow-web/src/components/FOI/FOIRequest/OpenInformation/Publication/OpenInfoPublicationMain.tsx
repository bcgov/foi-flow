import {
  Grid,
  TextField,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Typography,
  MenuItem,
  Radio,
  RadioGroup,
  FormControlLabel,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { makeStyles } from "@material-ui/styles";
import { useSelector } from "react-redux";
// import { useState, useEffect } from "react";

type OIPublicationStatus = {
  oipublicationstatusid: number;
  name: string;
  isactive: boolean;
};
type OIExemption = {
  oiexemptionid: number;
  name: string;
  isactive: boolean;
};

const OpenInfoPublicationMain = ({
  oiPublicationData,
  isOIUser,
}: any) => {
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );
  const oiExemptions: OIExemption[] = useSelector(
    (state: any) => state.foiRequests.oiExemptions
  );

  // let foiOITransactionData = useSelector(
  //   (state: any) => state.foiRequests.foiOpenInfoRequest
  // );

  // const [oiPublicationData, setOiPublicationData] = useState(foiOITransactionData);

  // useEffect(() => {
  //   setOiPublicationData(foiOITransactionData);
  // }, [foiOITransactionData, oiPublicationStatuses, oiExemptions]);

//   const disableIAOField =
//     oiPublicationData?.oipublicationstatus_id === 2 || isOIUser;
//   const disableOIField =
//     oiPublicationData?.oipublicationstatus_id === 2 || !isOIUser;

  //Styling
  const useStyles = makeStyles({
    heading: {
      color: "#FFF",
      fontSize: "16px !important",
      fontWeight: "bold",
    },
    accordionSummary: {
      flexDirection: "row-reverse",
    },
    accordionDetails: {
      margin: "10px 0 10px 0",
    },
  });
  const classes = useStyles();

  return (
    <div className="request-accordian">
      <Accordion defaultExpanded={true}>
        <AccordionSummary
          className={classes.accordionSummary}
          expandIcon={<ExpandMoreIcon />}
        >
          <Typography className={classes.heading}>
            PUBLICATION STATUS
          </Typography>
        </AccordionSummary>
        <AccordionDetails className={classes.accordionDetails}>
          <Grid container spacing={3}>
            <Grid item md={6}>
              {/* <div>{oiPublicationData?.oipublicationstatus_id}</div> */}
              <TextField
                fullWidth
                name="oipublicationstatus_id"
                label="Publication Status"
                variant="outlined"
                value={oiPublicationData?.oipublicationstatus_id || 2}
                select
                required
                InputLabelProps={{ shrink: true }}
                // onChange={(event) =>
                //   handleOIDataChange(event.target.value, event.target.name)
                // }
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
              >
                {oiPublicationStatuses.map((status) => {
                  if (status.oipublicationstatusid === 3) {
                    return null;
                  }
                  return (
                    <MenuItem
                      key={status.oipublicationstatusid}
                      value={status.oipublicationstatusid}
                    >
                      {status.name}
                    </MenuItem>
                  );
                })}
              </TextField>
            </Grid>
            <Grid item md={6}>
              <TextField
                fullWidth
                name="oiexemption_id"
                label="Publication Date"
                variant="outlined"
                value={oiPublicationData?.oiexemption_id || 0}
                select
                required={!isOIUser}
                InputLabelProps={{ shrink: true }}
                // onChange={(event) =>
                //   handleOIDataChange(event.target.value, event.target.name)
                // }
                // error={
                //   oiPublicationData?.oipublicationstatus_id !== 2 &&
                //   !oiPublicationData?.oiexemption_id
                // }
                // disabled={disableIAOField}
              >
                {oiExemptions.map((reason) => {
                  return (
                    <MenuItem
                      key={reason.oiexemptionid}
                      value={reason.oiexemptionid}
                    >
                      {reason.name}
                    </MenuItem>
                  );
                })}
              </TextField>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};

export default OpenInfoPublicationMain;
