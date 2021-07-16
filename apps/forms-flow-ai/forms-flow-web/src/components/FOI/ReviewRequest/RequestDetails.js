import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { formatDate } from "../../../helper/FOI/helper";
import moment from "moment-business-days";

moment.updateLocale('en-ca', {
  workingWeekdays: [1, 2, 3, 4, 5]
});

const RequestDetails = React.memo(({requestDetails, handleRequestDetailsValue, handleRequestDetailsInitialValue}) => {

    /**
     *  Request details box in the UI
     *  All fields are mandatory here
     */ 
    const ADD_DAYS = 30;
    //get the RequestType, ReceivedMode and DeliveryMode master data
    const requestType = useSelector(state=> state.foiRequests.foiRequestTypeList);
    const receivedMode = useSelector(state=> state.foiRequests.foiReceiveModeList);
    const deliveryMode = useSelector(state=> state.foiRequests.foiDeliveryModeList);

    const calculateReceivedDate = (receivedDateString) => {     
      if (receivedDateString !== "" && (receivedDateString.getHours() > 16 || (receivedDateString.getHours() === 16 && receivedDateString.getMinutes() > 30))) {        
        receivedDateString.setDate(receivedDateString.getDate() + 1);
      }
      return receivedDateString;
    }
    //updates the default values from the request details    
    React.useEffect(() => {
      let receivedDate = !!requestDetails.receivedDateUF ? new Date(requestDetails.receivedDateUF) : "";
      receivedDate = calculateReceivedDate(receivedDate);
      const receivedDateString = formatDate(receivedDate);
      const requestDetailsObject = {
        "requestType": !!requestDetails.requestType ? requestDetails.requestType : "Select Request Type",
        "receivedMode": !!requestDetails.receivedMode ? requestDetails.receivedMode : "Select Received Mode",
        "deliveryMode": !!requestDetails.deliveryMode ? requestDetails.deliveryMode : "Select Delivery Mode",
        "receivedDate": receivedDateString,
        "requestStartDate": receivedDateString,
      }
      //event bubble up - sets the initial value to validate the required fields      
      handleRequestDetailsInitialValue(requestDetailsObject);
  },[requestDetails, handleRequestDetailsInitialValue])

    //local state management for received date and start date
    let receivedDate = !!requestDetails.receivedDateUF ? new Date(requestDetails.receivedDateUF) : "";
    receivedDate = calculateReceivedDate(receivedDate);
    const receivedDateString = formatDate(receivedDate);
    const [receivedDateText, setReceivedDate] = React.useState(receivedDateString);
    const [startDateText, setStartDate] = React.useState(receivedDateString);

    //due date calculation
    let dueDate = new Date(receivedDateText);   
    dueDate = moment(dueDate, 'DD-MM-YYYY').businessAdd(ADD_DAYS + 1)._d;    
    const dueDateString = formatDate(dueDate);

    //local state management for RequestType, ReceivedMode and DeliveryMode
    const [selectedRequestType, setSelectedRequestType] = React.useState(!!requestDetails.requestType ? requestDetails.requestType : "Select Request Type");
    const [selectedReceivedMode, setSelectedReceivedMode] = React.useState(!!requestDetails.receivedMode ? requestDetails.receivedMode : "Select Received Mode");
    const [selectedDeliveryMode, setSelectedDeliveryMode] = React.useState(!!requestDetails.deliveryMode ? requestDetails.deliveryMode : "Select Delivery Mode");

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
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, "receivedDate");
    }
    const handleStartDateChange = (e) => {
      setStartDate(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, "requestStartDate");
    }  
    const handleRequestTypeChange = (e) => {
      setSelectedRequestType(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, "requestType");
    }
    const handleReceivedModeChange = (e) => {
      setSelectedReceivedMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, "receivedMode");
    }
    const handleDeliveryModeChange = (e) => {
      setSelectedDeliveryMode(e.target.value);
      //event bubble up - for required feild validation
      handleRequestDetailsValue(e.target.value, "deliveryMode");
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
                            value={receivedDateText} 
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
                            value={startDateText} 
                            onChange={handleStartDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            required
                            error={startDateText === undefined}
                            fullWidth
                        />
                        <TextField                
                            label="Due Date"
                            type="date" 
                            value={dueDateString}                            
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