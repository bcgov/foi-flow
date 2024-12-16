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
import { formatDate } from "../../../../../helper/FOI/helper";

type OIPublicationStatus = {
  oipublicationstatusid: number;
  name: string;
  isactive: boolean;
};

const OpenInfoPublicationMain = ({
  oiPublicationData,
  isOIUser,
  currentOIRequestState,
  handleOIDataChange,
}: any) => {
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
  );

  console.log("oiPublicationData", oiPublicationData)

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
            PUBLICATION DETAILS
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
                value={oiPublicationData?.oipublicationstatus_id || 2}
                select
                required
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
              >
                {oiPublicationStatuses.map((status) => {
                  // if (status.oipublicationstatusid === 1) {
                  //   return null;
                  // }
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
                name="publicationdate"
                label="Publication Date"
                variant="outlined"
                disabled={["OI Review", "Exemption Request", "Do Not Publish", "Publication Review"].includes(currentOIRequestState)}
                InputLabelProps={{ shrink: true }}
                onChange={(event) =>
                  handleOIDataChange(event.target.value, event.target.name)
                }
                value={oiPublicationData?.publicationdate ? formatDate(new Date(oiPublicationData?.publicationdate)) : ""}
                type="date"
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
                  name="copyrightsevered"
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(true, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.copyrightsevered === true}
                    />
                  }
                  label="Copyright Severed"
                />
                <FormControlLabel
                  value={false}
                  name="copyrightsevered"
                  control={
                    <Radio
                      onChange={(event) =>
                        handleOIDataChange(false, event.target.name)
                      }
                      color="default"
                      checked={oiPublicationData?.copyrightsevered === false}
                    />
                  }
                  label="No Copyright"
                />
              </RadioGroup>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};

export default OpenInfoPublicationMain;
