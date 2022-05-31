import React from 'react';
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
import type { CFRFormData } from './types';
import { calculateFees } from './util';
import foiFees from '../../../../constants/FOI/foiFees.json';

export const CFRForm = (props: CFRFormData) => {

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

  const userGroups = props.userDetail.groups.map(group => group.slice(1));
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

  // let formData = JSON.parse(JSON.stringify(props));
  const [formData, setFormData] = React.useState(props);

  React.useEffect(() => {
    let newFormData: CFRFormData = calculateFees(formData);
    console.log("newFormData");
    console.log(newFormData);
    setFormData(newFormData);
    console.log("formData");
    console.log(formData);
  }, [formData]);

  const handleChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.name;
    const value = e.target.value;

    setFormData(values => ({...values, [name]: value}));
  };
  
  const handleEstimateChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    // console.log(formData);
    const estimates = formData.estimates;
    const newEstimates = {...estimates, [name]: value};
    // console.log(newEstimates);

    setFormData(values => ({...values, ["estimates"]: newEstimates}));
  };
  
  const handleActualChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    // console.log(formData);
    const actual = formData.actual;
    const newActual = {...actual, [name]: value};

    setFormData(values => ({...values, ["actual"]: newActual}));
  };


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
          <h3 className="foi-review-request-text">{formData?.requestNumber}</h3>
        </div>      
        <div className="col-3">
          <TextField
            id="cfrStatus"
            label={"CFR Status"}
            inputProps={{ "aria-labelledby": "cfrStatus-label"}}
            InputLabelProps={{ shrink: true }}
            select
            name="formStatus"
            value={formData?.formStatus || ""}
            onChange={handleChanges}
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
                  name="amountPaid"
                  value={formData?.amountPaid || ""}
                  onChange={handleChanges}
                  fullWidth
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
                  name="amountDue"
                  value={formData?.amountDue || ""}
                  onChange={handleChanges}
                  variant="outlined"
                  placeholder="0"
                  fullWidth
                  disabled={true}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-5 foi-details-col">
                <span className="formLabel">Balance Remaining</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{"$"+(formData?.amountDue - formData?.amountPaid)}</span>
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
                    step: foiFees.locating.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="locating"
                  value={formData?.estimates?.locating || ""}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.locating, foiFees.locating.unit)}
                  helperText={validateField(formData?.estimates?.locating, foiFees.locating.unit) &&
                    "Hours must be entered in increments of " + foiFees.locating.unit
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
                    step: foiFees.locating.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="locating"
                  value={formData?.actual?.locating || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(actualLocating, foiFees.locating.unit)}
                  helperText={validateField(actualLocating, foiFees.locating.unit) &&
                    "Hours must be entered in increments of " + foiFees.locating.unit
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
                    step: foiFees.producing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="producing"
                  value={formData?.estimates?.producing || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.producing, foiFees.producing.unit)}
                  helperText={validateField(formData?.estimates?.producing, foiFees.producing.unit) &&
                    "Hours must be entered in increments of " + foiFees.producing.unit
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
                    step: foiFees.producing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="producing"
                  value={formData?.actual?.producing || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.producing, foiFees.producing.unit)}
                  helperText={validateField(formData?.actual?.producing, foiFees.producing.unit) &&
                    "Hours must be entered in increments of " + foiFees.producing.unit
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
                    step: foiFees.preparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="preparing"
                  value={formData?.estimates?.preparing || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.preparing, foiFees.preparing.unit)}
                  helperText={validateField(formData?.estimates?.preparing, foiFees.preparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.preparing.unit
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
                    step: foiFees.preparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="preparing"
                  value={formData?.actual?.preparing || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.preparing, foiFees.preparing.unit)}
                  helperText={validateField(formData?.actual?.preparing, foiFees.preparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.preparing.unit
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
                    step: foiFees.electronicPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="electronicPages"
                  value={formData?.estimates?.electronicPages || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.electronicPages, foiFees.electronicPages.unit)}
                  helperText={validateField(formData?.estimates?.electronicPages, foiFees.electronicPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.electronicPages.unit
                  }
                  disabled={!isMinistry}
                >
                </TextField>
                <TextField
                  id="estimatedhardcopy"
                  label="Hardcopy Estimated Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: foiFees.hardcopyPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="electronicPages"
                  value={formData?.estimates?.electronicPages || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.electronicPages, foiFees.hardcopyPages.unit)}
                  helperText={validateField(formData?.actual?.electronicPages, foiFees.hardcopyPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.hardcopyPages.unit
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
                    step: foiFees.electronicPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="hardcopyPages"
                  value={formData?.actual?.electronicPages || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.electronicPages, foiFees.electronicPages.unit)}
                  helperText={validateField(formData?.actual?.electronicPages, foiFees.electronicPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.electronicPages.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
                />
                <TextField
                  id="actualhardcopy"
                  label="Hardcopy Actual Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: foiFees.hardcopyPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="hardcopyPages"
                  value={formData?.actual?.hardcopyPages || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.hardcopyPages, foiFees.hardcopyPages.unit)}
                  helperText={validateField(formData?.actual?.hardcopyPages, foiFees.hardcopyPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.hardcopyPages.unit
                  }
                  disabled={!isMinistry || cfrStatus !== 'approved'}
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
                  name="suggestions"
                  value={formData?.suggestions || ""}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }} 
                  onChange={handleChanges}
                  // error={requestDescriptionText===""}
                  fullWidth
                  disabled={!isMinistry}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className="col-lg-4 buttonContainer">
        <button
          className="btn saveButton"
          // onClick={saveCFRForm}
          color="primary"
        >
          Save
        </button>
      </div>
    </div>
  </div></Box>
  </div>
  );
}
