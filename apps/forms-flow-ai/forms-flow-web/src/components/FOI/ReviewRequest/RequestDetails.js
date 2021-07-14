import React, {useEffect} from 'react';
import "./requestdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import { SelectWithLegend } from '../customComponents';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import { makeStyles } from '@material-ui/core/styles';
import { formatDate } from "../../../helper/helper";

const useStyles = makeStyles((theme) => ({
    root: {
      '& .MuiTextField-root': {
        margin: theme.spacing(1),
        width: '25ch',
      },
    },
  }));
const RequestDetails = React.memo(({requestDetails, requestDetailsValues, handleRequestDetailsValue, handleRequestDetailsInitialValue}) => {
    
    const requestType = useSelector(state=> state.foiRequests.foiRequestTypeList);
    const receivedMode = useSelector(state=> state.foiRequests.foiReceiveModeList);
    const deliveryMode = useSelector(state=> state.foiRequests.foiDeliveryModeList);

    React.useEffect(() => {
      const receivedDate = !!requestDetails.receivedDateUF ? new Date(requestDetails.receivedDateUF) : "";
      const receivedDateString = formatDate(receivedDate);
      const requestDetailsObject = {
        "requestType": !!requestDetails.requestType ? requestDetails.requestType : "Select Request Type",
        "receivedMode": !!requestDetails.receivedMode ? requestDetails.receivedMode : "Select Received Mode",
        "deliveryMode": !!requestDetails.deliveryMode ? requestDetails.deliveryMode : "Select Delivery Mode",
        "receivedDate": receivedDateString,
        "requestStartDate": receivedDateString,
      }
      // const requestTpeValue = !!requestDetails.requestType ? requestDetails.requestType : "Select Request Type";        
      handleRequestDetailsInitialValue(requestDetailsObject);
  },[])

    const receivedDate = !!requestDetails.receivedDateUF ? new Date(requestDetails.receivedDateUF) : "";
    const receivedDateString = formatDate(receivedDate);
    const [receivedDateText, setReceivedDate] = React.useState(receivedDateString);
    const [startDateText, setStartDate] = React.useState(receivedDateString);
    const dueDate = new Date(startDateText);
    dueDate.setDate(dueDate.getDate() + 40);
    const dueDateString = formatDate(dueDate);

    // const selectedRequestType = !!requestDetails.requestType ? requestDetails.requestType : "Select Request Type";
    const [selectedRequestType, setSelectedRequestType] = React.useState(!!requestDetails.requestType ? requestDetails.requestType : "Select Request Type");
    const [selectedReceivedMode, setSelectedReceivedMode] = React.useState(!!requestDetails.receivedMode ? requestDetails.receivedMode : "Select Received Mode");
    const [selectedDeliveryMode, setSelectedDeliveryMode] = React.useState(!!requestDetails.deliveryMode ? requestDetails.deliveryMode : "Select Delivery Mode");

    const requestTypes = requestType.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const receivedModes = receivedMode.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const deliveryModes = deliveryMode.map((item) => {    
      return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
    });
    const handleReceivedDateChange = (e) => {
      setReceivedDate(e.target.value);
      handleRequestDetailsValue(e.target.value, "receivedDate");
    }
    const handleStartDateChange = (e) => {
      setStartDate(e.target.value);
      handleRequestDetailsValue(e.target.value, "requestStartDate");
    }  
    const handleRequestTypeChange = (e) => {
      setSelectedRequestType(e.target.value);
      handleRequestDetailsValue(e.target.value, "requestType");
    }
    const handleReceivedModeChange = (e) => {
      setSelectedReceivedMode(e.target.value);
      handleRequestDetailsValue(e.target.value, "receivedMode");
    }
    const handleDeliveryModeChange = (e) => {
      setSelectedDeliveryMode(e.target.value);
      handleRequestDetailsValue(e.target.value, "deliveryMode");
    }
    const classes = useStyles();
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">REQUEST DETAILS</label>
            <CardContent>
            {/* <form className={classes.root} noValidate autoComplete="off"> */}
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">
                    {/* <SelectWithLegend id="requestType" selectData = {requestType} legend="Request Type" selectDefault={selectedRequestType}required={true}/> */}
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
                    {/* <SelectWithLegend id="receivedMode" selectData = {receivedMode} legend="Received Mode" selectDefault="Select Received Mode" required={true}/> */}
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
                    {/* <SelectWithLegend id="deliveryMode" selectData = {deliveryMode} legend="Delivery Mode" selectDefault="Select Delivery Mode" required={true}/>                                         */}
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
                    <div className="col-lg-6 foi-applicant-details-col"> 
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
                        />
                        <TextField                
                            label="Due Date"
                            type="date" 
                            value={dueDateString} 
                            // onChange={handleDOBChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            variant="outlined" 
                            required
                            disabled
                        />
                    </div>
                </div> 
                {/* </form>              */}
            </CardContent>
        </Card>
       
    );
  });

export default RequestDetails;