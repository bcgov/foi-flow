import React, {useEffect} from 'react';
import "./requestdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import { SelectWithLegend } from '../customComponents';
import TextField from '@material-ui/core/TextField';
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
const RequestDetails = React.memo(({requestDetails}) => {
  
  
    const requestType = useSelector(state=> state.foiRequests.foiRequestTypeList);
    const receivedMode = useSelector(state=> state.foiRequests.foiReceiveModeList);
    const deliveryMode = useSelector(state=> state.foiRequests.foiDeliveryModeList);


    const receivedDate = !!requestDetails.receivedDateUF ? new Date(requestDetails.receivedDateUF) : "";
    const receivedDateString = formatDate(receivedDate);
    const [receivedDateText, setReceivedDate] = React.useState(receivedDateString);
    const [startDateText, setStartDate] = React.useState(receivedDateString);
    const dueDate = new Date(startDateText);
    dueDate.setDate(dueDate.getDate() + 40);
    const dueDateString = formatDate(dueDate);

    const selectedRequestType = !!requestDetails.requestType ? requestDetails.requestType : "Select Request Type";
    
    const handleReceivedDateChange = (e) => {
      setReceivedDate(e.target.value);
    }
    const handleStartDateChange = (e) => {
      setStartDate(e.target.value);
    }
    
    const classes = useStyles();
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">REQUEST DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">
                    <SelectWithLegend selectData = {requestType} legend="Request Type" selectDefault={selectedRequestType}required={true}/>
                    <SelectWithLegend selectData = {receivedMode} legend="Received Mode" selectDefault="Select Received Mode" required={true}/>
                    <SelectWithLegend selectData = {deliveryMode} legend="Delivery Mode" selectDefault="Select Delivery Mode" required={true}/>                                        
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
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default RequestDetails;