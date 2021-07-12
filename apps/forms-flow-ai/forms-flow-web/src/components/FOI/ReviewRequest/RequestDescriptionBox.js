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
      btndisabled: {
        border: 'none',
        backgroundColor: '#eceaea',
        color: '#FFFFFF'
      },
      btnenabled: {
        border: 'none',
        backgroundColor: '#38598A',
        color: '#FFFFFF'
      },
      btnsecondaryenabled: {
        border: '1px solid #38598A',
        backgroundColor: '#FFFFFF',
        color: '#38598A'
      }
  }));

const RequestDescription = React.memo(({selectedCategory, requestDetails}) => {
   
    const classes = useStyles();
    const ministries = useSelector(state=> state.foiRequests.foiProgramAreaList);
    
    const [startDate, setStartDate] = React.useState(moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"));
    const [endDate, setEndDate] = React.useState(moment(new Date(requestDetails.fromDate)).format("YYYY-MM-DD"));
    const [requestDescriptionText, setRequestDescription] = React.useState(!!requestDetails.description ? requestDetails.description : "");
    const selectedMinistries = !!requestDetails.selectedMinistries ? requestDetails.selectedMinistries : "";
    
    if(selectedMinistries !== "") {
        const selectedList = selectedMinistries.map(element => element.code);
         ministries.map(ministry => {
            ministry.isChecked = !!selectedList.find(selectedMinistry => selectedMinistry === ministry.bcgovcode);           
       });      
    }

    const handleStartDateChange = (event) => {
        setStartDate(event.target.value);
    };      
    const handleEndDateChange = (event) => {
        setEndDate(event.target.value);
    };
    const handleRequestDescriptionChange = (event) => {
        setRequestDescription(event.target.value);
    };

     return (
        
        <Card className="foi-request-description-card">            
            <label className="foi-request-description-label">REQUEST DESCRIPTION</label>
            <CardContent>
            {/* <form className={classes.root} noValidate autoComplete="off"> */}
                <div className="row foi-request-description-row">
                    <div className="col-lg-10 foi-request-description-row1">
                        <h3>Date Range for Record Search</h3>
                        <TextField                
                            label="Start Date"
                            type="date"                
                            // defaultValue={dateData.value}                
                            value={startDate}        
                            className={classes.textField}
                            onChange={handleStartDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                            // InputProps={{inputProps: { min: "2001-04-21", max: "2020-05-04"} }}
                            variant="outlined"                            
                            required
                        />

                        <TextField                
                            label="End Date"
                            type="date"                
                            // defaultValue={dateData.value}                
                            value={endDate}        
                            className={classes.textField}
                            onChange={handleEndDateChange}
                            InputLabelProps={{
                            shrink: true,
                            }}
                             InputProps={{inputProps: { min: startDate} }}
                            variant="outlined"                            
                            required
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
                     />        
                    </div>
                    <MinistriesList ministries={ministries}/>
                    <div className="foi-requestdescription-button-group">
                        <button type="button" className={`btn btn-bottom ${classes.btnenabled}`}>Save Updated Description</button>
                        <button type="button" className={`btn btn-bottom ${selectedCategory === '' ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={selectedCategory === ''}  >Split Request</button>
                        <button type="button" className={`btn btn-bottom ${selectedCategory === '' ? classes.btndisabled : classes.btnsecondaryenabled}`} disabled={selectedCategory === ''}  >Redirect in Full</button>
      
                    </div>
                   
                {/* </form>              */}
            </CardContent>
        </Card>
       
    );
  });

export default RequestDescription;