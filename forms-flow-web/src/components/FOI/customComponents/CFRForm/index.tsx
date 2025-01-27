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
import Chip from '@mui/material/Chip';
import { errorToast, isMinistryLogin } from "../../../../helper/FOI/helper";
import type { params, CFRFormData } from './types';
import { calculateFees, paymentMethods } from './util';
import foiFees from '../../../../constants/FOI/foiFees.json';
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { returnToQueue } from '../../../FOI/FOIRequest/BottomButtonGroup/utils';
import CustomizedTooltip from '../Tooltip/MuiTooltip/Tooltip';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import { CFRFormHistoryModal } from './CFRFormHistoryModal';
import Tooltip from '../../customComponents/Tooltip/Tooltip';

export const CFRForm = ({
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
  const formHistory: Array<any> = useSelector((state: any) => state.foiRequests.foiRequestCFRFormHistory);

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
      disabled: isMinistry
    },
    {
      value: 'approved',
      label: 'Approved',
      disabled: isMinistry,
    },
  ];

  const reasons = [
    {
      value: 'init',
      label: 'Select Reason',
      disabled: true
    },
    {
      value: 'narrowedrequest',
      label: 'Narrowed Request',
      disabled: false,
    },
    {
      value: 'revisedfeeestimate',
      label: 'Revised Fee Estimate',
      disabled: false,
    }
  ];

  React.useEffect(() => {
    if (ministryId) {
      fetchCFRForm(
        ministryId,
        dispatch,
      );
    }
  }, [ministryId]);

  const tooltipReasons = {
    "title": "Reasons",
    "content": [
      <div className="toolTipContent">
        <p>Select 'Narrowed Request' when the applicant has narrowed their request. Select 'Revised Fee Estimate'
          when the request has not been narrowed but the estimated hours have changed.</p>
      </div>]
  };
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

  const handleTextChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;

    setFormData(values => ({...values, [name]: value}));
  };

  const initialState: any = useSelector((state: any) => state.foiRequests.foiRequestCFRForm);

  const blankForm: CFRFormData = {
    cfrfeeid: null,
    formStatus: "init",
    estimatedTotalDue: 0,
    actualTotalDue: 0,
    amountPaid: 0,
    estimatePaymentMethod: "init",
    balancePaymentMethod: "init",
    balanceRemaining:0,
    feewaiverAmount:0,
    refundAmount:0,
    estimates: {
      locating: 0,
      producing: 0,
      ministryPreparing: 0,
      iaoPreparing: 0,
      electronicPages: 0,
      hardcopyPages: 0,
    },
    actual: {
      locating: 0,
      producing: 0,
      ministryPreparing: 0,
      iaoPreparing: 0,
      electronicPages: 0,
      hardcopyPages: 0,
    },
    suggestions: '',
    reason:"init"
  };

  const [initialFormData, setInitialFormData] = useState(blankForm);
  const [formData, setFormData] = useState(initialFormData);


  React.useEffect(() => {
    let formattedData = {
      cfrfeeid: initialState.cfrfeeid,
      formStatus: initialState.status === null ? 'init' : initialState.status,
      estimatedTotalDue: initialState.feedata?.estimatedtotaldue || 0,
      actualTotalDue: initialState.feedata?.actualtotaldue || 0,
      estimatePaymentMethod: initialState.feedata?.estimatepaymentmethod || 'init',
      balancePaymentMethod: initialState.feedata?.balancepaymentmethod || 'init',
      amountPaid: initialState.feedata?.amountpaid,
      balanceRemaining: initialState.feedata?.balanceremaining,
      feewaiverAmount: initialState.feedata?.feewaiveramount || 0,
      refundAmount: initialState.feedata?.refundamount,
      estimates: {
        locating: initialState.feedata?.estimatedlocatinghrs,
        producing: initialState.feedata?.estimatedproducinghrs,
        iaoPreparing: initialState.feedata?.estimatediaopreparinghrs,
        ministryPreparing: initialState.feedata?.estimatedministrypreparinghrs,
        electronicPages: initialState.feedata?.estimatedelectronicpages,
        hardcopyPages: initialState.feedata?.estimatedhardcopypages,
      },
      actual: {
        locating: initialState.feedata?.actuallocatinghrs,
        producing: initialState.feedata?.actualproducinghrs,
        iaoPreparing: initialState.feedata?.actualiaopreparinghrs,
        ministryPreparing: initialState.feedata?.actualministrypreparinghrs,
        electronicPages: initialState.feedata?.actualelectronicpages,
        hardcopyPages: initialState.feedata?.actualhardcopypages,
      },
      suggestions: initialState.overallsuggestions,
      reason: initialState.reason === null ? "init" : initialState.reason
    };
    setInitialFormData(formattedData)
    setFormData(formattedData);
  }, [initialState]);

  const popstateHandler = (e: any) => returnToQueue(e, true);
  const [firstEditFlag, setFirstEditFlag] = React.useState(true);

  React.useEffect(() => {
    if (!_.isEqual(initialFormData, formData)) {
      setCFRUnsaved(true);
    } else {
      setCFRUnsaved(false);
    }
  }, [initialFormData, formData]);


  const validateField = (value: number, step: number) => {
    return (value % step) !== 0;
  }

  const validateEstimatePaymentMethod = () => {
    return initialFormData?.amountPaid === 0 && formData?.amountPaid > 0 && formData?.estimatePaymentMethod === 'init'
  }

  const validateBalancePaymentMethod = () => {
    return initialFormData?.amountPaid !== 0 &&
    formData?.amountPaid !== 0 &&
    formData?.amountPaid > initialFormData?.amountPaid &&
    formData?.balancePaymentMethod === 'init'
  }

  const validateFields = () => {
    if (validateBalancePaymentMethod() || validateEstimatePaymentMethod()) {
      return false;
    }
    let field: keyof typeof formData.estimates;
    for (field in formData.estimates) {
      if (validateField(formData.estimates[field], foiFees[field].unit)) {
        return false;
      }
    }
    let afield: keyof typeof formData.actual
    for (afield in formData.actual) {
      if (validateField(formData.actual[afield], foiFees[afield].unit)) {
        return false;
      }
    }
    return !_.isEqual(initialFormData, formData);
  }

  const handlePaymentMethodChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;
    setFormData(values => ({...values, [name]: value}));
  };

  const handleAmountPaidChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if (value === 0) {
      setFormData(values => ({...values, estimatePaymentMethod: 'init', balancePaymentMethod: 'init'}));
    } else if (formData.amountPaid === 0 && value > 0) {
      setFormData(values => ({
        ...values,
        estimatePaymentMethod: initialFormData.estimatePaymentMethod,
        balancePaymentMethod: initialFormData.balancePaymentMethod
      }));
    }
    handleAmountChanges(e)
  };

  const handleAmountChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if (value <= Math.max(formData.actualTotalDue, formData.estimatedTotalDue)) {
      setFormData(values => ({...values, [name]: value}));
    }
  };

  const handleRefundChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const re = new RegExp('^-?\\d+(?:\.\\d{0,' + (2 || -1) + '})?');
    const value : number = +(e.target.value.match(re)?.[0] || 0)
    if(value <= formData.amountPaid)
      setFormData(values => ({...values, [name]: value}));
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

  const calculateBalanceRemaining = () => {
    let balanceRemaining = 0;
    if (formData?.actualTotalDue)
      balanceRemaining = (formData.actualTotalDue - formData.amountPaid - formData.feewaiverAmount);
    else
      balanceRemaining = (formData.estimatedTotalDue - formData.amountPaid - formData.feewaiverAmount)
    return !Number.isNaN(balanceRemaining) || balanceRemaining  ? balanceRemaining : 0;
  }

  const cfrStatusDisabled = () => {
    if(requestState === StateEnum.peerreview.name){
      return true;
    }
    if (formHistory.length > 0 && [StateEnum.feeassessed.name, StateEnum.onhold.name, StateEnum.callforrecords.name, StateEnum.onholdother.name].includes(requestState)) {
      if (isMinistry) {
        return ['review', 'approved'].includes(initialFormData.formStatus) || isNewCFRForm;
      } else {
        return initialFormData.formStatus !== 'review';
      }
    }
    if (formData.balanceRemaining > 0 &&  [StateEnum.feeassessed.name, StateEnum.onhold.name, StateEnum.onholdother.name].includes(requestState)) {
      if (isMinistry) {
        return !['clarification', 'init'].includes(initialFormData.formStatus);
      } else {
        return initialFormData.formStatus === 'clarification';
      }
    }
    return true;
  }

  const save = () => {
    let callback = (_res: string) => {
      setIsNewCFRForm(false)
      setInitialFormData(formData)
      toast.success("CFR Form has been saved successfully.", {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      fetchCFRForm(
        ministryId,
        dispatch,
      );
    };
    let data;
    if (isMinistry) {
      data = {
        feedata:{
          amountpaid: formData.amountPaid,
          estimatedtotaldue: formData.estimatedTotalDue,
          actualtotaldue: formData.actualTotalDue,
          ...formData.estimatePaymentMethod !== 'init' && {estimatepaymentmethod: formData.estimatePaymentMethod},
          ...formData.balancePaymentMethod !== 'init' && {balancepaymentmethod: formData.balancePaymentMethod},
          balanceremaining: calculateBalanceRemaining(),
          feewaiveramount: formData.feewaiverAmount,
          refundamount: formData.refundAmount,
          estimatedlocatinghrs: formData.estimates.locating,
          actuallocatinghrs: formData.actual.locating,
          estimatedproducinghrs: formData.estimates.producing,
          actualproducinghrs: formData.actual.producing,
          estimatediaopreparinghrs: formData.estimates.iaoPreparing,
          estimatedministrypreparinghrs: formData.estimates.ministryPreparing,
          actualiaopreparinghrs: formData.actual.iaoPreparing,
          actualministrypreparinghrs: formData.actual.ministryPreparing,
          estimatedelectronicpages: formData.estimates.electronicPages,
          actualelectronicpages: formData.actual.electronicPages,
          estimatedhardcopypages: formData.estimates.hardcopyPages,
          actualhardcopypages: formData.actual.hardcopyPages,
        },
        overallsuggestions: formData.suggestions,
        status: formData.formStatus === 'init' ? '' : formData.formStatus,
        cfrfeeid: formData.cfrfeeid,
        reason: formData.reason === "init" ? '' : formData.reason
      }
    } else {
      data = {
        feedata:{
          amountpaid: formData.amountPaid,
          estimatediaopreparinghrs: formData.estimates.iaoPreparing,
          actualiaopreparinghrs: formData.actual.iaoPreparing,
          estimatedtotaldue: formData.estimatedTotalDue,
          actualtotaldue: formData.actualTotalDue,
          ...formData.estimatePaymentMethod !== 'init' && {estimatepaymentmethod: formData.estimatePaymentMethod},
          ...formData.balancePaymentMethod !== 'init' && {balancepaymentmethod: formData.balancePaymentMethod},
          balanceremaining: calculateBalanceRemaining(),
          feewaiveramount: formData.feewaiverAmount,
          refundamount: formData.refundAmount,
        },
        status: formData.formStatus,
        reason: formData.reason === "init" ? '' : formData.reason
      }
    }
    saveCFRForm(
      data,
      ministryId,
      requestId,
      isMinistry,
      dispatch,
      callback,
      (errorMessage: string) => {
        errorToast(errorMessage)
      },
    )
  };


  const [modalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState(<></>);
  const handleSave = () => {
    setModalOpen(false);
    save();
  };
  const handleClose = () => {
    setFormData(values => ({...values, formStatus: initialFormData.formStatus}));
    setModalOpen(false);
  };
  const handleStatusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleTextChanges(e);
    if (e.target.value === 'review') {
      setModalMessage(<>By changing the CFR Form Status to <b>"In Review with IAO"</b> you
      will be sending the form to the IAO user and locking your ability to edit the form.
      Are you sure you would like to continue?</>);
    } else if (e.target.value === 'approved') {
      setModalMessage(<>Are you sure you want to change the status to <b>"Approved"</b>? Once approved, a CFR form is uneditable. Any changes will require a new CFR form to be created.</>);
    } else if (e.target.value === 'clarification') {
      setModalMessage(<>By changing the CFR Form Status to <b>"Needs Clarification with Ministry" </b> you
      will be sending the form to the Ministry user and locking your ability to edit the form.
      Are you sure you would like to continue?</>);
    }
    setModalOpen(true);
  };

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const handleCreateClose = () => {
    setCreateModalOpen(false);
  };

  const cfrActualsDisabled = () => {
    return !isMinistry || formData?.formStatus !== 'approved' || requestState !== StateEnum.callforrecords.name || formData?.amountPaid === 0 || 
    requestState === StateEnum.peerreview.name;
  }

  const cfrEstimatedDisabled = () => {
    return !isMinistry || initialFormData?.formStatus === 'approved' || initialFormData?.formStatus === 'review' || requestState === StateEnum.peerreview.name;
  }

  const [historyModalOpen, setHistoryModal] = useState(false);
  const handleHistoryClose = () => {
    setHistoryModal(false);
  }

  const disableNewCfrFormBtn = () => {
    return(formData?.formStatus !== 'approved' || requestState === StateEnum.peerreview.name || (requestState !== StateEnum.callforrecords.name &&
      requestState !== StateEnum.feeassessed.name && requestState !== StateEnum.onhold.name) || (requestState === StateEnum.onhold.name && formData?.actualTotalDue > 0) || 
      (requestState === StateEnum.onholdother.name && formData?.actualTotalDue > 0));
  }

  const disableAmountPaid = () => {
    return (isMinistry || requestState === StateEnum.peerreview.name || requestState === StateEnum.peerreview.name|| requestState === StateEnum.feeassessed.name || formData?.formStatus !== 'approved' || ('balancePaymentMethod' in formData && formData?.balancePaymentMethod !== "init"))
  }

  const [isNewCFRForm, setIsNewCFRForm] = useState(false)
  const newCFRForm = () => {
    setCreateModalOpen(false)
    blankForm.amountPaid= initialState?.feedata?.amountpaid;
    blankForm.estimatePaymentMethod = initialState?.feedata?.estimatepaymentmethod || 'init';
    blankForm.balancePaymentMethod= initialState?.feedata?.balancepaymentmethod || 'init';
    blankForm.feewaiverAmount = initialState?.feedata?.feewaiveramount;
    blankForm.refundAmount = initialState?.feedata?.refundamount;
    setInitialFormData(blankForm);
    setFormData(blankForm);
    setIsNewCFRForm(true)
  }

  const isFeeWaiverDisabled = () => {
    if(isMinistry || 
      requestState === StateEnum.peerreview.name || 
      (!isMinistry && (requestState !== StateEnum.onhold.name && requestState !== StateEnum.onholdother.name || formData?.formStatus !== 'approved')))
      return true;
    else
      return false;
  }

  return (
    <div className="foi-review-container">
      <Box
        component="form"
        sx={{
          '& .MuiTextField-root': { my: 1, mx: 0 },
          '& .Mui-disabled': { '-webkit-text-fill-color': "black !important" },
          '& .MuiInputBase-root.Mui-disabled': { 'background-color': "#eee !important" },
        }}
        autoComplete="off"
      >
        <div className="foi-request-form">
          <div style={{marginTop: 20}}></div>
            <div className="container foi-review-request-container cfrform-container">
              <div className="foi-request-review-header-row1">
                <div className="foi-request-review-header-col1">
                  <div className="foi-request-number-header">
                    <h3 className="foi-review-request-text">{requestNumber}</h3>
                  </div>
                  <Chip
                    label={initialFormData.formStatus === 'approved' ? "Version " + formHistory.length : "Version " + (formHistory.length + 1) + " Draft" }
                    sx={{ backgroundColor: '#096DD1', color: '#fff', height: 19}}
                  />
                </div>
                <div className='foi-assigned-to-container'>
                  <div className='foi-assigned-to-inner-container' id="cfrstatuscontainer">
                    <TextField
                      id="cfrStatus"
                      label={"CFR Status"}
                      inputProps={{ "aria-labelledby": "cfrStatus-label"}}
                      InputLabelProps={{ shrink: true }}
                      select
                      name="formStatus"
                      value={formData?.formStatus}
                      onChange={handleStatusChange}
                      variant="outlined"
                      fullWidth
                      required
                      disabled={cfrStatusDisabled()}
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
                  </div>
                  {(isNewCFRForm || (formHistory?.length > 0 && (formData?.cfrfeeid !== formHistory[0]?.cfrfeeid)) || formHistory?.length > 1)  &&
                  <>
                    <div className='foi-assigned-to-inner-container'>
                      <TextField
                        id="reasons"
                        label={"Reason for Creating New CFR Form"}
                        inputProps={{ "aria-labelledby": "reasons-label"}}
                        InputLabelProps={{ shrink: true }}
                        placeholder={"Select Reason"}
                        select
                        name="reason"
                        value={formData?.reason}
                        onChange={handleTextChanges}
                        variant="outlined"
                        fullWidth
                        required
                        error={formData?.reason === 'init'}
                        disabled={!isMinistry || requestState === StateEnum.peerreview.name || formData?.formStatus === 'approved'}
                      >
                        {reasons.map((option) => (
                        <MenuItem
                          key={option.value}
                          value={option.value}
                          disabled={option.disabled}
                        >
                          {option.label}
                        </MenuItem>
                        ))}
                      </TextField>
                      <div className="cfrform-floatRight cfrform-reasons">
                        <Tooltip content={tooltipReasons} position={""}/>
                        <p className="hideContent" id="popup-7">Information7</p>
                      </div>
                    </div>
                  </>
                  }
                </div>
              </div>
              <div className="cfr-history-button">
                <CFRFormHistoryModal
                  modalOpen={historyModalOpen}
                  handleClose={handleHistoryClose}
                  formHistory={formHistory}
                  isMinistry={isMinistry}
                />
                <button
                  type="button"
                  className="btn btn-link btn-cfr-history"
                  disabled={formHistory.length < 1}
                  onClick={() => setHistoryModal(true)}
                >
                  CFR Form History
                </button>
              </div>
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
                        {/* <TextField
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
                          value={formData?.amountDue?.toFixed(2)}
                          onChange={handleAmountChanges}
                          variant="outlined"
                          placeholder="0"
                          fullWidth
                          disabled={true}
                          // onChange={handleMiddleNameChange}
                        /> */}
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
              <div className="foi-bottom-button-group cfrform">
                <button
                  type="button"
                  className="col-lg-4 btn btn-bottom btn-save"
                  id="btncfrsave"
                  onClick={save}
                  color="primary"
                  disabled={!validateFields() || requestState === StateEnum.peerreview.name || (formData?.reason === 'init' && isNewCFRForm)}
                >
                  Save
                </button>
                {isMinistry &&
                  <button
                    type="button"
                    className="col-lg-4 btn btn-bottom btn-cancel"
                    onClick={() => {
                      setCreateModalOpen(true)
                    }}
                    disabled={disableNewCfrFormBtn()}
                  >
                    + Create New CFR Form
                  </button>
                }
              </div>
            </div>
        </div>
      </Box>

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
    <div className="state-change-dialog">
      <Dialog
        open={createModalOpen}
        onClose={handleCreateClose}
        aria-labelledby="state-change-dialog-title"
        aria-describedby="state-change-dialog-description"
        maxWidth={'md'}
        fullWidth={true}
        // id="state-change-dialog"
      >
        <DialogTitle disableTypography id="state-change-dialog-title">
            <h2 className="state-change-header">Create New CFR Form </h2>
            <IconButton className="title-col3" onClick={handleCreateClose}>
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
        <DialogContent className={'dialog-content-nomargin'}>
          <DialogContentText id="state-change-dialog-description" component={'span'}>
            <span className="confirmation-message create-new-modal-message">
              Are you sure you want to create a new, blank CFR form? <br></br>
              <em>
                Any unsaved changes will be lost. The previous version will be locked for editing
                and viewable in the CFR Form History.
              </em>
            </span>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <button
            className={`btn-bottom btn-save btn`}
            onClick={newCFRForm}
          >
            Continue
          </button>
          <button className="btn-bottom btn-cancel" onClick={handleCreateClose}>
            Cancel
          </button>
        </DialogActions>
      </Dialog>
    </div>
  </div>
  );
}
