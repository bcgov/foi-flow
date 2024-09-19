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

const IAOOpenInfoMain = ({ oiPublicationData, handleOIDataChange }: any) => {
  //App State
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );
  const oiExemptions: OIExemption[] = useSelector(
    (state: any) => state.foiRequests.oiExemptions
  );

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
              <TextField
                fullWidth
                name="oipublicationstatusid"
                label="Publication Status"
                variant="outlined"
                value={
                  oiPublicationData
                    ? oiPublicationData.oipublicationstatusid
                    : 2
                }
                select
                required
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
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
                name="oiexemptionid"
                label="Do Not Publish Reason"
                variant="outlined"
                value={oiPublicationData ? oiPublicationData.oiexemptionid : 0}
                select
                required
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
                disabled={
                  !oiPublicationData ||
                  oiPublicationData?.oipublicationstatusid === 2
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
                name="pagereferences"
                variant="outlined"
                value={
                  oiPublicationData ? oiPublicationData.pageReferences : ""
                }
                required
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                // error={
                //   (!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""
                // }
                disabled={
                  !oiPublicationData ||
                  oiPublicationData?.oipublicationstatusid === 2
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
                  name="oiApproved"
                  disabled={
                    !oiPublicationData ||
                    oiPublicationData?.oipublicationstatusid === 2
                  }
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(true, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.oiApproved === true}
                    />
                  }
                  label="Approved"
                />
                <FormControlLabel
                  value={false}
                  name="oiApproved"
                  disabled={
                    !oiPublicationData ||
                    oiPublicationData?.oipublicationstatusid === 2
                  }
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(false, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.oiApproved === false}
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
              value={
                oiPublicationData ? oiPublicationData.analystrationale : null
              }
              disabled={
                !oiPublicationData ||
                oiPublicationData?.oipublicationstatusid === 2
              }
              style={{ paddingBottom: "2%" }}
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
              value={oiPublicationData ? oiPublicationData.oifeedback : null}
              disabled={
                !oiPublicationData ||
                oiPublicationData?.oipublicationstatusid === 2
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
