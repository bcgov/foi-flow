import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { formatDate, addBusinessDays } from "../../../helper/FOI/helper";
import moment from "moment-business-days";
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';


moment.updateLocale('en-ca', {
  workingWeekdays: [1, 2, 3, 4, 5]
});

const RequestDetails = React.memo(({requestDetails, handleRequestDetailsValue, handleRequestDetailsInitialValue, createSaveRequestObject}) => {

    /**
     *  Request details box in the UI
     *  All fields are mandatory here
     */ 
    const ADD_DAYS = 30;
    const validateFields = (request, name, value) => {
      if (request !== undefined) {
        if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {
          return !!request.requestType ? request.requestType : "Select Request Type";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
          return !!request.receivedMode ? request.receivedMode : "Select Received Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
          return !!request.deliveryMode ? request.deliveryMode : "Select Delivery Mode";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF) {
          return !!request.receivedDateUF ? new Date(request.receivedDateUF) : "";
        }
        else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
          return !!request.requestProcessStart ? formatDate(request.requestProcessStart) : value ? value : "";
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
      if (receivedDateString !== "" && (receivedDateString.getHours() > 16 || (receivedDateString.getHours() === 16 && receivedDateString.getMinutes() > 30))) {
        receivedDateString = addBusinessDays(formatDate(receivedDateString), 1);
      }
      return receivedDateString;
    }
    //updates the default values from the request details    
    React.useEffect(() => {
      let receivedDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF);     
      receivedDate = calculateReceivedDate(receivedDate);
      const startDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, receivedDate);
      const dueDate = dueDateCalculation(startDate);
      const requestDetailsObject = {
        requestType: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE),
        receivedMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE),
        deliveryMode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE),
        receivedDate: !!receivedDate ? receivedDate: "",
        requestStartDate: startDate,
        dueDate: dueDate,
      }
      //event bubble up - sets the initial value to validate the required fields      
      handleRequestDetailsInitialValue(requestDetailsObject);
  },[requestDetails, handleRequestDetailsInitialValue])

    //local state management for received date and start date
    let receivedDate = validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_DATE_UF);
    receivedDate = formatDate(calculateReceivedDate(receivedDate));    
    const [receivedDateText, setReceivedDate] = React.useState(receivedDate);
    const [startDateText, setStartDate] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE, receivedDate));
    

    //due date calculation
    const dueDateCalculation = (dateText) => {
      return dateText? addBusinessDays(dateText,ADD_DAYS) : "";
    }    

    const [dueDateText, setDueDate] = React.useState(dueDateCalculation(startDateText));

    //local state management for RequestType, ReceivedMode and DeliveryMode
    const [selectedRequestType, setSelectedRequestType] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.REQUEST_TYPE));
    const [selectedReceivedMode, setSelectedReceivedMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.RECEIVED_MODE));
    const [selectedDeliveryMode, setSelectedDeliveryMode] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.DELIVERY_MODE));

    //generating the menuItems for RequestTypes, ReceivedModes and DeliveryModes
    const requestTypes = requestType.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const receivedModes = receivedMode.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
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
      handleRequestDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE);
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
                            error={receivedDateText === undefined}
                            fullWidth
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
                            error={startDateText === undefined}
                            fullWidth
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