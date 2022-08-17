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
import { errorToast, isMinistryLogin, formatDate, addBusinessDays } from "../../../../helper/FOI/helper";
import type { params, FeeWaiverFormData } from './types';
import { fetchCFRForm, saveCFRForm } from "../../../../apiManager/services/FOI/foiCFRFormServices";
import _ from 'lodash';
import { toast } from "react-toastify";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import FileUpload from "../../customComponents/FileUpload";
import {
  MimeTypeList,
  MaxFileSizeInMB,
} from "../../../../constants/FOI/enum";
import {isValidationError} from "./util";

export const FeeWaiverForm = ({
  requestDescription,
  fromDate,
  toDate,
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
  const cfrTotalAmountDue: number = useSelector((state: any) => state.foiRequests.foiRequestCFRForm.feedata.totalamountdue);

  const FeeWaiverStatuses = [
    {
      value: 'iao',
      label: 'In Progress IAO',
      disabled: isMinistry,
    },
    {
      value: 'review',
      label: 'Ministry Review',
      disabled: isMinistry
    },
    {
      value: 'decision',
      label: 'Ministry Decision',
      disabled: !isMinistry,
    },
    {
       value: 'completed',
       label: 'Completed',
       disabled: true,
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


  const blankForm: FeeWaiverFormData = {
    status: "iao",
    formdata: {    
      requesteddate: "",
      receiveddate: "",
      summary: "",
      recordsdescription: "",
      inability: false,
      publicinterest: false,
      inabilitydetails: {
          hasproof: undefined,
          description: ""
      },
      publicinterestdetails: {
          debate: undefined,
          environment: undefined,
          disclosing: undefined,
          understanding: undefined,
          newpolicy: undefined,
          financing: undefined,
          other: "",
          analysis: "", //partial yes or no
          description: ""

      },
      disseminate: undefined,
      abletodisseminate: undefined,
      narrow: undefined,
      exceed: undefined,
      timelines: undefined,
      previous: undefined,
      description: "",
      recommendation: {
          waive: "partial", //partial yes or no
          summary: "",
          amount: 0
      },
      decision: {
        amount: 0
      }
    }
  };

  
  const [feeWaiverData, setFeeWaiverData] = useState(blankForm);
  const [initialFormData, setInitialFormData] = React.useState(blankForm);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState(<></>);
  const [dirty, setDirty] = React.useState(false);
  const markFormDirty = () => setDirty(true);
  const initialState: any = useSelector((state: any) => state.foiRequests.foiRequestFeeWaiverForm);

  React.useEffect(() => {
    console.log("initialState",initialState);
    if(initialState && Object.entries(initialState).length > 0){
        setInitialFormData(initialState);
        setFeeWaiverData(initialState);
    }
  }, [initialState]);
  
  const handleStatusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name : string = e.target.name;
    const value : string = e.target.value;
    setFeeWaiverData(values => ({...values, [name]: value}));
    if (e.target.value === 'review') {
        setModalMessage(<>Are you sure you want to change the status to Ministry Review? 
        The Fee Waiver form will be locked for editing and only the Ministry coordinator can change it back?</>);
        setModalOpen(true);
    } else if (e.target.value === 'decision') {
        setModalMessage(<>Are you sure you wish to save the Fee Waiver Form? 
        Once you save this amount and approve the form the total will update for IAO and the applicant?</>);
        setModalOpen(true);
    }
  };

  const handleFormDataChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: string = e.target.value;

    const formData = feeWaiverData?.formdata;
    const newFormData = {...formData, [name]: (name === 'requesteddate' || name === 'receiveddate' || name === 'summary'||
                                            name === 'recordsdescription' || name === 'description' ) ? value : JSON.parse(value)};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: newFormData};
    setFeeWaiverData(newFeeWaiverData);
  };

  const handleInabilityDetailsChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: string = e.target.value;

    const formData = feeWaiverData?.formdata;
    const inabilityDetails = formData?.inabilitydetails;
    const newInabilityDetails = {...inabilityDetails, [name]: name === 'hasproof' ? JSON.parse(value) : value};
    console.log("newInabilityDetails",newInabilityDetails);
    const newFormData = {...formData, ["inabilitydetails"]: newInabilityDetails};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: newFormData};
    console.log("newFeeWaiverData",newFeeWaiverData);
    setFeeWaiverData(newFeeWaiverData);
  };

  const handlePublicInterestDetailsChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: string = e.target.value;
    
    const formData = feeWaiverData?.formdata;
    const publicinterestdetails = formData?.publicinterestdetails;
    const newPublicInterestDetails = {...publicinterestdetails, [name]: (name !== 'description' && name !== 'analysis' && name !== 'other') ?
                                        JSON.parse(value) :value};
    const newFormData = {...formData, ["publicinterestdetails"]: newPublicInterestDetails};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: newFormData};
    console.log("newFeeWaiverData",newFeeWaiverData);
    setFeeWaiverData(newFeeWaiverData);
  };

  const handleRecommendationChanges = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: string = e.target.value;

    console.log("name",name);
    console.log("value",value);
    const formData = feeWaiverData?.formdata;
    const recommendation = formData?.recommendation;
    const newRecommendation = {...recommendation, [name]: value};
    const newFormData = {...formData, ["recommendation"]: newRecommendation};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: newFormData};
    console.log("newFeeWaiverData",newFeeWaiverData);
    setFeeWaiverData(newFeeWaiverData);
  };

  const handleAmountWaivedChanges = (e: any) => {
    const name : string = e.target.name;
    const value : number = Math.floor((+e.target.value) * 100) / 100;
    if (value <= cfrTotalAmountDue) {
      setFeeWaiverData({
        ...feeWaiverData,
        formdata: {
          ...feeWaiverData.formdata,
          [name]: {
            ...(feeWaiverData.formdata[name as keyof FeeWaiverFormData['formdata']] as Object),
            amount: value}
        }
      })
    }
  }


  const handleFeeWaiverTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: boolean = e.target.checked;

    const formData = feeWaiverData?.formdata;
    const newFormData = {...formData, [name]: value};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: newFormData};
    setFeeWaiverData(newFeeWaiverData);
  };

  const handleRequestedDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name: string = e.target.name;
    const value: string = e.target.value;
    console.log("name",name);
    console.log("value",value);
    const formData = feeWaiverData?.formdata;
    const newFormData = {...formData, [name]: value};
    calculateFeeWaiverReceivedDate(e.target.value, newFormData);
  }

  const calculateFeeWaiverReceivedDate = (requestedDate : string, newFormData : any) => {
    const dateString = requestedDate ? requestedDate.substring(0,10): "";
    const feeWaiverReceivedDate= dateString? addBusinessDays(dateString, 20) : "";
    const name = "receiveddate";
    const value = feeWaiverReceivedDate ? formatDate(feeWaiverReceivedDate) : "";
    const updatedFormData = {...newFormData, [name]: value};
    let newFeeWaiverData : FeeWaiverFormData = {...feeWaiverData, ["formdata"]: updatedFormData};
    setFeeWaiverData(newFeeWaiverData);
   }

  

  const [newFiles, setNewFiles] = useState([]);
  const [attachment, setAttachment] = useState({});


  const save = () => {
    var callback = (_res: string) => {
        setFeeWaiverData(feeWaiverData);
        toast.success("Fee Waiver Form has been saved successfully.", {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
      };
  }; 


  const handleSave = () => {
    setModalOpen(false);
    save();
  };
  const handleClose = () => {
    setFeeWaiverData(values => ({...values, status: initialFormData.status}));
    setModalOpen(false);
  };

  const validateField = (fieldName: string) => {
    switch(fieldName){
        case 'recordsdescription':
            return (feeWaiverData?.formdata.publicinterest || feeWaiverData?.formdata.inability &&
                !(!!feeWaiverData?.formdata?.recordsdescription))
        case 'inabilityDetailsDescription':
            return (feeWaiverData?.formdata.inabilitydetails.hasproof &&
                !(!!feeWaiverData?.formdata?.inabilitydetails.description))
        case 'publicInterestDescription':
            return (feeWaiverData?.formdata?.publicinterestdetails.analysis === 'partial' ||
                feeWaiverData?.formdata?.publicinterestdetails.analysis === 'yes' &&
                !(!!feeWaiverData?.formdata?.publicinterestdetails.description))
        case 'description':
            return ((feeWaiverData?.formdata?.previous || feeWaiverData?.formdata?.narrow || feeWaiverData?.formdata?.exceed ||
                feeWaiverData?.formdata?.timelines) && !(!!feeWaiverData?.formdata?.description))
        default:{
            return false;
        }
    }
  }


  return (
    <div className="foi-review-container">
    <Box
      component="form"
      sx={{
        '& .MuiTextField-root': { m: 1 },
      }}
      autoComplete="off"
      onChange={markFormDirty}>
    <div className="foi-request-form">
    <div style={{marginTop: 20}}></div>
    <div className="container foi-review-request-container cfrform-container">
      <div className="foi-request-review-header-row1">
        <div className="col-9 foi-request-number-header">
          <h3 className="foi-review-request-text">{requestNumber}</h3>
        </div>
        <div className="col-3">
          <TextField
            id="status"
            label={"Form Status"}
            inputProps={{ "aria-labelledby": "status-label"}}
            InputLabelProps={{ shrink: true }}
            select
            name="status"
            value={feeWaiverData?.status}
            onChange={handleStatusChange}
            variant="outlined"
            disabled={(feeWaiverData?.status === 'review' && !isMinistry) || feeWaiverData?.status === 'completed'}
            fullWidth
            required
          >
            {FeeWaiverStatuses.map((option) => (
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
      </div>
    <fieldset disabled={isMinistry || feeWaiverData?.status === 'review' || feeWaiverData?.status === 'completed'}>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">REQUEST DETAILS</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                <TextField
                    id="requesteddate"
                    name="requesteddate"
                    label="Fee Waiver Requested"
                    type="date"
                    value={feeWaiverData?.formdata.requesteddate || ''}
                    onChange={handleRequestedDateChange}
                    inputProps={{ "aria-labelledby": "requesteddate-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    InputProps={{inputProps: { max: formatDate(new Date())} }}
                    variant="outlined"
                    required
                    error={!(!!feeWaiverData?.formdata.requesteddate)}
                    fullWidth
                />
              </div>
              <div className="col-lg-6 foi-details-col">
                <TextField
                    id="receiveddate"
                    name="receiveddate"
                    label="Fee Waiver Received"
                    type="date"
                    value={feeWaiverData?.formdata.receiveddate || ''}
                    inputProps={{ "aria-labelledby": "receiveddate-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    //InputProps={{inputProps: { min: feeWaiverReceived, max: formatDate(new Date())} }}
                    variant="outlined"
                    required
                    error={!(!!feeWaiverData?.formdata.receiveddate)}
                    fullWidth
                    disabled= {true}
                />
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-12">
                    <div className="labelBold" style={{margin:"15px 8px"}}>Request Description</div>
                </div>
                <div className="col-lg-12">
                    <div className="contentStyle">{requestDescription}</div>
                </div>
            </div>
            <br/>
            <div className="row foi-details-row">
                <div className="col-lg-12">
                    <div className="contentStyle">Date Range for Records Search</div>
                </div>
                <div className="col-lg-12">
                    <div className="contentStyle">{fromDate} - {toDate}</div>
                </div>
            </div>
            <br/>
            <div className="row foi-details-row">
                <div className="col-lg-12">
                    <span className="contentStyle">Total Fees Due</span>
                </div>
              <div className="col-lg-12">
                <span className="contentStyle">{"$"+cfrTotalAmountDue}</span>
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
            <div className="row foi-details-row textPadding">
              <div className="col-lg-12">
                <TextField
                  id="summary"
                  label="Summary of Applicants Request to Waive Fee"
                  multiline
                  rows={4}
                  name="summary"
                  value={feeWaiverData?.formdata?.summary}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleFormDataChanges}
                  fullWidth
                  required
                  error={!(!!feeWaiverData?.formdata?.summary)}
                />
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col contentStyle">
                        <span><b>Type of Fee Waiver requested by applicant?* </b></span>
                        <span><i>Check 1 or more that apply and complete the applicable sections 2 or 3 below.</i></span>
                </div>
            </div>
            <div className="row foi-details-row labelText textPadding">
                <div className="col-lg-4">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="inability"
                        name="inability"
                        type="checkbox"
                        className="checkmark"
                        checked={feeWaiverData?.formdata.inability}
                        onChange={handleFeeWaiverTypeChange}
                        />
                        <span className="checkmark"></span>
                        INABILITY TO PAY
                    </label>
                </div>
                <div className="col-lg-4">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="publicinterest"
                        name="publicinterest"
                        type="checkbox"
                        className="checkmark"
                        checked={feeWaiverData?.formdata.publicinterest}
                        onChange={handleFeeWaiverTypeChange}
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
                        value={feeWaiverData?.formdata?.recordsdescription}
                        variant="outlined"
                        InputLabelProps={{ shrink: true, }}
                        onChange={handleFormDataChanges}
                        required={feeWaiverData?.formdata.publicinterest || feeWaiverData?.formdata.inability}
                        fullWidth
                        error= {validateField("recordsdescription")}
                        // error={feeWaiverData?.formdata.publicinterest || feeWaiverData?.formdata.inability &&
                        //     !(!!feeWaiverData?.formdata?.recordsdescription)}
                    />
                </div>
                <div className="col-lg-12 foi-details-col">
                    <div className="contentStyle"><i>
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
        <Accordion expanded={feeWaiverData?.formdata.inability}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">INABILITY TO PAY</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 textPadding">
                    Has the applicant provided documentary evidence of the inability to pay?*
                    (e.g.: bank statement, pay stub or tax return)?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        name="hasproof"
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleInabilityDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.inabilitydetails.hasproof === true}
                        //checked={!!feeWaiverData?.formdata?.inabilitydetails.hasproof ? feeWaiverData?.formdata?.inabilitydetails.hasproof : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        name="hasproof"
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleInabilityDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.inabilitydetails.hasproof === false}
                        //checked={feeWaiverData?.formdata?.inabilitydetails.hasproof === false ? !feeWaiverData?.formdata?.inabilitydetails.hasproof : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="inabilityDetailsDescription"
                  label="Describe evidence provided and whether it is sufficient"
                  multiline
                  rows={4}
                  name="description"
                  value={feeWaiverData?.formdata?.inabilitydetails.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleInabilityDetailsChanges}
                  required={feeWaiverData?.formdata.inabilitydetails.hasproof}
                  error={validateField("inabilityDetailsDescription")}
                //   error={feeWaiverData?.formdata.inabilitydetails.hasproof &&
                //     !(!!feeWaiverData?.formdata?.inabilitydetails.description) }
                  fullWidth
                />
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      <div className='request-accordian'>
        <Accordion expanded={feeWaiverData?.formdata.publicinterest}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">PUBLIC INTEREST</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                    Has the subject of the records been a matter of recent public debate?*
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="debate"
                        name='debate'
                        type="radio"
                        value='true'
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.debate === true}
                        //checked={!!feeWaiverData?.formdata?.publicinterestdetails.debate ? feeWaiverData?.formdata?.publicinterestdetails.debate : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="debate"
                        name='debate'
                        value='false'
                        type="radio"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.debate === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.debate === false ? !feeWaiverData?.formdata?.publicinterestdetails.debate : false}
                        
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                Does the subject matter of the records relate directly to the environment,
                public health, or safety?*
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="environment"
                        name='environment'
                        type="radio"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.environment === true}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.environment === true? feeWaiverData?.formdata?.publicinterestdetails.environment : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="environment"
                        name='environment'
                        type="radio"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.environment === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.environment === false? !feeWaiverData?.formdata?.publicinterestdetails.environment : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                 Could dissemination of the information in the records reasonably be expected to yield a public benefit by: *
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                Disclosing an environmental concern or a public health or safety concern?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="disclosing"
                        name="disclosing"
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.disclosing === true}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.disclosing === true? feeWaiverData?.formdata?.publicinterestdetails.disclosing : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="disclosing"
                        name="disclosing"
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.disclosing === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.disclosing === false? !feeWaiverData?.formdata?.publicinterestdetails.disclosing : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                Contributing to the development or public understanding of, or debate on, an
                important environmental or public health or safety issue?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="understanding"
                        name='understanding'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.understanding === true}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.understanding === true? feeWaiverData?.formdata?.publicinterestdetails.understanding : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="understanding"
                        name='understanding'
                        type="radio"
                        className="checkmark"
                        value="false"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.understanding === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.understanding === false? !feeWaiverData?.formdata?.publicinterestdetails.understanding : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                Contributing to public understanding of, or debate on, an important new policy, law, program,
                or service?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="newpolicy"
                        name='newpolicy'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.newpolicy === true}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.newpolicy === true? feeWaiverData?.formdata?.publicinterestdetails.newpolicy : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="newpolicy"
                        name='newpolicy'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.newpolicy === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.newpolicy === false? !feeWaiverData?.formdata?.publicinterestdetails.newpolicy : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold textPadding">
                    Do the records show how the public body is allocating financial or other resources? *
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="financing"
                        name='financing'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.financing === true}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.financing === true? feeWaiverData?.formdata?.publicinterestdetails.financing : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="financing"
                        name='financing'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.financing === false}
                        //checked={feeWaiverData?.formdata?.publicinterestdetails.financing === false? !feeWaiverData?.formdata?.publicinterestdetails.financing : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 textPadding">
                <TextField
                  id="other"
                  label="Other public interest considerations (if any)"
                  multiline
                  rows={4}
                  name="other"
                  value={feeWaiverData?.formdata?.publicinterestdetails.other}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handlePublicInterestDetailsChanges}
                  fullWidth
                />
              </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-6 labelBold textPadding">
                Based on the analysis above, do the requested records relate to a matter
                of public interest? *
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="analysis"
                        name="analysis"
                        type="radio"
                        value="partial"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.analysis == 'partial'}
                        //checked={!!feeWaiverData?.formdata?.publicinterestdetails.analysis ?feeWaiverData?.formdata?.publicinterestdetails.analysis == 'partial' :false}
                        />
                        <span className="checkmark"></span>
                        PARTIALLY
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="analysis"
                        name="analysis"
                        type="radio"
                        value="yes"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.analysis == 'yes'}
                        //checked={!!feeWaiverData?.formdata?.publicinterestdetails.analysis ?feeWaiverData?.formdata?.publicinterestdetails.analysis == 'yes' :false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="analysis"
                        name="analysis"
                        type="radio"
                        value="no"
                        className="checkmark"
                        onChange={handlePublicInterestDetailsChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.publicinterestdetails.analysis == 'no'}
                        //checked={!!feeWaiverData?.formdata?.publicinterestdetails.analysis ?feeWaiverData?.formdata?.publicinterestdetails.analysis == 'no' :false}
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
                  name="description"
                  value={feeWaiverData?.formdata?.publicinterestdetails.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handlePublicInterestDetailsChanges}
                  required={feeWaiverData?.formdata?.publicinterestdetails.analysis === 'partial' ||
                  feeWaiverData?.formdata?.publicinterestdetails.analysis === 'yes'}
                  error={validateField("publicInterestDescription")}
                //   error={feeWaiverData?.formdata?.publicinterestdetails.analysis === 'partial' ||
                //         feeWaiverData?.formdata?.publicinterestdetails.analysis === 'yes' &&
                //         !(!!feeWaiverData?.formdata?.publicinterestdetails.description)}
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
          <AccordionDetails className='labelBold'>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                    Is the applicant's primary purpose for requesting records to disseminate information
                    in a way that could reasonably be expected to benefit the public rather than serving
                    a private interest?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="disseminate"
                        name="disseminate"
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.disseminate === true}
                        //checked={feeWaiverData?.formdata?.disseminate === true? feeWaiverData?.formdata?.disseminate : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="disseminate"
                        name="disseminate"
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.disseminate === false}
                        //checked={feeWaiverData?.formdata?.disseminate === false? !feeWaiverData?.formdata?.disseminate : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                    Is the applicant able to disseminate the information to the public?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="abletodisseminate"
                        name='abletodisseminate'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.abletodisseminate === true}
                        //checked={feeWaiverData?.formdata?.abletodisseminate === true? feeWaiverData?.formdata?.abletodisseminate : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="abletodisseminate"
                        name='abletodisseminate'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.abletodisseminate === false}
                        //checked={feeWaiverData?.formdata?.abletodisseminate === false? !feeWaiverData?.formdata?.abletodisseminate : false}
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
            <div className="row foi-details-row labelText">
                <div className="col-lg-12 labelBold">
                    Is there any other reason it is fair to excuse payment?  Factors to consider include: *
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                    Was the applicant willing to narrow the request for records to reduce the fee?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="narrow"
                        name='narrow'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.narrow === true}
                        //checked={feeWaiverData?.formdata?.narrow === true? feeWaiverData?.formdata?.narrow : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="narrow"
                        name='narrow'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.narrow === false}
                        //checked={feeWaiverData?.formdata?.narrow === false? !feeWaiverData?.formdata?.narrow : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                    Do the costs of processing the applicant's FOI request exceed the fee estimate considerably
                    and, if so, is it reasonable to require the public body to bear some or all of those costs?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="exceed"
                        name='exceed'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.exceed === true}
                        //checked={feeWaiverData?.formdata?.exceed === true? feeWaiverData?.formdata?.exceed : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="exceed"
                        name='exceed'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.exceed === false}
                        //checked={feeWaiverData?.formdata?.exceed === false? !feeWaiverData?.formdata?.exceed : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 foi-details-col">
                    Have statutory timelines on the FOI file been met to date?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="timelines"
                        name='timelines'
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.timelines === true}
                        //checked={!!feeWaiverData?.formdata?.timelines ? feeWaiverData?.formdata?.timelines : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="timelines"
                        name='timelines'
                        type="radio"
                        value="false"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.timelines === false}
                        //checked={feeWaiverData?.formdata?.timelines === false? !feeWaiverData?.formdata?.timelines : false}
                        />
                        <span className="checkmark"></span>
                        NO
                    </label>
                </div>
            </div>
            <div className="row foi-details-row labelText textPadding">
                <div className="col-lg-8 foi-details-col">
                    Have previous orders of the OIPC ruled that similar types of records or information should
                    or should not be subject to a fee?
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="previous"
                        name="previous"
                        type="radio"
                        value="true"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.previous === true}
                        //checked={!!feeWaiverData?.formdata?.previous ? feeWaiverData?.formdata?.previous : false}
                        />
                        <span className="checkmark"></span>
                        YES
                    </label>
                </div>
                <div className="col-lg-2">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="previous"
                        name="previous"
                        value="false"
                        type="radio"
                        className="checkmark"
                        onChange={handleFormDataChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.previous === false}
                        //checked={feeWaiverData?.formdata?.previous === false? !feeWaiverData?.formdata?.previous : false}
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
                  value={feeWaiverData?.formdata?.description}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleFormDataChanges}
                  required={feeWaiverData?.formdata?.narrow || feeWaiverData?.formdata?.exceed || feeWaiverData?.formdata?.timelines ||
                            feeWaiverData?.formdata?.previous}
                  error={validateField("description")}
                //   error={(feeWaiverData?.formdata?.previous || feeWaiverData?.formdata?.narrow || feeWaiverData?.formdata?.exceed ||
                //         feeWaiverData?.formdata?.timelines) && !(!!feeWaiverData?.formdata?.description)}
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
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                    Select with Overall IAO Recommendations:*
                </div>
            </div>
            <div className="row foi-details-row labelText textPadding">
                <div className="col-lg-12">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="waive"
                        name='waive'
                        type="radio"
                        value="partial"
                        className="checkmark"
                        onChange={handleRecommendationChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.recommendation.waive === 'partial'}
                        //checked={!!feeWaiverData?.formdata?.recommendation.waive ? feeWaiverData?.formdata?.recommendation.waive === 'partial' : false}
                        />
                        <span className="checkmark"></span>
                        Waive Fee in Part
                    </label>
                </div>
                <div className="col-lg-12">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="waive"
                        name='waive'
                        type="radio"
                        value="yes"
                        className="checkmark"
                        onChange={handleRecommendationChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.recommendation.waive === 'yes'}
                        //checked={!!feeWaiverData?.formdata?.recommendation.waive ? feeWaiverData?.formdata?.recommendation.waive === 'yes' : false}
                        />
                        <span className="checkmark"></span>
                        Waive Fee in Full
                    </label>
                </div>
                <div className="col-lg-12">
                    <label className='check-item checkboxStyle'>
                        <input
                        id="waive"
                        name='waive'
                        value="no"
                        type="radio"
                        className="checkmark"
                        onChange={handleRecommendationChanges}
                        defaultChecked={false}
                        checked={feeWaiverData?.formdata?.recommendation.waive === 'no'}
                        //checked={!!feeWaiverData?.formdata?.recommendation.waive ? feeWaiverData?.formdata?.recommendation.waive === 'no' : false}
                        />
                        <span className="checkmark"></span>
                        Do Not Waive Fee
                    </label>
                </div>
            </div>
            <div className="row foi-details-row textPadding">
              <div className="col-lg-12 foi-details-col">
                <TextField
                  id="recommendationSummary"
                  label="Summarize Rational"
                  multiline
                  rows={4}
                  name="summary"
                  value={feeWaiverData?.formdata?.recommendation.summary}
                  variant="outlined"
                  InputLabelProps={{ shrink: true, }}
                  onChange={handleRecommendationChanges}
                  required={!!feeWaiverData?.formdata?.recommendation.waive}
                  error={(!!feeWaiverData?.formdata?.recommendation.waive && !(!!feeWaiverData?.formdata?.recommendation.summary))}
                  fullWidth
                />
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">
                    <TextField
                    id="amounttobewaivedrecommendation"
                    label="Amount to be waived"
                    inputProps={{
                        "aria-labelledby": "amounttobewaived-label",
                        step: 0.01,
                        max: cfrTotalAmountDue,
                        min: 0
                    }}
                    InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    name="recommendation"
                    type="number"
                    value={feeWaiverData?.formdata?.recommendation.amount}
                    onChange={handleAmountWaivedChanges}
                    onBlur={(e) => {
                        e.target.value = parseFloat(e.target.value).toFixed(2);
                    }}
                    fullWidth
                    disabled={cfrTotalAmountDue<=0 || feeWaiverData?.formdata?.recommendation.waive === 'no'|| feeWaiverData?.formdata?.recommendation.waive === 'yes'}
                    />
                </div>
                <div className="col-lg-6 foi-details-col">
                    <TextField
                        id="valueofamountrecommendation"
                        label={"Value of amount"}
                        inputProps={{
                          "aria-labelledby": "valueofamount-label",
                          step: 1,
                          max: 100,
                          min: 0
                        }}
                        InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="valueofamount"
                        type="number"
                        onChange={(e) => handleAmountWaivedChanges({target: {name: 'recommendation', value: ((parseFloat(e.target.value) / 100) * cfrTotalAmountDue).toFixed(2)}})}
                        value={Math.round((feeWaiverData?.formdata?.recommendation.amount / cfrTotalAmountDue) * 100)}
                        variant="outlined"
                        fullWidth
                        required
                        disabled={ cfrTotalAmountDue<=0 || feeWaiverData?.formdata?.recommendation.waive === 'no'|| feeWaiverData?.formdata?.recommendation.waive === 'yes'}
                    >
                    </TextField>
                </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
      </fieldset>
      <div className='request-accordian'>
        <Accordion defaultExpanded={true}>
          <AccordionSummary className="accordionSummary" expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className="heading">PUBLIC BODY DECISION</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="row foi-details-row labelText">
                <div className="col-lg-8 labelBold">
                    Signature <em>Upload Image or Signed Form</em>*
                </div>
            </div>
            <div className="row foi-details-row">
              <div className="col-lg-12 foi-details-col">
                <div className="feeWaiverFileUpload">
                  <FileUpload
                    attchmentFileNameList={[]}
                    multipleFiles={false}
                    mimeTypes={MimeTypeList.extensionAttachment}
                    maxFileSize={MaxFileSizeInMB.extensionAttachment}
                    totalFileSize={MaxFileSizeInMB.totalFileSize}
                    updateFilesCb={setNewFiles}
                    attachment={attachment}
                    existingDocuments={[]}
                  />
                </div>
              </div>
            </div>
            <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">
                    <TextField
                    id="amounttobewaiveddecision"
                    label="Amount to be waived"
                    inputProps={{
                        "aria-labelledby": "amounttobewaived-label",
                        step: 0.01,
                        max: cfrTotalAmountDue,
                        min: 0
                    }}
                    InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>
                    }}
                    InputLabelProps={{ shrink: true }}
                    variant="outlined"
                    name="decision"
                    type="number"
                    value={feeWaiverData?.formdata?.decision.amount}
                    onChange={handleAmountWaivedChanges}
                    onBlur={(e) => {
                        e.target.value = parseInt(e.target.value).toFixed(1);
                    }}
                    fullWidth
                    disabled={cfrTotalAmountDue<=0}
                    />
                </div>
                <div className="col-lg-6 foi-details-col">
                    <TextField
                        id="valueofamountdecision"
                        label={"Value of amount"}
                        inputProps={{
                          "aria-labelledby": "valueofamount-label",
                          step: 1,
                          max: 100,
                          min: 0
                        }}
                        InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>
                        }}
                        InputLabelProps={{ shrink: true }}
                        name="valueofamount"
                        type="number"
                        onChange={(e) => handleAmountWaivedChanges({target: {name: 'decision', value: ((parseFloat(e.target.value) / 100) * cfrTotalAmountDue).toFixed(2)}})}
                        value={Math.round((feeWaiverData?.formdata?.decision.amount / cfrTotalAmountDue) * 100)}
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
          disabled={isValidationError(feeWaiverData, newFiles) || !dirty}
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
    >
      <DialogTitle disableTypography id="state-change-dialog-title">
          <h2 className="state-change-header">Waiving Fees</h2>
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
