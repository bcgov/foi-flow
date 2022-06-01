import React from 'react';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import './index.scss'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';
import type { CFRFormData } from './types';
import { calculateFees } from './util';

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

  // let formData = JSON.parse(JSON.stringify(props));
  const [formData, setFormData] = React.useState(props);

  const handleTextChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;

    setFormData(values => ({...values, [name]: value}));
  };

  const handleAmountChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : number = +e.target.value;

    setFormData(values => ({...values, [name]: value}));
  };
  
  const handleEstimateChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    const estimates = formData.estimates;
    const newEstimates = {...estimates, [name]: value};
    let newFormData : CFRFormData = {...formData, ["estimates"]: newEstimates};
    newFormData = calculateFees(newFormData);
    setFormData(newFormData);
  };
  
  const handleActualChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    const actual = formData.actual;
    const newActual = {...actual, [name]: value};
    let newFormData : CFRFormData = {...formData, ["actual"]: newActual};
    newFormData = calculateFees(newFormData);
    setFormData(newFormData);
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
            onChange={handleTextChanges}
            variant="outlined"
            fullWidth
            required
            // disabled={disableInput}
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
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  placeholder="hr"
                  name="amountPaid"
                  value={formData?.amountPaid || ""}
                  onChange={handleAmountChanges}
                  fullWidth
                  // required={true}
                  // disabled={disableInput}
                  // error={applicantFirstNameText === ""}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="totalamountdue"
                  label="Total Amount Due"
                  inputProps={{ "aria-labelledby": "totalamountdue-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="amountDue"
                  value={formData?.amountDue || ""}
                  onChange={handleAmountChanges}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-4 foi-details-col">
                <span className="formLabel">Balance Remaining</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{"$"+(formData?.amountDue - formData?.amountPaid > 0 ? formData?.amountDue - formData?.amountPaid : "00.00")}</span>
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
                  inputProps={{ "aria-labelledby": "estimatedlocating-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="locating"
                  value={formData?.estimates?.locating || ""}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // required={true}
                  // disabled={disableInput}
                  // error={applicantLastNameText === ""}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actuallocating"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actuallocating-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="locating"
                  value={formData?.actual?.locating || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
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
                  inputProps={{ "aria-labelledby": "estimatedproducing-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="producing"
                  value={formData?.estimates?.producing || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualproducing"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actualproducing-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="producing"
                  value={formData?.actual?.producing || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
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
                  inputProps={{ "aria-labelledby": "estimatedpreparing-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="preparing"
                  value={formData?.estimates?.preparing || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualpreparing"
                  label="Actual Hours"
                  inputProps={{ "aria-labelledby": "actualpreparing-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="preparing"
                  value={formData?.actual?.preparing || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  placeholder="hr"
                  fullWidth
                  // disabled={disableInput}
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
                  inputProps={{ "aria-labelledby": "estimatedelectronic-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="electronicPages"
                  value={formData?.estimates?.electronicPages || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
                <TextField
                  id="estimatedhardcopy"
                  label="Hardcopy Estimated Pages"
                  inputProps={{ "aria-labelledby": "estimatedhardcopy-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="hardcopyPages"
                  value={formData?.estimates?.hardcopyPages || ""}
                  onChange={handleEstimateChanges}
                  // input={<Input />}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // required
                  // disabled={disableInput || disableFieldForMinistryRequest}
                  // error={selectedCategory.toLowerCase().includes("select")}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualelectronic"
                  label="Electronic Actual Pages"
                  inputProps={{ "aria-labelledby": "actualelectronic-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="electronicPages"
                  value={formData?.actual?.electronicPages || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // disabled={disableInput}
                />
                <TextField
                  id="actualhardcopy"
                  label="Hardcopy Actual Pages"
                  inputProps={{ "aria-labelledby": "actualhardcopy-label"}}
                  InputLabelProps={{ shrink: true }}
                  name="hardcopyPages"
                  value={formData?.actual?.hardcopyPages || ""}
                  onChange={handleActualChanges}
                  variant="outlined"
                  placeholder="pgs"
                  fullWidth
                  // disabled={disableInput}
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
                  onChange={handleTextChanges}
                  // error={requestDescriptionText===""}
                  fullWidth
                  // disabled={disableInput}
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
