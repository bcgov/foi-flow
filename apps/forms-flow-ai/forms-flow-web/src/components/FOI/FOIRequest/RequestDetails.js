import React from 'react';
import { useParams } from 'react-router-dom';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { formatDate, addBusinessDays, businessDay } from "../../../helper/FOI/helper";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const RequestDetails = React.memo(({requestDetails, handleRequestDetailsValue, handleRequestDetailsInitialValue, createSaveRequestObject}) => {

    /**
     *  Request details box in the UI
     *  All fields are mandatory here
     */
     const {ministryId} = useParams();  
    const ADD_DAYS = 30;
    const validateFields = (request, name, value) => {
      if (request !== undefined) {
        const startDate = !!request.requestProcessStart ? formatDate(request.requestProcessStart) : "";  
        if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {
          return !!request.requestType ? request.requestType : "Select Request Type";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
          const source = requestDetails.sourceOfSubmission ? requestDetails.sourceOfSubmission : "";
          return !!request.receivedMode ? request.receivedMode : source === FOI_COMPONENT_CONSTANTS.ONLINE_FORM.replace(/\s/g, '').toLowerCase() ? FOI_COMPONENT_CONSTANTS.ONLINE_FORM : "Select Received Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
          return !!request.deliveryMode ? request.deliveryMode : "Select Delivery Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF) {          
          return !!request.receivedDateUF ? request.receivedDateUF : "";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
                 
          return startDate && startDate >= formatDate(value)  ? startDate : value ? value : "";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.DUE_DATE) {
          return request.dueDate ?  request.dueDate : dueDateCalculation(value);
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

    const calculateReceivedDate = (receivedDateString) => {
      const dateString = receivedDateString ? receivedDateString.substring(0,10): "";
      receivedDateString = receivedDateString ? new Date(receivedDateString): "";
      if (receivedDateString !== "" && ((receivedDateString.getHours() > 16 || (receivedDateString.getHours() === 16 && receivedDateString.getMinutes() > 30)) || !businessDay(dateString))) {        
          receivedDateString = addBusinessDays(receivedDateString, 1);
      }
        return receivedDateString;
      }
    //updates the default values from the request details    
    React.useEffect(() => {
      let receivedDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF);     
      receivedDate = calculateReceivedDate(receivedDate);
      const startDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, receivedDate);      
      const requestDetailsObject = {
        requestType: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE),
        receivedMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE),
        deliveryMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE),
        receivedDate: !!receivedDate ? formatDate(receivedDate, 'yyyy MM, dd'): "",
        requestStartDate: startDate ? formatDate(startDate): "",
        dueDate:  validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DUE_DATE, formatDate(startDate)),
      }
      //event bubble up - sets the initial value to validate the required fields      
      handleRequestDetailsInitialValue(requestDetailsObject);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES, requestDetailsObject);
  },[requestDetails, handleRequestDetailsInitialValue])

    //local state management for received date and start date
    let receivedDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF);
    receivedDate = calculateReceivedDate(receivedDate);
    receivedDate = receivedDate ? formatDate(receivedDate): "";
    let processStartDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, receivedDate);
    processStartDate = processStartDate ? formatDate(processStartDate): "";

    const [receivedDateText, setReceivedDate] = React.useState(receivedDate);
    const [startDateText, setStartDate] = React.useState(processStartDate);
    

    //due date calculation
    const dueDateCalculation = (dateText) => {
      return dateText? addBusinessDays(dateText,ADD_DAYS) : "";
    }    

    const [dueDateText, setDueDate] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DUE_DATE, processStartDate));

    //local state management for RequestType, ReceivedMode and DeliveryMode
    const [selectedRequestType, setSelectedRequestType] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE));
    const [selectedReceivedMode, setSelectedReceivedMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE));
    const [selectedDeliveryMode, setSelectedDeliveryMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE));

    //generating the menuItems for RequestTypes, ReceivedModes and DeliveryModes
    const requestTypes = requestType.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const receivedModes = receivedMode.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select") || (item.name === FOI_COMPONENT_CONSTANTS.ONLINE_FORM && window.location.href.indexOf(FOI_COMPONENT_CONSTANTS.ADDREQUEST) > -1)}>{item.name}</MenuItem> )
    });
    const deliveryModes = deliveryMode.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    //handling the received date change
    const handleReceivedDateChange = (e) => {
      setReceivedDate(e.target.value);
      if(new Date(e.target.value) > new Date(startDateText))
        setStartDate(e.target.value);      
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RECEIVED_DATE, e.target.value);
    }
    const handleStartDateChange = (e) => {
      setStartDate(e.target.value);
      const dueDate = dueDateCalculation(e.target.value);
      setDueDate(dueDate);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, dueDate);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, e.target.value, dueDate);
    }  
    const handleRequestTypeChange = (e) => {
      setSelectedRequestType(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.REQUEST_TYPE, e.target.value);
    }
    const handleReceivedModeChange = (e) => {
      setSelectedReceivedMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.RECEIVED_MODE, e.target.value);
    }
    const handleDeliveryModeChange = (e) => {
      setSelectedDeliveryMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DELIVERY_MODE, e.target.value);
    }
     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DETAILS</label>
            <CardContent>            
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                    <TextField
                            id="requestType"
                            label="Request Type"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectedRequestType}
                            onChange={handleRequestTypeChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth
                            required
                            error={selectedRequestType.toLowerCase().includes("select")}                            
                        >            
                        {requestTypes}
                        </TextField> 
                    <TextField
                            id="receivedMode"
                            label="Received Mode"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectedReceivedMode}
                            onChange={handleReceivedModeChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth
                            required
                            error={selectedReceivedMode.toLowerCase().includes("select")}                            
                        >            
                        {receivedModes}
                        </TextField> 
                    <TextField
                            id="deliveryMode"
                            label="Delivery Mode"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectedDeliveryMode}
                            onChange={handleDeliveryModeChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth
                            required
                            error={selectedDeliveryMode.toLowerCase().includes("select")}                            
                        >            
                        {deliveryModes}
                        </TextField> 
                    </div>
                    <div className="col-lg-6 foi-details-col"> 
                    <TextField                
                            label="Received Date"
                            type="date" 
                            value={receivedDateText || ''} 
                            onChange={handleReceivedDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            required
                            error={receivedDateText === undefined || receivedDateText === ""}
                            fullWidth
                            disabled={!!ministryId}
                        />
                        <TextField                
                            label="Start Date"
                            type="date" 
                            value={startDateText || ''} 
                            onChange={handleStartDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            InputProps={{inputProps: { min: receivedDateText} }}
                            variant="outlined" 
                            required
                            error={startDateText === undefined || startDateText === ""}
                            fullWidth
                            disabled={!!ministryId}
                        />
                        <TextField                
                            label="Due Date"
                            type="date" 
                            value={dueDateText || ''}                            
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            required
                            disabled
                            fullWidth
                        />
                    </div>
                </div>                
            </CardContent>
        </Card>
       
    );
  });

export default RequestDetails;