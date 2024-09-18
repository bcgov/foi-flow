import { useState } from "react";
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
type OITransactionObject = {
  oipublicationstatusid: number;
  oiexemptionid: number;
  oiApproved: boolean;
  pagereferences: "";
  analystrationale: "";
  oifeedback: "";
};

const IAOOpenInfoMain = ({ oiPublicaitionObj }: any) => {
  //App State
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );
  const oiExemptions: OIExemption[] = useSelector(
    (state: any) => state.foiRequests.oiExemptions
  );

  //Local State
  const [oiPublication, setOiPublication] = useState(oiPublicaitionObj);
  console.log("exemptions", oiExemptions);
  console.log("publicationstats", oiPublicationStatuses);

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
        margin: "10px 0 10px 0"
    }
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
              <TextField
                fullWidth
                label="Publication Status"
                variant="outlined"
                value={oiPublication ? oiPublication.oipublicationstatusid : 2}
                select
                required
                InputLabelProps={{ shrink: true }}
                // onChange={(event) => handlePublicationStatus(event.target.value)}
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
                // disabled={oipc.outcomeid && oipc.outcomeid !== 5}
              >
                {oiPublicationStatuses.map((status) => {
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
                label="Do Not Publish Reason"
                variant="outlined"
                value={oiPublication ? oiPublication.oiexemptionid : 0}
                select
                required
                InputLabelProps={{ shrink: true }}
                // onChange={(event) => handleOIPCNumber(event.target.value)}
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
                disabled={
                  !oiPublication || oiPublication?.oipublicationstatusid === 2
                }
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
            <Grid item md={6}>
              <TextField
                fullWidth
                label="Page References"
                variant="outlined"
                value={oiPublication ? oiPublication.pageReferences : ""}
                required
                InputLabelProps={{ shrink: true }}
                // onChange={(event) => handleOIPCNumber(event.target.value)}
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
                disabled={
                  !oiPublication || oiPublication?.oipublicationstatusid === 2
                }
              ></TextField>
            </Grid>
            <Grid item md={6}>
              <RadioGroup
                row
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
              >
                <FormControlLabel
                  value={true}
                  disabled={
                    !oiPublication || oiPublication?.oipublicationstatusid === 2
                  }
                  control={<Radio checked={oiPublication?.oiApproved} />}
                  label="Approved"
                />
                <FormControlLabel
                  value={false}
                  disabled={
                    !oiPublication || oiPublication?.oipublicationstatusid === 2
                  }
                  control={
                    <Radio
                      checked={
                        oiPublication !== null && !oiPublication?.oiApproved
                      }
                    />
                  }
                  label="Declined"
                />
              </RadioGroup>
            </Grid>
          </Grid>
          <div className="oi-main-text">
            <TextField
              fullWidth
              variant="outlined"
              label="Analyst Rationale"
              required
              InputLabelProps={{ shrink: true }}
              value={oiPublication ? oiPublication.analystrationale : null}
              disabled={
                !oiPublication || oiPublication?.oipublicationstatusid === 2
              }
              style={{paddingBottom: "2%"}}
              // onChange={(event) => handleOIPCNumber(event.target.value)}
              // error={
              //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
              // }
              multiline
              minRows={6}
            />
            <TextField
              fullWidth
              variant="outlined"
              label="OI Feedback"
              required
              InputLabelProps={{ shrink: true }}
              value={oiPublication ? oiPublication.oifeedback : null}
              disabled={
                !oiPublication || oiPublication?.oipublicationstatusid === 2
              }
              // onChange={(event) => handleOIPCNumber(event.target.value)}
              // error={
              //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
              // }
              multiline
              minRows={6}
            />
          </div>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};

export default IAOOpenInfoMain;
