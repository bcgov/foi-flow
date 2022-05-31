import TextField from '@mui/material/TextField';
import InputAdornment from "@mui/material/InputAdornment";
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';
import { useState } from 'react';
import { isMinistryLogin } from "../../../../helper/FOI/helper";

type CFRForm = {
  requestNumber: string;
  userDetail: {
    groups: string[];
  };
}

export const CFRForm = ({
  requestNumber,
  userDetail
}: CFRForm) => {

  const CFRStatuses = [
    {
      value: 'review',
      label: 'In Review'
    },
    {
      value: 'approved',
      label: 'Approved'
    },
    {
      value: 'clarification',
      label: 'Clarification'
    },
  ];

  const userGroups = userDetail.groups.map(group => group.slice(1));
  const isMinistry = isMinistryLogin(userGroups);

  const [cfrStatus, setCfrStatus] = useState('review');

  const [estimatedLocating, setEstimatedLocating] = useState(0)
  const [estimatedProducing, setEstimatedProducing] = useState(0)
  const [estimatedPreparing, setEstimatedPreparing] = useState(0)
  const [estimatedElectronic, setEstimatedElectronic] = useState(0)
  const [estimatedHardcopy, setEstimatedHardcopy] = useState(0)
  const [actualLocating, setActualLocating] = useState(0)
  const [actualProducing, setActualProducing] = useState(0)
  const [actualPreparing, setActualPreparing] = useState(0)
  const [actualElectronic, setActualElectronic] = useState(0)
  const [actualHardcopy, setActualHardcopy] = useState(0)

  // temp code, remove when integrated with back end
  const handleCFRStatusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCfrStatus(e.target.value);
  };

  const validateField = (value: number, step:number) => {
    return (value % step) !== 0;
  }

  const fees = require('../../../../constants/FOI/foiFees.json');

  return (
    <div className="foi-review-container">
    <Box
      component="form"
      sx={{
        '& .MuiTextField-root': { m: 1 },
      }}
      autoComplete="off"
    ><div className="foi-request-form">
    <div style={{marginTop: 20}}></div>
    <div className="container foi-review-request-container">
      <div className="foi-request-review-header-row1">
        <div className="col-9 foi-request-number-header">
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>
        <div className="col-3">
          <TextField
            id="cfrStatus"
            label={"CFR Status"}
            inputProps={{ "aria-labelledby": "cfrStatus-label"}}
            InputLabelProps={{ shrink: true }}
            select
            value={cfrStatus}
            onChange={handleCFRStatusChange}
            variant="outlined"
            fullWidth
            required
            // disabled={isMinistry} comment back in when back end is intergrated
            // error={selectedAssignedTo.toLowerCase().includes("unassigned")}
          >
            {CFRStatuses.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
            ))}
          </TextField>
        </div>


      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">OVERALL FEES ESTIMATE</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="amountpaid"
                  label="Amount Paid"
                  inputProps={{ "aria-labelledby": "amountpaid-label"}}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  placeholder="0"
                  // value={applicantFirstNameText}
                  fullWidth
                  // onChange={handleFirtNameChange}
                  // required={true}
                  // error={applicantFirstNameText === ""}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="totalamountdue"
                  label="Total Amount Due"
                  inputProps={{ "aria-labelledby": "totalamountdue-label"}}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  // value={applicantMiddleNameText}
                  variant="outlined"
                  placeholder="0"
                  fullWidth
                  disabled={true}
                  // onChange={handleMiddleNameChange}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-5 foi-details-col">
                <span className="formLabel">Balance Remaining</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">$00.00</span>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <hr />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">Locating/Retrieving - this includes searching all relevant sources.</div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedlocating"
                  label="Estimated Hours"
                  inputProps={{
                    "aria-labelledby": "estimatedlocating-label",
                    step: fees.locating.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={estimatedLocating}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEstimatedLocating(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(estimatedLocating, fees.locating.unit)}
                  helperText={validateField(estimatedLocating, fees.locating.unit) &&
                    "Hours must be entered in increments of " + fees.locating.unit
                  }
                  disabled={!isMinistry}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actuallocating"
                  label="Actual Hours"
                  inputProps={{
                    "aria-labelledby": "actuallocating-label",
                    step: fees.locating.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={actualLocating}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setActualLocating(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(actualLocating, fees.locating.unit)}
                  helperText={validateField(actualLocating, fees.locating.unit) &&
                    "Hours must be entered in increments of " + fees.locating.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Producing - this only applies where you are creating records from other sources* (e.g. developing a program to create new records from a database)
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedproducing"
                  label="Estimated Hours"
                  inputProps={{
                    "aria-labelledby": "estimatedproducing-label",
                    step: fees.producing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={estimatedProducing}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEstimatedProducing(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(estimatedProducing, fees.producing.unit)}
                  helperText={validateField(estimatedProducing, fees.producing.unit) &&
                    "Hours must be entered in increments of " + fees.producing.unit
                  }
                  disabled={!isMinistry}
                >
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualproducing"
                  label="Actual Hours"
                  inputProps={{
                    "aria-labelledby": "actualproducing-label",
                    step: fees.producing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={actualProducing}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setActualProducing(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(actualProducing, fees.producing.unit)}
                  helperText={validateField(actualProducing, fees.producing.unit) &&
                    "Hours must be entered in increments of " + fees.producing.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Preparing - this may include time spent by IAO (for electronic records) or the Ministry (for hardcopy records)
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedpreparing"
                  label="Estimated Hours"
                  inputProps={{
                    "aria-labelledby": "estimatedpreparing-label",
                    step: fees.preparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={estimatedPreparing}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEstimatedPreparing(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(estimatedPreparing, fees.preparing.unit)}
                  helperText={validateField(estimatedPreparing, fees.preparing.unit) &&
                    "Hours must be entered in increments of " + fees.preparing.unit
                  }
                  disabled={!isMinistry}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualpreparing"
                  label="Actual Hours"
                  inputProps={{
                    "aria-labelledby": "actualpreparing-label",
                    step: fees.preparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={actualPreparing}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setActualPreparing(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(actualPreparing, fees.preparing.unit)}
                  helperText={validateField(actualPreparing, fees.preparing.unit) &&
                    "Hours must be entered in increments of " + fees.preparing.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="formLabel">
                  Volume - for electronic records please provide the estimated number of files and for hardcopy records please continue to provide the number of pages
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatedelectronic"
                  label="Electronic Estimated Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: fees.electronicpages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={estimatedElectronic}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEstimatedElectronic(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(estimatedElectronic, fees.electronicpages.unit)}
                  helperText={validateField(estimatedElectronic, fees.electronicpages.unit) &&
                    "Pages must be entered in increments of " + fees.electronicpages.unit
                  }
                  disabled={!isMinistry}
                >
                </TextField>
                <TextField
                  id="estimatedhardcopy"
                  label="Hardcopy Estimated Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: fees.hardcopypages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={estimatedHardcopy}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setEstimatedHardcopy(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(estimatedHardcopy, fees.hardcopypages.unit)}
                  helperText={validateField(estimatedHardcopy, fees.hardcopypages.unit) &&
                    "Pages must be entered in increments of " + fees.hardcopypages.unit
                  }
                  disabled={!isMinistry}
                >
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualelectronic"
                  label="Electronic Actual Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: fees.electronicpages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={actualElectronic}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setActualElectronic(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(actualElectronic, fees.electronicpages.unit)}
                  helperText={validateField(actualElectronic, fees.electronicpages.unit) &&
                    "Pages must be entered in increments of " + fees.electronicpages.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                />
                <TextField
                  id="actualhardcopy"
                  label="Hardcopy Actual Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: fees.hardcopypages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  value={actualHardcopy}
                  variant="outlined"
                  fullWidth
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    setActualHardcopy(parseFloat(e.target.value))
                  }}
                  type="number"
                  error={validateField(actualHardcopy, fees.hardcopypages.unit)}
                  helperText={validateField(actualHardcopy, fees.hardcopypages.unit) &&
                    "Pages must be entered in increments of " + fees.hardcopypages.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                  // onChange={handleOrganizationChange}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">OVERALL CLARIFICATION SUGGESTIONS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="combinedsuggestions"
                  // required={true}
                  label="Combined suggestions for futher clarifications   "
                  multiline
                  rows={4}
                  // value={requestDescriptionText}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  // onChange={handleRequestDescriptionChange}
                  // error={requestDescriptionText===""}
                  fullWidth
                  disabled={!isMinistry}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    </div>
  </div></Box>
  </div>
  );
}
