import React from 'react';
import { useSelector } from "react-redux";
import "./requestdescriptionbox.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { MinistriesList } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';
import moment from 'moment';

const useStyles = makeStyles((theme) => ({
      headingError: {
        color: "#ff0000"    
      },
      headingNormal: {
        color: "000000"
      }
  }));

const RequestDescription = React.memo(({      
    programAreaList, 
    requestDetails,       
     handleOnChangeRequiredRequestDescriptionValues,
     handleInitialRequiredRequestDescriptionValues,
     handleUpdatedProgramAreaList
    }) => {
    

    /* All fields in this component are mandatory */
    
    const classes = useStyles();

    //gets the program area list master data
    var masterProgramAreaList = useSelector(state=> state.foiRequests.foiProgramAreaList);
    
    //updates the default values from the request details    
    React.useEffect(() => {
        const descriptionObject = {
            "startDate": moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"),
            "endDate": moment(new Date(requestDetails.toDate)).format("YYYY-MM-DD"),
            "description": !!requestDetails.description ? requestDetails.description : "",
            "isMinistrySelected": !!requestDetails.selectedMinistries
        }    
        handleInitialRequiredRequestDescriptionValues(descriptionObject);
    },[requestDetails, handleInitialRequiredRequestDescriptionValues])     
    
    //if updated program area list not exists then, update the master list with selected ministries
    if (Object.entries(programAreaList).length === 0){
        const selectedMinistries = !!requestDetails.selectedMinistries ? requestDetails.selectedMinistries : "";     
        
        if(selectedMinistries !== "" && Object.entries(masterProgramAreaList).length !== 0) {
            const selectedList = selectedMinistries.map(element => element.code);
            masterProgramAreaList.map(programArea => {
            return programArea.isChecked = !!selectedList.find(selectedMinistry => selectedMinistry === programArea.bcgovcode);           
        });      
        }
    }
    //if updated program area list exists then use that list instead of master data
    else {
        masterProgramAreaList = programAreaList;       
    }

    //component state management for startDate, endDate and Description
    const [startDate, setStartDate] = React.useState(moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"));
    const [endDate, setEndDate] = React.useState(moment(new Date(requestDetails.toDate)).format("YYYY-MM-DD"));
    const [requestDescriptionText, setRequestDescription] = React.useState(!!requestDetails.description ? requestDetails.description : "");

    //handle onchange of start date and set state with latest value
    const handleStartDateChange = (event) => {
        setStartDate(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, "startDate");
    };
    //handle onchange of end date and set state with latest value
    const handleEndDateChange = (event) => {
        setEndDate(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, "endDate");
    };
    //handle onchange of description and set state with latest value
    const handleRequestDescriptionChange = (event) => {
        setRequestDescription(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, "description");
    };  
    //handle onchange of Program Area List and bubble up the latest data to ReviewRequest
    const handleUpdatedMasterProgramAreaList = (programAreaList) => {
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(programAreaList.some(programArea => programArea.isChecked), "isProgramAreaSelected");     
        //event bubble up - Updated program area list
        handleUpdatedProgramAreaList(programAreaList);
    }
     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
            <CardContent>
                <div className="row foi-details-row">
                    <div className="col-lg-12 foi-request-description-row">
                        <div className="col-lg-6">
                        <h3 className="foi-date-range-h3">Date Range for Record Search</h3>
                        </div>
                        <div className="col-lg-6 foi-request-dates">
                        <TextField                
                            label="Start Date"
                            type="date"
                            value={startDate}
                            className={classes.textField}
                            onChange={handleStartDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}    
                            variant="outlined"                            
                            required
                            error={startDate === undefined}
                            fullWidth
                        />                       
                        <TextField                
                            label="End Date"
                            type="date" 
                            value={endDate}        
                            className={classes.textField}
                            onChange={handleEndDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                             InputProps={{inputProps: { min: startDate} }}
                            variant="outlined"                            
                            required
                            error={endDate === undefined}
                            fullWidth
                        />  
                        </div>                                                              
                    </div>
                    </div>
                    <div className="foi-request-description-textbox">
                    <TextField
                        id="outlined-multiline-request-description"
                        required={true}
                        label="Request Description"
                        multiline
                        rows={4}
                        value={requestDescriptionText}
                        variant="outlined"
                        InputLabelProps={{ shrink: true, }} 
                        onChange={handleRequestDescriptionChange}
                        error={requestDescriptionText===""}
                        fullWidth
                     />        
                    </div>
                    { Object.entries(masterProgramAreaList).length !== 0 ?
                    <MinistriesList masterProgramAreaList={masterProgramAreaList} handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList} />
                    :null}
            </CardContent>
        </Card>
       
    );
  });

export default RequestDescription;