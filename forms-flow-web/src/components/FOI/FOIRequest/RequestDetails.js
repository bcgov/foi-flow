import React, {useState} from 'react';
import { useParams } from 'react-router-dom';
import { useSelector } from "react-redux";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { formatDate, addBusinessDays, businessDay } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { StateEnum } from '../../../constants/FOI/statusEnum';
import { shouldDisableFieldForMinistryRequests, findRequestState } from "./utils"
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import MinistriesCanvassed from '../customComponents/MinistriesCanvassed/MinistriesCanvassed';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InputAdornment from "@material-ui/core/InputAdornment";
import SvgIcon from "./InternalConsultation/SvgIcon";
import { Chip } from '@mui/material';
import clsx from "clsx";
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';


const RequestDetails = React.memo(
  ({
    requestDetails,
    requestStatus,
    handleRequestDetailsValue,
    handleRequestDetailsInitialValue,
    handleConsultRequestDetailsValue,
    handleConsultRequestDetailsInitialValue,
    createSaveRequestObject,
    disableInput,
    isHistoricalRequest, 
    isAddConsultRequest,
    isDataSynced,
    requestConsults,
    setUnSavedRequest,
    createSaveConsultRequestObject,
    handleConsultDueDateValidation,
  }) => {    /**
     *  Request details box in the UI
     *  All fields are mandatory here
     */

    const useStyles = makeStyles({
      heading: {
        color: '#FFF',
        fontSize: '16px !important',
        fontWeight: 'bold !important'
      },
      accordionSummary: {
        flexDirection: 'row-reverse'
      },
      showConsultDueDateFieldValidation: {
        color: "#CE3E39",
        fontStyle: 'italic',
        fontSize: '13px !important',
      },
      hideConsultDueDateFieldValidation: {
        visibility: 'hidden',
      },
      warningAmberIcon:{
        color: "#CE3E39 !important",
        width: "20px",
        transform: 'translateY(-1%)',
        fontSize: "medium !important",
      },
      showDueDateIcon: {
        color: "#CE3E39 !important",
        backgroundColor: "#fff !important",
        position: 'absolute',
        right: 37,
        pointerEvents: 'none',
      },
      hideDueDateIcon: {
        visibility: 'hidden',
      },
    });
    const classes = useStyles();
    const disableFieldForMinistryRequest = shouldDisableFieldForMinistryRequests(requestStatus)
    const {ministryId} = useParams();
    const validateFields = (request, name, value) => {
      if (request !== undefined) {
        const startDate = !!request.requestProcessStart ? formatDate(request.requestProcessStart) : "";
        if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {
          return !!request.requestType ? request.requestType : "Select Request Type";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
          if(request.receivedMode) {
            return request.receivedMode;
          }

          const source = requestDetails.sourceOfSubmission ? requestDetails.sourceOfSubmission : "";
          if(source === FOI_COMPONENT_CONSTANTS.ONLINE_FORM.replace(/\s/g, '').toLowerCase()) {
            return FOI_COMPONENT_CONSTANTS.ONLINE_FORM;
          }

          return "Select Received Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
          return !!request.deliveryMode ? request.deliveryMode : "Select Delivery Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF) {
          return !!request.receivedDateUF ? request.receivedDateUF : "";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {

          if(startDate && startDate >= formatDate(value)) {
            return startDate
          }

          return value || "";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.DUE_DATE) {
          if(request.dueDate || request.isconsultflag) {
            return request.dueDate
          }

          if(value) {
            return dueDateCalculation(value);
          }

          return "";
        }
      }
      else {
        return "";
      }
    }

    //get the RequestType, ReceivedMode and DeliveryMode master data
    const requestType = useSelector(state=> state.foiRequests.foiRequestTypeList);
    const receivedMode = useSelector(state=> state.foiRequests.foiReceivedModeList);
    const deliveryMode = useSelector(state=> state.foiRequests.foiDeliveryModeList);
    const [openModal, setModal] = useState(false);
    const [consultDueDate, setConsultDueDate] = useState(requestConsults?.dueDate ? requestConsults?.dueDate : '')
    const [isConsultDueDateValid, setIsConsultDueDateValid] = React.useState(false);
    const calculateReceivedDate = (receivedDateString) => {
      const dateString = receivedDateString ? receivedDateString.substring(0,10): "";
      receivedDateString = receivedDateString ? new Date(receivedDateString): "";
      if (receivedDateString !== "" && ((receivedDateString.getHours() > 16 || (receivedDateString.getHours() === 16 && receivedDateString.getMinutes() > 30)) || !businessDay(dateString))) {
          receivedDateString = addBusinessDays(receivedDateString, 1);
      }
      return formatDate(receivedDateString);
    }

    //updates the default values from the request details
    React.useEffect(() => {

      setSelectedRequestType(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE));
      setSelectedReceivedMode(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE));
      setSelectedDeliveryMode(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE));
      setReceivedDate(getReceivedDateForLocalState);
      setStartDate(getProcessStartDateForLocalState);
      setDueDate(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DUE_DATE, getProcessStartDateForLocalState()));

      let receivedDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF);
      receivedDate = calculateReceivedDate(receivedDate);
      const startDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, receivedDate);
      const requestDetailsObject = {
        requestType: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE),
        receivedMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE),
        deliveryMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE),
        receivedDate: !!receivedDate ? formatDate(receivedDate): "",
        requestStartDate: startDate ? formatDate(startDate): "",
        dueDate:  validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DUE_DATE, startDate ? formatDate(startDate): ""),
        requestState: findRequestState(requestDetails?.requeststatuslabel)
      }
      //event bubble up - sets the initial value to validate the required fields
      // handleRequestDetailsInitialValue(requestDetailsObject);
      // createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES, requestDetailsObject);
    },[requestDetails, handleRequestDetailsInitialValue])
    
    const prevConsultFlag = React.useRef(requestDetails?.isconsultflag);

    React.useEffect(() => {
      if (prevConsultFlag.current === true && !requestDetails?.isconsultflag) {
        const calculatedDueDate = startDateText ? dueDateCalculation(startDateText) : "";
        setDueDate(calculatedDueDate);
        // handleRequestDetailsValue(calculatedDueDate, FOI_COMPONENT_CONSTANTS.DUE_DATE);
        // createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DUE_DATE, calculatedDueDate);
      }

      prevConsultFlag.current = requestDetails?.isconsultflag;
    }, [requestDetails?.isconsultflag]);

    const getReceivedDateForLocalState = () => {
      let receivedDate = validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF
      );
      receivedDate = calculateReceivedDate(receivedDate);
      receivedDate = receivedDate ? formatDate(receivedDate) : "";
      return receivedDate;
    }

    const getProcessStartDateForLocalState = () => {
      let processStartDate = validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE,
        getReceivedDateForLocalState()
      );
      processStartDate = processStartDate ? formatDate(processStartDate) : "";
      return processStartDate;
    }
    const [receivedDateText, setReceivedDate] = React.useState(getReceivedDateForLocalState);
    const [startDateText, setStartDate] = React.useState(getProcessStartDateForLocalState);


    //due date calculation
    const dueDateCalculation = (dateText) => {
      return dateText? addBusinessDays(dateText, 30) : "";
    }

    const [dueDateText, setDueDate] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DUE_DATE, getProcessStartDateForLocalState()));

    //local state management for RequestType, ReceivedMode and DeliveryMode
    const [selectedRequestType, setSelectedRequestType] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE));
    const [selectedReceivedMode, setSelectedReceivedMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE));
    const [selectedDeliveryMode, setSelectedDeliveryMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE));

    //generating the menuItems for RequestTypes, ReceivedModes and DeliveryModes
    const requestTypes = requestType.map((item) => {
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const receivedModes = receivedMode.map((item) => {
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select") || (item.name === FOI_COMPONENT_CONSTANTS.ONLINE_FORM && ((!requestDetails.receivedMode) || (requestDetails.receivedMode && requestDetails.receivedMode.toLowerCase() !== FOI_COMPONENT_CONSTANTS.ONLINE_FORM.toLowerCase())))}>{item.name}</MenuItem> )
    });
    const deliveryModes = deliveryMode.map((item) => {
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    //handling the received date change
    const handleReceivedDateChange = (e) => {
      const receivedDate = calculateReceivedDate(e.target.value);
      setReceivedDate(receivedDate);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(receivedDate, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE);
      handleConsultRequestDetailsValue(receivedDate, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RECEIVED_DATE, receivedDate);
    }
    const handleStartDateChange = (e) => {
      setStartDate(e.target.value);
      const dueDate = dueDateCalculation(e.target.value);
      setDueDate(dueDate);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, dueDate);
      handleConsultRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, dueDate);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, e.target.value, dueDate);
    }
    const handleRequestTypeChange = (e) => {
      setSelectedRequestType(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE);
      handleConsultRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.REQUEST_TYPE, e.target.value);
    }
    const handleReceivedModeChange = (e) => {
      setSelectedReceivedMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE);
      handleConsultRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RECEIVED_MODE, e.target.value);
    }
    const handleDeliveryModeChange = (e) => {
      setSelectedDeliveryMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE);
      handleConsultRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DELIVERY_MODE, e.target.value);
    }

    const handleDueDateChange = (e) => {
      const newDueDate = requestDetails?.isconsultflag ? e.target.value : dueDateCalculation(startDateText);
      setDueDate(newDueDate);
      handleRequestDetailsValue(newDueDate, FOI_COMPONENT_CONSTANTS.DUE_DATE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DUE_DATE, newDueDate);
      handleConsultDueDateValidation(newDueDate);
    }

    const handleConsultDueDateChange = (event) => {
      const newDueDate = event.target.value;
      setConsultDueDate(newDueDate);

      // Validate the due date
      const isValid = newDueDate && new Date(newDueDate) >= new Date(requestDetails.receivedDate);
      setIsConsultDueDateValid(isValid);
      handleConsultRequestDetailsValue(event.target.value, FOI_COMPONENT_CONSTANTS.CONSULT_DUE_DATE);
      setUnSavedRequest(true);
      createSaveConsultRequestObject(FOI_COMPONENT_CONSTANTS.CONSULT_DUE_DATE, newDueDate);
    };
    
     return (

      <div className='request-accordian' >
      <Accordion defaultExpanded={true}>
        <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="requestDetails-header">
          <Typography className={classes.heading}>REQUEST DETAILS</Typography>
          {isDataSynced && (
              <Chip
                  icon={<CheckCircleOutlineIcon className="synced-data-icon"/>}
                  label={"Synchronized data"}
                  className="synced-data-chip"
              />
            )}
        </AccordionSummary>
        <AccordionDetails>
          <div>
              <button type="button" className={`btn btn-link btn-description-history`} onClick={() => setModal(true)} 
                disabled={!(!!requestDetails.linkedRequests) || (!!requestDetails.linkedRequests && !requestDetails.linkedRequests?.length >0)}>
                Linked Requests
              </button>
              <MinistriesCanvassed  openModal={openModal} selectedMinistries={(typeof requestDetails.linkedRequests == 'string' ? JSON.parse(requestDetails.linkedRequests) : requestDetails.linkedRequests)} 
              setModal={setModal} isLinkedRequest={true} />
          </div>
          <div className="row foi-details-row foi-details-row-break">
            <div className="col-lg-6 foi-details-col">
                <TextField
                  id="receivedDate"
                  label="Received Date"
                  type="date"
                  value={receivedDateText || ''}
                  onChange={handleReceivedDateChange}
                  inputProps={{ "aria-labelledby": "receivedDate-label"}}
                  InputLabelProps={{
                  shrink: true,
                  }}
                  InputProps={{inputProps: { max: startDateText || formatDate(new Date())} }}
                  variant="outlined"
                  required
                  error={receivedDateText === undefined || receivedDateText === ""}
                  fullWidth
                  disabled={!!ministryId || disableInput || isDataSynced}
                />
                <TextField
                  id="originalDueDate"
                  label="Original Due Date"
                  type={requestDetails?.originalDueDate ? "date" : "text"}
                  value={requestDetails?.originalDueDate || 'N/A'}
                  inputProps={{ "aria-labelledby": "dueDate-label"}}
                  InputLabelProps={{
                  shrink: true,
                  }}
                  variant="outlined"
                  required
                  disabled
                  fullWidth
                />
                <TextField
                  id="dueDate"
                  label="Legislated Due Date"
                  type={(requestDetails?.currentState?.toLowerCase() === StateEnum.onhold.name.toLowerCase() || requestDetails?.currentState?.toLowerCase() === StateEnum.onholdother.name.toLowerCase()) ? "text" : "date"}
                  value={(requestDetails?.currentState?.toLowerCase() === StateEnum.onhold.name.toLowerCase() || requestDetails?.currentState?.toLowerCase() === StateEnum.onholdother.name.toLowerCase()) ? 'N/A' : (dueDateText || '')}
                  onChange={handleDueDateChange}
                  inputProps={{ "aria-labelledby": "dueDate-label"}}
                  InputLabelProps={{
                  shrink: true,
                  }}
                  variant="outlined"
                  required
                  disabled={!requestDetails?.isconsultflag || requestDetails?.currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase() || isDataSynced}
                  fullWidth
                />
            </div>
            <div className="col-lg-6 foi-details-col">
                <TextField
                    id="startDate"
                    label="Start Date"
                    type="date"
                    value={startDateText || ''}
                    onChange={handleStartDateChange}
                    inputProps={{ "aria-labelledby": "startDate-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    InputProps={{inputProps: { min: receivedDateText, max: formatDate(new Date())} }}
                    variant="outlined"
                    required
                    error={startDateText === undefined || startDateText === ""}
                    fullWidth
                    disabled={!!ministryId || disableInput || isDataSynced}
                />
                <TextField
                    id="recordsDueDate"
                    label="Records Due Date"
                    value={requestDetails?.cfrDueDate || 'N/A'}
                    inputProps={{ "aria-labelledby": "startDate-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    InputProps={{inputProps: { min: receivedDateText, max: formatDate(new Date())} }}
                    variant="outlined"
                    required
                    error={startDateText === undefined || startDateText === ""}
                    fullWidth
                    disabled
                />
                {isAddConsultRequest? (
                  <>
                  <TextField
                  id="consultDueDate"
                  label="Consult(s) due date*"
                  type="date"
                  value={consultDueDate}
                  onChange={handleConsultDueDateChange}
                  inputProps={{ "aria-labelledby": "startDate-label"}}
                  InputLabelProps={{
                  shrink: true,
                  }}
                  InputProps={{
                    endAdornment: (
                    <InputAdornment position="start">
                      <Chip
                          icon={
                              <WarningAmberIcon
                              className={clsx(classes.warningAmberIcon)} 
                              />
                          }
                          className={clsx({
                              [classes.showDueDateIcon]: !isConsultDueDateValid,
                              [classes.hideDueDateIcon]: isConsultDueDateValid,
                          })}
                      />
                    </InputAdornment>
                  ),inputProps: { min: receivedDateText } 
                  }}
                  variant="outlined"
                  required
                  error={consultDueDate === undefined || consultDueDate === ""}
                  fullWidth
              />
                <h5
                    className={clsx({
                      [classes.showConsultDueDateFieldValidation]: !isConsultDueDateValid,
                      [classes.hideConsultDueDateFieldValidation]: isConsultDueDateValid,
                    })}
                >This field is required</h5>
                  </>
                ):(
                    <TextField
                    id="closedDate"
                    label="Closed Date"
                    value={requestDetails?.currentState?.toLowerCase() === StateEnum.closed.name.toLowerCase() ?
                      requestDetails?.closedate : "N/A"}
                    inputProps={{ "aria-labelledby": "startDate-label"}}
                    InputLabelProps={{
                    shrink: true,
                    }}
                    InputProps={{inputProps: { min: receivedDateText, max: formatDate(new Date())} }}
                    variant="outlined"
                    required
                    error={startDateText === undefined || startDateText === ""}
                    fullWidth
                    disabled
                    />
                )}
                
                
            </div>
          </div>

          <div className="row foi-details-row">
              <div className="col-lg-6 foi-details-col">
                {!isHistoricalRequest ?
                  <TextField
                        id="requestType"
                        label="Request Type"
                        inputProps={{ "aria-labelledby": "requestType-label"}}
                        InputLabelProps={{ shrink: true, }}
                        select
                        value={selectedRequestType}
                        onChange={handleRequestTypeChange}
                        // input={<Input />}
                        variant="outlined"
                        fullWidth
                        required
                        disabled={disableInput || disableFieldForMinistryRequest || isDataSynced}
                        error={selectedRequestType.toLowerCase().includes("select")}
                    >
                    {requestTypes}
                  </TextField>
                :
                  <TextField
                        id="requestType"
                        label="Request Type"
                        inputProps={{ "aria-labelledby": "requestType-label"}}
                        InputLabelProps={{ shrink: true, }}
                        value={selectedRequestType}
                        onChange={handleRequestTypeChange}
                        // input={<Input />}
                        variant="outlined"
                        fullWidth
                        required
                        disabled
                    >
                  </TextField>
                }

                {!isHistoricalRequest ?
                  <TextField
                        id="deliveryMode"
                        label="Delivery Mode"
                        inputProps={{ "aria-labelledby": "deliveryMode-label"}}
                        InputLabelProps={{ shrink: true, }}
                        select
                        value={selectedDeliveryMode}
                        onChange={handleDeliveryModeChange}
                        input={<Input />}
                        variant="outlined"
                        fullWidth
                        required
                        disabled={disableInput || disableFieldForMinistryRequest}
                        error={selectedDeliveryMode.toLowerCase().includes("select")}
                    >
                    {deliveryModes}
                  </TextField>
                  :
                  <TextField
                        id="deliveryMode"
                        label="Delivery Mode"
                        inputProps={{ "aria-labelledby": "deliveryMode-label"}}
                        InputLabelProps={{ shrink: true, }}
                        value={selectedDeliveryMode}
                        onChange={handleDeliveryModeChange}
                        input={<Input />}
                        variant="outlined"
                        fullWidth
                        disabled
                    >
                  </TextField>
                }
              </div>
              <div className="col-lg-6 foi-details-col">
                {!isHistoricalRequest ?
                  <TextField
                        id="receivedMode"
                        label="Received Mode"
                        inputProps={{ "aria-labelledby": "receivedMode-label"}}
                        InputLabelProps={{ shrink: true, }}
                        select
                        value={selectedReceivedMode}
                        onChange={handleReceivedModeChange}
                        input={<Input />}
                        variant="outlined"
                        fullWidth
                        required
                        error={selectedReceivedMode.toLowerCase().includes("select")}
                        disabled={disableInput ||
                          requestDetails.receivedMode?.toLowerCase() === FOI_COMPONENT_CONSTANTS.ONLINE_FORM.toLowerCase() ||
                          requestDetails.currentState?.toLowerCase() === StateEnum.unopened.name.toLowerCase() ||
                          disableFieldForMinistryRequest
                        }
                    >
                    {receivedModes}
                  </TextField>
                  :
                  <TextField
                        id="receivedMode"
                        label="Received Mode"
                        inputProps={{ "aria-labelledby": "receivedMode-label"}}
                        InputLabelProps={{ shrink: true, }}
                        value={selectedReceivedMode}
                        onChange={handleReceivedModeChange}
                        input={<Input />}
                        variant="outlined"
                        fullWidth
                        disabled
                    >
                  </TextField>
                }
              </div>
          </div>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  });

export default RequestDetails;