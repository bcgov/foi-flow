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
import { OIPublicationStatus, OIExemption } from "../types";
import { OIPublicationStatuses, OIExemptions } from "../../../../../helper/openinfo-helper";

const IAOOpenInfoMain = ({
  oiPublicationData,
  handleOIDataChange,
  isOIUser,
}: any) => {
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );
  const oiExemptions: OIExemption[] = useSelector(
    (state: any) => state.foiRequests.oiExemptions
  );

  const disableIAOField =
    oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.Publish || isOIUser;
  const disableOIField =
    oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.Publish || !isOIUser;

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
            EXEMPTION STATUS
          </Typography>
        </AccordionSummary>
        <AccordionDetails className={classes.accordionDetails}>
          <Grid container spacing={3}>
            <Grid item md={6}>
              <TextField
                fullWidth
                name="oipublicationstatus_id"
                label="Publication Status"
                variant="outlined"
                value={oiPublicationData?.oipublicationstatus_id || OIPublicationStatuses.Publish}
                select
                required
                InputLabelProps={{ shrink: true }}
                onChange={((event) => {
                  const selectedValue: number = parseInt(event.target.value);
                  if (selectedValue === OIPublicationStatuses.UnpublishRequest) return;
                  handleOIDataChange(event.target.value, event.target.name)
                })}
              >
                {oiPublicationStatuses.map((status) => {
                  return (
                    <MenuItem
                      style={status.oipublicationstatusid === OIPublicationStatuses.UnpublishRequest ? {
                        color: "grey", fontStyle: "italic", pointerEvents: "none" 
                      } : {}}
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
                label="Do Not Publish Reason"
                variant="outlined"
                value={oiPublicationData?.oiexemption_id || 0}
                select
                required={!isOIUser}
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                error={
                  oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish &&
                  !oiPublicationData?.oiexemption_id
                }
                disabled={oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.Publish}
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
                name="pagereference"
                variant="outlined"
                value={oiPublicationData?.pagereference}
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                required={!isOIUser}
                error={
                  oiPublicationData?.oipublicationstatus_id !== OIPublicationStatuses.Publish &&
                  oiPublicationData?.oiexemption_id !== OIExemptions.OutsideScopeOfPublication &&
                  !oiPublicationData?.pagereference
                }
                disabled={oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.Publish }
                multiline
                maxRows={2}
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
                  name="oiexemptionapproved"
                  disabled={disableOIField}
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(true, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.oiexemptionapproved === true}
                    />
                  }
                  label="Approved"
                />
                <FormControlLabel
                  value={false}
                  name="oiexemptionapproved"
                  disabled={disableOIField}
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(false, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.oiexemptionapproved === false}
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
              name="iaorationale"
              label="Analyst Rationale"
              InputLabelProps={{ shrink: true }}
              value={oiPublicationData?.iaorationale}
              required={!isOIUser}
              disabled={disableIAOField}
              error={
                oiPublicationData?.oipublicationstatus_id !== OIPublicationStatuses.Publish &&
                oiPublicationData?.oiexemption_id !== OIExemptions.OutsideScopeOfPublication &&
                !oiPublicationData?.iaorationale
              }
              style={{ paddingBottom: "2%" }}
              onChange={(event) =>
                handleOIDataChange(event.target.value, event.target.name)
              }
              multiline
              minRows={6}
            />
            <TextField
              fullWidth
              variant="outlined"
              name="oifeedback"
              label="OI Feedback"
              InputLabelProps={{ shrink: true }}
              value={oiPublicationData?.oifeedback}
              disabled={disableOIField}
              required={isOIUser}
              onChange={(event) =>
                handleOIDataChange(event.target.value, event.target.name)
              }
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
