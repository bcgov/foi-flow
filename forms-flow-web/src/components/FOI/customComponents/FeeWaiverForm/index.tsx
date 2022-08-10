import React, { useState } from 'react';
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
import type { params, FeeWaiverFormData } from './types';
import foiFees from '../../../../constants/FOI/foiFees.json';
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { returnToQueue } from '../../../FOI/FOIRequest/BottomButtonGroup/utils';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import { formatDate, addBusinessDays } from "../../../../helper/FOI/helper";

export const FeeWaiverForm = ({
  requestNumber,
  requestState,
  ministryId,
  requestId,
  userDetail,
  setCFRUnsaved
}: params) => {

  const dispatch = useDispatch();

  const userGroups = userDetail.groups.map(group => group.slice(1));
  const isMinistry = isMinistryLogin(userGroups);

  const CFRStatuses = [
    {
      value: 'init',
      label: 'Select CFR Form Status',
      disabled: true,
    },
    {
      value: 'review',
      label: 'In Review with IAO',
      disabled: false,
    },
    {
      value: 'clarification',
      label: 'Needs Clarification with Ministry',
      disabled: false
    },
    {
      value: 'approved',
      label: 'Approved',
      disabled: isMinistry,
    },
  ];

  React.useEffect(() => {
    if (ministryId) {
      fetchCFRForm(
        ministryId,
        dispatch,
      );
    }
  }, [ministryId]);

  const tooltipLocating = {
    "title": "Locating/Retrieving",
    "content": [
      <div className="toolTipContent">
        <strong>Areas to consider searching:</strong>
        <ul>
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
          <li>Includes gathering and providing records, not creating records</li>
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
    
    setFeeWaiverData(values => ({...values, [name]: value}));
  };

  const initialState: any = useSelector((state: any) => state.foiRequests.foiRequestCFRForm);

  const blankForm: FeeWaiverFormData = {
    "status": "iao",
    "formdata": {    
        "requesteddate": "2012-04-23T18:25:43.511Z",
        "receiveddate": "2012-04-23T18:25:43.511Z",
        "summary": "full text",
        "recordsdescription": "full text",
        "type": "public", // public or inability
        "inability": {
            "hasproof": false,
            "description": "full text"
        },
        "public": {
            "debate": false,
            "environment": false,
            "disclosing": false,
            "understanding": false,
            "newpolicy": false,
            "financing": false,
            "other": "free text",
            "analysis": "partial", //partial yes or no
            "description": "free text"

        },
        "disseminate": false,
        "abletodisseminate": false,
        "narrow": false,
        "exceed": false,
        "timelines": false,
        "previous": false,
        "recommendation": {
            "waive": "partial", //partial yes or no
            "summary": "free text",
            "amount": 0
        }
    }
  };

  const [initialFormData, setInitialFormData] = React.useState(blankForm);

  const [feeWaiverData, setFeeWaiverData] = React.useState(initialFormData);

  React.useEffect(() => {
    if (!_.isEqual(initialFormData, feeWaiverData)) {
      setCFRUnsaved(true);
    } else {
      setCFRUnsaved(false);
    }
  }, [initialFormData, feeWaiverData]);


  const save = () => {

  }; 


  const [modalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState(<></>);
  const handleSave = () => {
    setModalOpen(false);
    save();
  };
  const handleClose = () => {
    //setFeeWaiverData(values => ({...values, formStatus: initialFormData.formStatus}));
    setModalOpen(false);
  };

  const [feeWaiverRequested, setFeeWaiverRequested] = React.useState("");
  const [feeWaiverReceived, setFeeWaiverReceived] = React.useState("");

  const handleFeeWaiverRequestedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    //const requestedDate = formatDate(e.target.value);
    setFeeWaiverRequested(e.target.value);
    let receivedDateText = calculateFeeWaiverReceivedDate(e.target.value);
    setFeeWaiverReceived(receivedDateText ? formatDate(receivedDateText) : "");
    
  }

  const calculateFeeWaiverReceivedDate = (requestedDate : string) => {
    const dateString = requestedDate ? requestedDate.substring(0,10): "";
    return dateString? addBusinessDays(dateString, 20) : "";
   }   


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
    <div className="container foi-review-request-container cfrform-container">
      <div className="foi-request-review-header-row1">
        <div className="col-9 foi-request-number-header">
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>
        {/* <div className="col-3">
          <TextField
            id="feeWaiverFormStatus"
            label={"Form Status"}
            inputProps={{ "aria-labelledby": "feeWaiverFormStatus-label"}}
            InputLabelProps={{ shrink: true }}
            select
            name="feeWaiverFormStatus"
            value={formData?.formStatus}
            onChange={handleStatusChange}
            variant="outlined"
            fullWidth
            required
          >
            {CFRStatuses.map((option) => (
            <MenuItem
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </MenuItem>
            ))}
          </TextField>
        </div> */}
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">REQUEST DETAILS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                    id="feeWaiverRequested"
                    label="Fee Waiver Requested"
                    type="date" 
                    value={feeWaiverRequested || ''} 
                    onChange={handleFeeWaiverRequestedChange}
                    inputProps={{ "aria-labelledby": "feeWaiverRequested-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    InputProps={{inputProps: { max: formatDate(new Date())} }}
                    variant="outlined" 
                    required
                    error={feeWaiverRequested === undefined || feeWaiverRequested === ""}
                    fullWidth
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                    id="feeWaiverReceived"
                    label="Fee Waiver Received"
                    type="date" 
                    value={feeWaiverReceived || ''} 
                    //onChange={calculateFeeWaiverReceivedDate(feeWaiverReceived)}
                    inputProps={{ "aria-labelledby": "feeWaiverReceived-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    //InputProps={{inputProps: { min: feeWaiverReceived, max: formatDate(new Date())} }}
                    variant="outlined" 
                    required
                    error={feeWaiverReceived === undefined || feeWaiverReceived === ""}
                    fullWidth
                    disabled= {true}
                />
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                    <span className="formLabel">Request Description</span>
                </div>
              <div className="col-lg-4 foi-details-col">
                <span className="formLabel">Total Fees Due</span>
              </div>
              <div className="col-lg-2 foi-details-col">
                <span className="formLabel">{"$"}</span>
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">APPLICANTS REQUEST</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="summary"
                  label="Summary of Applicants Request to Waive Fee"
                  multiline
                  rows={4}
                  name="summary"
                  value={feeWaiverData?.formdata.summary}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
              <div className="col-lg-12 foi-details-col formLabel">
                    <span><b>Type of Fee Waiver requested by applicant?</b></span>
                    <span><i>Check 1 or more that apply and complete the applicable sections 2 or 3 below.</i></span>
              </div>
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-4">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        INABILITY TO PAY
                    </label>  
                </div>
                <div className="col-lg-4">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        PUBLIC INTEREST
                    </label> 
                </div> 
            </div>
             <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                    <TextField
                        id="recordsdescription"
                        label="Description of requested records"
                        multiline
                        rows={4}
                        name="recordsdescription"
                        value={feeWaiverData?.formdata.recordsdescription}
                        variant="outlined"
                        InputLabelProps={{ shrink: true, }}
                        onChange={handleTextChanges}
                        fullWidth
                    />
                </div>
                <div className="col-lg-12 foi-details-col">
                    <div className="formLabel"><i>
                    If provided by public body and relevant to the consideration of form 
                    (ie: volume, document types, content and/or format) 
                    </i>
                    </div>
                </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">INABILITY TO PAY</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Has the applicant provided documentary evidence of the inability to pay?*
                    (e.g.: bank statement, pay stub or tax return)?
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="description"
                  label="Describe evidence provided and whether it is sufficient"
                  multiline
                  rows={4}
                  name="description"
                  value={feeWaiverData?.formdata?.inability.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">PUBLIC INTEREST</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Has the subject of the records been a matter of recent public debate?*
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                Does the subject matter of the records relate directly to the environment, 
                public health, or safety?* 
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                 Could dissemination of the information in the records reasonably be expected to yield a public benefit by: *
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                Disclosing an environmental concern or a public health or safety concern?  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                Contributing to the development or public understanding of, or debate on, an
                important environmental or public health or safety issue? 
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                Contributing to public understanding of, or debate on, an important new policy, law, program,
                or service?
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                Do the records show how the public body is allocating financial or other resources? *
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="publicInterestDescription"
                  label="Other public interest considerations (if any)"
                  multiline
                  rows={4}
                  name="publicInterestDescription"
                  value={feeWaiverData?.formdata?.public.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-6 foi-details-col">
                Based on the analysis above, do the requested records relate to a matter 
                of public interest? *  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        PARTIALLY
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="publicInterestDescription"
                  label="Provide description of which records relate to a matter of public interest, partially."
                  multiline
                  rows={4}
                  name="publicInterestDescription"
                  value={feeWaiverData?.formdata?.public.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">EXCUSING PART OR FULL FEE</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Is the applicant's primary purpose for requesting records to disseminate information 
                    in a way that could reasonably be expected to benefit the public rather than serving
                    a private interest? 
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Is the applicant able to disseminate the information to the public? 
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">ANY OTHER REASON TO EXCUSE FEE</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Is there any other reason it is fair to excuse payment?  Factors to consider include: *  
                </div>
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Was the applicant willing to narrow the request for records to reduce the fee?    
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Do the costs of processing the applicant's FOI request exceed the fee estimate considerably
                    and, if so, is it reasonable to require the public body to bear some or all of those costs? 
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Have statutory timelines on the FOI file been met to date?     
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Have previous orders of the OIPC ruled that similar types of records or information should
                    or should not be subject to a fee?
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>  
                </div>
                <div className="col-lg-2">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="description"
                  label="Please describe reason here"
                  multiline
                  rows={4}
                  name="description"
                  value={feeWaiverData?.formdata?.inability.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">IAO ANALYST RECOMMENDATIONS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row label-text">
                <div className="col-lg-8 foi-details-col">
                    Select with Overall IAO Recommendations:*  
                </div>
            </div>
            <div className="row foi-details-row label-text">
                <div className="col-lg-12">
                    <label className='checkbox-style'>                  
                        <input
                        id="inabilityToPay"
                        type="checkbox"
                        className="checkmark"
                        checked={false}
                        />
                        <span className="checkmark"></span>
                        Waive Fee in Part
                    </label>  
                </div>
                <div className="col-lg-12">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        Waive Fee in Full
                    </label> 
                </div> 
                <div className="col-lg-12">
                    <label className='checkbox-style'>                  
                        <input
                        id="publicInterest"
                        type="checkbox"
                        className="checkmark"
                        checked={true}
                        />
                        <span className="checkmark"></span>
                        Do Not Waive Fee
                    </label> 
                </div> 
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="description"
                  label="Summarize Rational"
                  multiline
                  rows={4}
                  name="description"
                  value={feeWaiverData?.formdata?.inability.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleTextChanges}
                  fullWidth
                />
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">
                    <TextField
                    id="amounttobewaived"
                    label="Amount to be waived"
                    inputProps={{
                        "aria-labelledby": "amounttobewaived-label",
                        step: 0.01,
                        //max: formData.amountDue,
                        min: 0
                    }}
                    InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    name="amounttobewaived"
                    type="number"
                    value={feeWaiverData?.formdata?.recommendation.amount}
                    //onChange={handleAmountPaidChanges}
                    onBlur={(e) => {
                        e.target.value = parseFloat(e.target.value).toFixed(2);
                    }}
                    fullWidth
                    />
                </div>
                <div className="col-lg-6 foi-details-col">
                    <TextField
                        id="valueofamount"
                        label={"Value of amount"}
                        inputProps={{ "aria-labelledby": "valueofamount-label"}}
                        InputLabelProps={{ shrink: true }}
                        select
                        name="valueofamount"
                        value={feeWaiverData?.formdata?.recommendation.amount}
                        variant="outlined"
                        fullWidth
                        required
                    >
                    </TextField>
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
          //disabled={!validateFields()}
        >
          Save
        </button>
      </div>
    </div>
  </div></Box>

  <div className="state-change-dialog">
    <Dialog
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="state-change-dialog-title"
      aria-describedby="state-change-dialog-description"
      maxWidth={'md'}
      fullWidth={true}
      // id="state-change-dialog"
    >
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">CFR Form Status</h2>
          <IconButton className="title-col3" onClick={handleClose}>
            <i className="dialog-close-button">Close</i>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
      <DialogContent className={'dialog-content-nomargin'}>
        <DialogContentText id="state-change-dialog-description" component={'span'}>
        <span className="confirmation-message">
            {modalMessage}
          </span>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <button
          className={`btn-bottom btn-save btn`}
          onClick={handleSave}
        >
          Save Change
        </button>
        <button className="btn-bottom btn-cancel" onClick={handleClose}>
          Cancel
        </button>
      </DialogActions>
    </Dialog>
  </div>
  </div>
  );
}
