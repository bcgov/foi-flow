import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import { InputAdornment, MenuItem, TextField } from '@mui/material';
import CustomizedTooltip from '../../Tooltip/MuiTooltip/Tooltip';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import foiFees from '../../../../../constants/FOI/foiFees.json';
import { StateEnum } from '../../../../../constants/FOI/statusEnum';
import { paymentMethods, calculateFees } from '../util';
import _ from 'lodash';
import '../index.scss'
import { CFRFormData } from '../types';

export const CFRFormTab = ({ 
  requestState,
  ministryId,
  formData,
  setFormData,
  isMinistry,
  requestNumber,
  userDetail,
  requestId,
  initialFormData,
  calculateBalanceRemaining,
  validateField,
  validateEstimatePaymentMethod,
  validateBalancePaymentMethod,
  setCFRUnsaved,
  handleTextChanges,
}: any) => {
  const handlePaymentMethodChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;
    setFormData((values:any) => ({...values, [name]: value}));
  };

  const handleAmountChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if (value <= Math.max(formData.actualTotalDue, formData.estimatedTotalDue)) {
      setFormData((values: any) => ({...values, [name]: value}));
    }
  };
    
  const handleAmountPaidChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if (value === 0) {
      setFormData((values: any) => ({...values, estimatePaymentMethod: 'init', balancePaymentMethod: 'init'}));
    } else if (formData.amountPaid === 0 && value > 0) {
      setFormData((values: any) => ({
        ...values,
        estimatePaymentMethod: initialFormData.estimatePaymentMethod,
        balancePaymentMethod: initialFormData.balancePaymentMethod
      }));
    }
    handleAmountChanges(e)
  };

  const handleEstimateChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    const estimates = formData.estimates;
    const newEstimates = {...estimates, [name]: value};
    let newFormData : CFRFormData = {
      ...formData, ["estimates"]: newEstimates,
      estimatedTotalDue: calculateFees(newEstimates)
    };
    setFormData(newFormData);
  };


  const handleActualChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: number = +e.target.value;

    const actual = formData.actual;
    const newActual = {...actual, [name]: value};
    let newFormData : CFRFormData = {
      ...formData,
      ["actual"]: newActual,
      actualTotalDue: calculateFees(newActual)
    };
    setFormData(newFormData);
  };

  const disableAmountPaid = () => {
    return (isMinistry || requestState === StateEnum.peerreview.name || requestState === StateEnum.peerreview.name|| requestState === StateEnum.feeassessed.name || formData?.formStatus !== 'approved' || ('balancePaymentMethod' in formData && formData?.balancePaymentMethod !== "init"))
  }
    
  const isFeeWaiverDisabled = () => {
    if(isMinistry || requestState === StateEnum.peerreview.name || (!isMinistry && (requestState !== StateEnum.onhold.name || formData?.formStatus !== 'approved')))
      return true;
    else
      return false;
  }

  const handleRefundChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if(value <= formData.amountPaid)
      setFormData((values: any) => ({...values, [name]: value}));
  };

  const cfrActualsDisabled = () => {
    return !isMinistry || formData?.formStatus !== 'approved' || requestState !== StateEnum.callforrecords.name || formData?.amountPaid === 0 || 
    requestState === StateEnum.peerreview.name;
  }
  const cfrEstimatedDisabled = () => {
    return !isMinistry || initialFormData?.formStatus === 'approved' || initialFormData?.formStatus === 'review' || requestState === StateEnum.peerreview.name;
  }

  const tooltipTotals = {
    "title": "Payment Details",
    "content": [
      <div className="toolTipContent">
        <p>The balance remaining for a fee estimate is the Estimated total subtracted by the amount paid.
          When actuals are entered, the balance remaining is the actual totals subtracted by the amount paid.
          If the balance is negative, then an applicant may be owed a refund.</p>
      </div>]
  };
  const tooltipLocating = {
    "title": "Locating/Retrieving",
    "content": [
      <div className="toolTipContent">
        <strong>Areas to consider searching:</strong>
        <ul>
          <li>Includes gathering and providing records, not creating records</li>
          <li>Outlook (including 'deleted' and 'sent' folders)</li>
          <li>Records management systems (ex. EDRMS)</li>
          <li>LAN, shared drives, SharePoint, databases</li>
          <li>Offsite records</li>
        </ul>
      </div>]
  };
  const tooltipProducing = {
    "title": "Producing",
    "content": [
      <div className="toolTipContent">
        <strong>Tasks include:</strong>
        <ul>
          <li>Identifying relevant sources of data/information</li>
          <li>Manual time spent creating and producing records</li>
          <li>Ex: generating a custom report from a database using existing data</li>
        </ul>
      </div>]
  };
  const tooltipPreparing = {
    "title": "Preparing",
    "content": [
      <div className="toolTipContent">
        <strong>Tasks include:</strong>
        <ul>
          <li>Converting records to PDF</li>
          <li>Consolidating records into a single PDF document</li>
          <li>Organizing records packages (e.g. by date department, staff, records type, etc.)</li>
          <li>Photocopying or scanning records into electronic format</li>
          <li>Ensuring completeness of responsive records</li>
          <li>Copying other types of media (audio and /or video)</li>
          <li>For electronic records, you do not need to provide a time estimate, please provide the number of files where requested below and IAO will be in a position to calculate the time required and to consider charging a fee.</li>
        </ul>
      </div>]
  };
  const tooltipVolume = {
    "title": "Volume",
    "content": [
      <div className="toolTipContent">
        <strong>Electronic:</strong>
        <ul>
          <li>Files (e.g. emails, Word Docs, Excel sheets, PDFs, photos, etc.)</li>
        </ul>
        <strong>Hardcopy:</strong>
        <ul>
          <li>Average file folder = 1" and holds approx. 200 pages (single-sided)</li>
          <li>1 standard Records Centre</li>
        </ul>
        <strong>Services box:</strong>
        <ul>
          <li>Legal sized folders = 1800 pages</li>
          <li>Letter sized folders = 2200 pages</li>
        </ul>
      </div>]
  };

  return (
    <>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="payment-details">
            <Typography className="heading">PAYMENT DETAILS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {!isMinistry && <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="estimatePaymentMethod"
                  label={"Estimate Payment Method"}
                  inputProps={{ "aria-labelledby": "estimatePaymentMethod-label"}}
                  InputLabelProps={{ shrink: true }}
                  select
                  name="estimatePaymentMethod"
                  value={formData?.estimatePaymentMethod}
                  onChange={handlePaymentMethodChanges}
                  variant="outlined"
                  fullWidth
                  required
                  disabled={requestState === StateEnum.peerreview.name|| initialFormData?.formStatus !== 'approved' || initialFormData?.amountPaid !== 0 || formData?.amountPaid === initialFormData?.amountPaid}
                  error={validateEstimatePaymentMethod()}
                  helperText={validateEstimatePaymentMethod() &&
                    "Estimate payment method must be specified if amount paid is manually added"
                  }
                >
                  {paymentMethods.map((option: any) => (
                  <MenuItem
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                  >
                    {option.label}
                  </MenuItem>
                  ))}
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="balancePaymentMethod"
                  label={"Balance Payment Method"}
                  inputProps={{ "aria-labelledby": "balancePaymentMethod-label"}}
                  InputLabelProps={{ shrink: true }}
                  select
                  name="balancePaymentMethod"
                  value={formData?.balancePaymentMethod}
                  onChange={handlePaymentMethodChanges}
                  variant="outlined"
                  fullWidth
                  required
                  disabled={requestState === StateEnum.peerreview.name|| initialFormData?.formStatus !== 'approved' || initialFormData?.amountPaid === 0 || formData?.amountPaid <= initialFormData?.amountPaid}
                  error={validateBalancePaymentMethod()}
                  helperText={validateBalancePaymentMethod() &&
                    "Balance payment method must be specified if amount paid is manually updated"
                  }
                >
                  {paymentMethods.map((option) => (
                  <MenuItem
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                  >
                    {option.label}
                  </MenuItem>
                  ))}
                </TextField>
              </div>
            </div>}
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="amountpaid"
                  label="Amount Paid"
                  inputProps={{
                    "aria-labelledby": "amountpaid-label",
                    step: 0.01,
                    max: Math.max(formData.estimatedTotalDue, formData.actualTotalDue),
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
                  disabled={disableAmountPaid()}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="balanceremaining"
                  label="Balance Remaining"
                  inputProps={{
                    "aria-labelledby": "balanceremaining-label"
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="balanceRemaining"
                  value={calculateBalanceRemaining().toFixed(2)}
                  variant="outlined"
                  placeholder="0"
                  fullWidth
                  disabled={true}
                />
              </div>
            </div>
            <div className="row cfr-fee-totals">
              <div className="col-lg-4 foi-details-col">
                <span className="formLabel">Estimated Total</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{`$${+(formData?.estimatedTotalDue || 0)?.toFixed(2) || 0}`}</span>
              </div>
              <div className="col-lg-4 foi-details-col">
                <span className="formLabel">Actual Total</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{`$${+(formData?.actualTotalDue || 0)?.toFixed(2) || 0}`}</span>
              </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="feewaiver"
                  label="Fee Waiver Amount"
                  inputProps={{
                    "aria-labelledby": "feewaiver-label",
                    step: 0.01,
                    max: Math.max(formData.estimatedTotalDue, formData.actualTotalDue),
                    min: 0
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  name="feewaiverAmount"
                  type="number"
                  value={formData?.feewaiverAmount}
                  onChange={handleAmountChanges}
                  onBlur={(e) => {
                    e.target.value = parseFloat(e.target.value).toFixed(2);
                  }}
                  fullWidth
                  disabled={isFeeWaiverDisabled()}
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="refund"
                  label="Refund Amount"
                  inputProps={{
                    "aria-labelledby": "refund-label",
                    step: 0.01,
                    max: formData.amountPaid,
                    min: 0
                  }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  variant="outlined"
                  name="refundAmount"
                  type="number"
                  value={formData?.refundAmount}
                  onChange={handleRefundChanges}
                  onBlur={(e) => {
                    e.target.value = parseFloat(e.target.value).toFixed(2);
                  }}
                  fullWidth
                  disabled={isMinistry || requestState === StateEnum.peerreview.name|| (!isMinistry && formData?.formStatus !== 'approved')}
                />
              </div>
            </div>
            <div className="cfrform-floatRight cfrform-totals">
              <CustomizedTooltip content={tooltipTotals} position={""} />
              <p className="hideContent" id="popup-6">Information6</p>
            </div>
          </AccordionDetails>
        </Accordion>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="overall-fee-estimate">
            <Typography className="heading">OVERALL FEES ESTIMATE</Typography>
          </AccordionSummary>
          <AccordionDetails>
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
                  disabled={cfrEstimatedDisabled()}
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
                  disabled={cfrActualsDisabled()}
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
                  disabled={cfrEstimatedDisabled()}
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
                  disabled={cfrActualsDisabled()}
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
              <div className="col-lg-3 foi-details-col">
                <TextField
                  id="estimatediaopreparing"
                  label="Estimated Hours IAO"
                  inputProps={{
                    "aria-labelledby": "estimatedpreparing-label",
                    step: foiFees.iaoPreparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="iaoPreparing"
                  value={formData?.estimates?.iaoPreparing}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.iaoPreparing, foiFees.iaoPreparing.unit)}
                  helperText={validateField(formData?.estimates?.iaoPreparing, foiFees.iaoPreparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.iaoPreparing.unit
                  }
                  disabled={isMinistry || requestState === StateEnum.peerreview.name || initialFormData?.formStatus !== 'review'}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-3 foi-details-col">
                <TextField
                  id="estimatedministrypreparing"
                  label="Estimated Hours Ministry"
                  inputProps={{
                    "aria-labelledby": "estimatedministrypreparing-label",
                    step: foiFees.ministryPreparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="ministryPreparing"
                  value={formData?.estimates?.ministryPreparing}
                  onChange={handleEstimateChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.estimates?.ministryPreparing, foiFees.ministryPreparing.unit)}
                  helperText={validateField(formData?.estimates?.ministryPreparing, foiFees.ministryPreparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.ministryPreparing.unit
                  }
                  disabled={cfrEstimatedDisabled()}
                >
                  {/* {menuItems} */}
                </TextField>
              </div>
              <div className="col-lg-3 foi-details-col">
                <TextField
                  id="actualiaopreparing"
                  label="Actual Hours IAO"
                  inputProps={{
                    "aria-labelledby": "actualiaopreparing-label",
                    step: foiFees.iaoPreparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="iaoPreparing"
                  value={formData?.actual?.iaoPreparing}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.iaoPreparing, foiFees.iaoPreparing.unit)}
                  helperText={validateField(formData?.actual?.iaoPreparing, foiFees.iaoPreparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.iaoPreparing.unit
                  }
                  disabled={isMinistry || requestState === StateEnum.peerreview.name || formData?.formStatus !== 'approved'
                  || (requestState !== StateEnum.deduplication.name && requestState !== StateEnum.review.name)}
                />
              </div>
              <div className="col-lg-3 foi-details-col">
                <TextField
                  id="actualministrypreparing"
                  label="Actual Hours Ministry"
                  inputProps={{
                    "aria-labelledby": "actualministrypreparing-label",
                    step: foiFees.ministryPreparing.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hr(s)</InputAdornment>
                  }}
                  InputLabelProps={{ shrink: true }}
                  name="ministryPreparing"
                  value={formData?.actual?.ministryPreparing}
                  onChange={handleActualChanges}
                  variant="outlined"
                  fullWidth
                  type="number"
                  error={validateField(formData?.actual?.ministryPreparing, foiFees.ministryPreparing.unit)}
                  helperText={validateField(formData?.actual?.ministryPreparing, foiFees.ministryPreparing.unit) &&
                    "Hours must be entered in increments of " + foiFees.ministryPreparing.unit
                  }
                  disabled={cfrActualsDisabled()}
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
                  label="Electronic Estimated Files"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: foiFees.electronicPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">file(s)</InputAdornment>
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
                  disabled={cfrEstimatedDisabled()}
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
                  disabled={cfrEstimatedDisabled()}
                >
                </TextField>
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                  id="actualelectronic"
                  label="Electronic Actual Files"
                  inputProps={{
                    "aria-labelledby": "estimatedelectronic-label",
                    step: foiFees.electronicPages.unit,
                    min: 0,
                  }}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">file(s)</InputAdornment>
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
                  disabled={cfrActualsDisabled()}
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
                  disabled={cfrActualsDisabled()}
                />
              </div>
            </div>

            <div className="cfrform-floatRight cfrform-locating">
              <CustomizedTooltip content={tooltipLocating} position={""} />
              <p className="hideContent" id="popup-1">Information1</p>
            </div>
            <div className="cfrform-floatRightRight cfrform-locating">
              <p className="hideContent" id="popup-5">Information5</p>
            </div>
            <div className="cfrform-floatRight cfrform-producing">
              <CustomizedTooltip content={tooltipProducing} position={""} />
              <p className="hideContent" id="popup-2">Information2</p>
            </div>
            <div className="cfrform-floatRight cfrform-preparing">
              <CustomizedTooltip content={tooltipPreparing} position={""} />
              <p className="hideContent" id="popup-3">Information3</p>
            </div>
            <div className="cfrform-floatRight cfrform-volume">
              <CustomizedTooltip content={tooltipVolume} position={""} />
              <p className="hideContent" id="popup-4">Information4</p>
            </div>

          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="clarification-suggestions">
            <Typography className="heading">OVERALL CLARIFICATION SUGGESTIONS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="combinedsuggestions"
                  label="Combined suggestions for futher clarifications"
                  multiline
                  rows={4}
                  name="suggestions"
                  value={formData?.suggestions}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                  disabled={cfrEstimatedDisabled()}
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    </>
  )
}