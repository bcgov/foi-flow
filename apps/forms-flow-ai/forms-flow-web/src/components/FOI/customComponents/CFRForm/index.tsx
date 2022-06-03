import React from 'react';
import { useDispatch, useSelector } from "react-redux";
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
import { errorToast, isMinistryLogin } from "../../../../helper/FOI/helper";
import type { params, CFRFormData } from './types';
import { calculateFees } from './util';
import foiFees from '../../../../constants/FOI/foiFees.json';
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { valueToPercent } from '@mui/base';

export const CFRForm = ({
  requestNumber,
  ministryId,
  userDetail
}: params) => {

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

  const dispatch = useDispatch();

  const userGroups = userDetail.groups.map(group => group.slice(1));
  const isMinistry = isMinistryLogin(userGroups);

  React.useEffect(() => {
    if (ministryId) {
      fetchCFRForm(
        ministryId,
        dispatch,
      );
    }
  }, [ministryId]);

    const handleTextChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;

    setFormData(values => ({...values, [name]: value}));
  };

  const initialState: any = useSelector((state: any) => {
    return state.foiRequests.foiRequestCFRForm;
  });

  const [initialFormData, setInitialFormData] = React.useState({ 
    formStatus: '',
    amountDue: 0,
    amountPaid: 0,
    estimates: {
      locating: 0,
      producing: 0,
      preparing: 0,
      electronicPages: 0,
      hardcopyPages: 0
    },
    actual: {
      locating: 0,
      producing: 0,
      preparing: 0,
      electronicPages: 0,
      hardcopyPages: 0
    },
    suggestions: ''
  });
  
  const [formData, setFormData] = React.useState(initialFormData);

  React.useEffect(() => {
    var formattedData = {
      formStatus: initialState.status,
      amountDue: initialState.feedata.totalamountdue,
      amountPaid: initialState.feedata.amountpaid,
      estimates: {
        locating: initialState.feedata.estimatedlocatinghrs,
        producing: initialState.feedata.estimatedproducinghrs,
        preparing: initialState.feedata.estimatedpreparinghrs,
        electronicPages: initialState.feedata.estimatedelectronicpages,
        hardcopyPages: initialState.feedata.estimatedhardcopypages,
      },
      actual: {
        locating: initialState.feedata.actuallocatinghrs,
        producing: initialState.feedata.actualproducinghrs,
        preparing: initialState.feedata.actualpreparinghrs,
        electronicPages: initialState.feedata.actualelectronicpages,
        hardcopyPages: initialState.feedata.estimatedhardcopypages,
      },
      suggestions: initialState.overallsuggestions
    };
    setInitialFormData(formattedData)
    setFormData(formattedData);
  }, [initialState]);

  const validateField = (value: number, step: number) => {
    return (value % step) !== 0;
  }

  const validateFields = () => {
    var field: keyof typeof formData.estimates;
    for (field in formData.estimates) {
      if (validateField(formData.estimates[field], foiFees[field].unit)) {
        return false;
      }
    }
    var afield: keyof typeof formData.actual
    for (afield in formData.actual) {
      if (validateField(formData.estimates[afield], foiFees[afield].unit)) {
        return false;
      }
    }
    var retval = !_.isEqual(initialFormData, formData);
    return retval
  }

  const handleAmountPaidChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : number = Math.floor((+e.target.value) * 100) / 100;
    if (value <= formData.amountDue) {
      setFormData(values => ({...values, [name]: value}));
    }
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

  const save = () => {
    var callback = (_res: string) => {
      setInitialFormData(formData)
      toast.success("The request has been saved successfully.", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    };

    saveCFRForm(
      {
        feedata:{
          amountpaid: formData.amountPaid,
          totalamountdue: formData.amountDue,
          estimatedlocatinghrs: formData.estimates.locating,
          actuallocatinghrs: formData.actual.locating,
          estimatedproducinghrs: formData.estimates.producing,
          actualproducinghrs: formData.actual.producing,
          estimatedpreparinghrs: formData.estimates.preparing,
          actualpreparinghrs: formData.actual.preparing,
          estimatedelectronicpages: formData.estimates.electronicPages,
          actualelectronicpages: formData.actual.electronicPages,
          estimatedhardcopypages: formData.estimates.hardcopyPages,
          actualhardcopypages: formData.actual.hardcopyPages,
        },
        overallsuggestions: formData.suggestions,
        status: formData.formStatus
      },
      ministryId,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage)
      },
    )
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
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>
        <div className="col-3">
          <TextField
            id="cfrStatus"
            label={"CFR Status"}
            inputProps={{ "aria-labelledby": "cfrStatus-label"}}
            InputLabelProps={{ shrink: true }}
            select
            name="formStatus"
            value={formData?.formStatus}
            onChange={handleTextChanges}
            variant="outlined"
            fullWidth
            required
            disabled={isMinistry}
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
                  inputProps={{
                    "aria-labelledby": "amountpaid-label",
                    step: 0.01,
                    max: formData.amountDue,
                    min: 0
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  name="amountPaid"
                  type="number"
                  value={formData?.amountPaid}
                  onChange={handleAmountPaidChanges}
                  onBlur={(e) => {
                    e.target.value = parseFloat(e.target.value).toFixed(2);
                  }}
                  fullWidth
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="amountdue"
                  label="Total Amount Due"
                  inputProps={{
                    "aria-labelledby": "amountdue-label"
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="amountDue"
                  value={formData?.amountDue.toFixed(2)}
                  onChange={handleAmountChanges}
                  variant="outlined"
                  placeholder="0"
                  fullWidth
                  disabled={true}
                />
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-4 foi-details-col">
                <span className="formLabel">Balance Remaining</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{"$"+(formData?.amountDue - formData?.amountPaid).toFixed(2)}</span>
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
                  value={formData?.estimates?.locating}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.locating, foiFees.locating.unit)}
                  helperText={validateField(formData?.estimates?.locating, foiFees.locating.unit) &&
                    "Hours must be entered in increments of " + foiFees.locating.unit
                  }
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
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
                  value={formData?.actual?.locating}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.locating, foiFees.locating.unit)}
                  helperText={validateField(formData?.actual?.locating, foiFees.locating.unit) &&
                    "Hours must be entered in increments of " + foiFees.locating.unit
                  }
                  disabled={!isMinistry || formData?.formStatus !== 'approved'}
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
                  value={formData?.estimates?.producing}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.producing, foiFees.producing.unit)}
                  helperText={validateField(formData?.estimates?.producing, foiFees.producing.unit) &&
                    "Hours must be entered in increments of " + foiFees.producing.unit
                  }
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
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
                  value={formData?.actual?.producing}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.producing, foiFees.producing.unit)}
                  helperText={validateField(formData?.actual?.producing, foiFees.producing.unit) &&
                    "Hours must be entered in increments of " + foiFees.producing.unit
                  }
                  disabled={!isMinistry || formData?.formStatus !== 'approved'}
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
                  value={formData?.estimates?.preparing}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.preparing, foiFees.preparing.unit)}
                  helperText={validateField(formData?.estimates?.preparing, foiFees.preparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.preparing.unit
                  }
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
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
                  value={formData?.actual?.preparing}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.preparing, foiFees.preparing.unit)}
                  helperText={validateField(formData?.actual?.preparing, foiFees.preparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.preparing.unit
                  }
                  disabled={!isMinistry || formData?.formStatus !== 'approved'}
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
                  value={formData?.estimates?.electronicPages}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.electronicPages, foiFees.electronicPages.unit)}
                  helperText={validateField(formData?.estimates?.electronicPages, foiFees.electronicPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.electronicPages.unit
                  }
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
                >
                </TextField>
                <TextField
                  id="estimatedhardcopy"
                  label="Hardcopy Estimated Pages"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: foiFees.hardcopyPages.unit,
                    min: 0,
                    pattern: "^([1-9]+|0{1})(?:\.\d{1,2})?$"
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">pg(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="hardcopyPages"
                  value={formData?.estimates?.hardcopyPages}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.hardcopyPages, foiFees.hardcopyPages.unit)}
                  helperText={validateField(formData?.estimates?.hardcopyPages, foiFees.hardcopyPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.hardcopyPages.unit
                  }
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
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
                  name="electronicPages"
                  value={formData?.actual?.electronicPages}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.electronicPages, foiFees.electronicPages.unit)}
                  helperText={validateField(formData?.actual?.electronicPages, foiFees.electronicPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.electronicPages.unit
                  }
                  disabled={!isMinistry || formData?.formStatus !== 'approved'}
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
                  value={formData?.actual?.hardcopyPages}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.hardcopyPages, foiFees.hardcopyPages.unit)}
                  helperText={validateField(formData?.actual?.hardcopyPages, foiFees.hardcopyPages.unit) &&
                    "Pages must be entered in increments of " + foiFees.hardcopyPages.unit
                  }
                  disabled={!isMinistry || formData?.formStatus !== 'approved'}
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
                  label="Combined suggestions for futher clarifications   "
                  multiline
                  rows={4}
                  name="suggestions"
                  value={formData?.suggestions}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                  disabled={!isMinistry || formData?.formStatus === 'approved'}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className="col-lg-4 buttonContainer">
        <button
          type="button"
          className="btn saveButton"
          onClick={save}
          color="primary"
          disabled={!validateFields()}
        >
          Save
        </button>
      </div>
    </div>
  </div></Box>
  </div>
  );
}
