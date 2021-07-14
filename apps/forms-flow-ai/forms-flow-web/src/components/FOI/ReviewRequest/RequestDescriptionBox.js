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
    textField: {
        marginLeft: theme.spacing(1),
        marginRight: theme.spacing(1),
        width: 200,
      },      
      headingError: {
        color: "#ff0000"    
      },
      headingNormal: {
        color: "000000"
      }
  }));

const RequestDescription = React.memo(({      
     requestDetails,       
     handleOnChangeRequestDescription,
     handleInitialValue
    }) => {
    const ministries = useSelector(state=> state.foiRequests.foiProgramAreaList);
    const [checkboxItems, setCheckboxItems] = React.useState(ministries);
    // console.log(`ministries = ${JSON.stringify(ministries)}`)
    React.useEffect(() => {
        const descriptionObject = {
            "startDate": moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"),
            "endDate": moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"),
            "description": !!requestDetails.description ? requestDetails.description : "",
            "isMinistrySelected": !!requestDetails.selectedMinistries
        }    
        handleInitialValue(descriptionObject);
    },[requestDetails])
    React.useEffect(() => {      
        setCheckboxItems(ministries);       
    },[ministries])
    
    const classes = useStyles();
    // const ministries = useSelector(state=> state.foiRequests.foiProgramAreaList);    
    const [startDate, setStartDate] = React.useState(moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"));
    const [endDate, setEndDate] = React.useState(moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"));
    const [requestDescriptionText, setRequestDescription] = React.useState(!!requestDetails.description ? requestDetails.description : "");
    const selectedMinistries = !!requestDetails.selectedMinistries ? requestDetails.selectedMinistries : "";
  
    
    
    if(selectedMinistries !== "") {
        const selectedList = selectedMinistries.map(element => element.code);
        ministries.map(ministry => {
           return ministry.isChecked = !!selectedList.find(selectedMinistry => selectedMinistry === ministry.bcgovcode);           
       });      
    }
    const handleStartDateChange = (event) => {
        setStartDate(event.target.value);
        handleOnChangeRequestDescription(event.target.value, "startDate");
    };      
    const handleEndDateChange = (event) => {
        setEndDate(event.target.value);
        handleOnChangeRequestDescription(event.target.value, "endDate");
    };
    const handleRequestDescriptionChange = (event) => {
        setRequestDescription(event.target.value);
        handleOnChangeRequestDescription(event.target.value, "description");
    };

    const handleMinistrySelected = (isSelected) => {
        // console.log(`newCheckboxes = ${JSON.stringify(newCheckboxes)}`);
        // setCheckboxItems(newCheckboxes);
        handleOnChangeRequestDescription(isSelected, "isMinistrySelected");
    }

    const handleOnChange = (newCheckboxes) => {
        setCheckboxItems(newCheckboxes);
    }
     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
            <CardContent>
                <div className="row foi-details-row">
                    <div className="col-lg-10 foi-request-description-row">
                        <h3>Date Range for Record Search</h3>
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
                    <MinistriesList ministries={checkboxItems} handleMinistrySelected={handleMinistrySelected} handleOnChange={handleOnChange}/>
                    
                    {/* <div className="foi-requestdescription-button-group">
                        <button type="button" className={`btn btn-bottom ${classes.btnenabled}`}>Save Updated Description</button>
                        <button type="button" className={`btn btn-bottom ${isRequieredError ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isRequieredError}  >Split Request</button>
                        <button type="button" className={`btn btn-bottom ${isRequieredError ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={isRequieredError}  >Redirect in Full</button>
      
                    </div> */}
            </CardContent>
        </Card>
       
    );
  });

export default RequestDescription;