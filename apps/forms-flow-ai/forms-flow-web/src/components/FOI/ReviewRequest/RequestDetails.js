import React, {useEffect} from 'react';
import "./requestdetails.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { useSelector } from "react-redux";
import { SelectWithLegend, DateTimeWithLegend } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    root: {
      '& .MuiTextField-root': {
        margin: theme.spacing(1),
        width: '25ch',
      },
    },
  }));
const RequestDetails = React.memo((props) => {
  
    useEffect(() => {       
       
    }, [])
    const requestType = useSelector(state=> state.foiRequests.foiRequestTypeList);

    const receivedMode = useSelector(state=> state.foiRequests.foiReceiveModeList);

    const deliveryMode = useSelector(state=> state.foiRequests.foiDeliveryModeList);

    const receivedDate = {
        "label": "Received Date",
        "value": "2021-05-07",
        "disabled": false,
        "required": true
    }

    const startDate = {
        "label": "Start Date",
        "value": "2021-05-07",
        "disabled": false,
        "required": true
    }

    const dueDate = {
        "label": "Due Date",
        "value": "2021-06-18",
        "disabled": true,
        "required": true
    }

    
    const classes = useStyles();
     return (
        
        <Card className="foi-applicant-details-card">            
            <label className="foi-applcant-details-label">REQUEST DETAILS</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-applicant-details-row">
                    <div className="col-lg-6 foi-applicant-details-col">
                    <SelectWithLegend selectData = {requestType} legend="Request Type" selectDefault="Select Request Type" required={true}/>
                    <SelectWithLegend selectData = {receivedMode} legend="Received Mode" selectDefault="Select Received Mode" required={true}/>
                    <SelectWithLegend selectData = {deliveryMode} legend="Delivery Mode" selectDefault="Select Delivery Mode" required={true}/>                                        
                    </div>
                    <div className="col-lg-6 foi-applicant-details-col">                       
                    <DateTimeWithLegend dateData = {receivedDate} />
                    <DateTimeWithLegend dateData = {startDate} />
                    <DateTimeWithLegend dateData = {dueDate} />
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default RequestDetails;