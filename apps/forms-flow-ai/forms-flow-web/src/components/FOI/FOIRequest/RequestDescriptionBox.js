import React, { useEffect } from 'react';
import { useSelector } from "react-redux";
import "./requestdescriptionbox.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { MinistriesList } from '../customComponents';
import { makeStyles } from '@material-ui/core/styles';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { StateEnum } from '../../../constants/FOI/statusEnum';
import { formatDate } from "../../../helper/FOI/helper";
import RequestDescriptionHistory from "../RequestDescriptionHistory";
import { useParams } from 'react-router-dom';

const useStyles = makeStyles((theme) => ({
      headingError: {
        color: "#ff0000"    
      },
      headingNormal: {
        color: "000000"
      },
      btndisabled: { 
        color: "#808080"
      }
  }));

const RequestDescription = React.memo(({     
    programAreaList, 
    requestDetails,       
    handleOnChangeRequiredRequestDescriptionValues,
    handleInitialRequiredRequestDescriptionValues,
    handleUpdatedProgramAreaList,
    createSaveRequestObject,
    disableInput
}) => {
    
    
    /* All fields in this component are mandatory */
    
    const classes = useStyles();
    const {ministryId} = useParams();
    //gets the program area list master data
    var masterProgramAreaList = useSelector(state=> state.foiRequests.foiProgramAreaList);
    var requestDescriptionHistoryList = useSelector(state=> state.foiRequests.foiRequestDescriptionHistoryList);    
    //updates the default values from the request description box    
    useEffect(() => {
        const descriptionObject = {
            startDate: !!requestDetails.fromDate ? formatDate(new Date(requestDetails.fromDate)): "",
            endDate: !!requestDetails.toDate ? formatDate(new Date(requestDetails.toDate)): "",
            description: !!requestDetails.description ? requestDetails.description : "",
            isProgramAreaSelected: !!requestDetails.selectedMinistries,
            isPiiRedacted: ministryId ? true : !!requestDetails.ispiiredacted
        }    
        handleInitialRequiredRequestDescriptionValues(descriptionObject);
    },[requestDetails, handleInitialRequiredRequestDescriptionValues])     
    
    useEffect(() => {
      //if updated program area list not exists then, update the master list with selected ministries
      if (Object.entries(programAreaList).length === 0) {
        const selectedMinistries = !!requestDetails.selectedMinistries
          ? requestDetails.selectedMinistries
          : "";
        if (
          selectedMinistries !== "" &&
          Object.entries(masterProgramAreaList).length !== 0
        ) {
          const selectedList = selectedMinistries.map(
            (element) => element.code
          );
          masterProgramAreaList = masterProgramAreaList.map((programArea) => {
            programArea.isChecked = !!selectedList.find(
              (selectedMinistry) => selectedMinistry === programArea.bcgovcode
            );
            return programArea;
          });
        } else {
          //if it is add request then keep all check boxes unchecked
          masterProgramAreaList = masterProgramAreaList.map((programArea) => {
            programArea.isChecked = false;
            return programArea;
          });
        }
      }
      //if updated program area list exists then use that list instead of master data
      else {
        masterProgramAreaList = programAreaList;
      }
    }, [programAreaList]);

    //component state management for startDate, endDate and Description
    const [startDate, setStartDate] = React.useState(!!requestDetails.fromDate ? formatDate(new Date(requestDetails.fromDate)): "");
    const [endDate, setEndDate] = React.useState(!!requestDetails.toDate ? formatDate(new Date(requestDetails.toDate)): "");
    const [requestDescriptionText, setRequestDescription] = React.useState(!!requestDetails.description ? requestDetails.description : "");
    const [isPIIRedacted, setPIIRedacted] = React.useState(ministryId ? true : !!requestDetails.ispiiredacted);

    const handlePIIRedacted = (event) => {
        setPIIRedacted(event.target.checked);
        handleOnChangeRequiredRequestDescriptionValues(event.target.checked, FOI_COMPONENT_CONSTANTS.ISPIIREDACTED)
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.ISPIIREDACTED, event.target.checked);
    }
    //handle onchange of start date and set state with latest value
    const handleStartDateChange = (event) => {
        setStartDate(event.target.value);
        if(endDate === "" || new Date(event.target.value) > new Date(endDate))
          setEndDate(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, FOI_COMPONENT_CONSTANTS.START_DATE);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.START_DATE, event.target.value);
    };
    //handle onchange of end date and set state with latest value
    const handleEndDateChange = (event) => {
        setEndDate(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, FOI_COMPONENT_CONSTANTS.END_DATE);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.END_DATE, event.target.value);
    };
    //handle onchange of description and set state with latest value
    const handleRequestDescriptionChange = (event) => {
        setRequestDescription(event.target.value);
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(event.target.value, FOI_COMPONENT_CONSTANTS.DESCRIPTION);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.DESCRIPTION, event.target.value);
    };  
    //handle onchange of Program Area List and bubble up the latest data to ReviewRequest
    const handleUpdatedMasterProgramAreaList = (updatedProgramAreaList) => {
        //event bubble up- update the required fields to validate later
        handleOnChangeRequiredRequestDescriptionValues(updatedProgramAreaList.some(programArea => programArea.isChecked), FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED);     
        //event bubble up - Updated program area list
        handleUpdatedProgramAreaList(updatedProgramAreaList);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST, updatedProgramAreaList);
    }

    const [openModal, setOpenModal] = React.useState(false);
    const handleDescriptionHistoryClick = () => {
        setOpenModal(true);
    }
    const handleModalClose = () => {
        setOpenModal(false);
    }
    
    const filteredList = requestDescriptionHistoryList.filter((request, index, self) =>
        index === self.findIndex((copyRequest) => (
            copyRequest.description === request.description && copyRequest.fromDate === request.fromDate && copyRequest.toDate === request.toDate
        ))
    )
    const sortedList = filteredList.sort((a, b) => {       
        return new Date(a.createdAt) - new Date(b.createdAt);
    });

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">REQUEST DESCRIPTION</label>
            <CardContent>
                <RequestDescriptionHistory requestDescriptionHistoryList={sortedList} openModal={openModal} handleModalClose={handleModalClose}/>
                <div className="row foi-details-row">
                <div className="foi-request-description-history">
                    <button type="button" className={`btn btn-link btn-description-history ${sortedList.length <= 1 ? classes.btndisabled : ""}`} disabled={sortedList.length <= 1}  onClick={handleDescriptionHistoryClick}>
                       Description History
                    </button>
                </div>
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
                            InputProps={{inputProps: { max: formatDate(new Date())} }}   
                            variant="outlined"
                            fullWidth
                            disabled={disableInput}
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
                             InputProps={{inputProps: { min: startDate , max: formatDate(new Date())} }}
                            variant="outlined" 
                            fullWidth
                            disabled={disableInput}
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
                        disabled={disableInput}
                    />
                    <label className={`check-item no-personal-info ${!isPIIRedacted ? classes.headingError : ""}`}>                  
                    <input
                        type="checkbox"
                        className="checkmark"
                        checked={isPIIRedacted}
                        onChange={handlePIIRedacted}
                        disabled={disableInput || (isPIIRedacted && (requestDetails.currentState && requestDetails.currentState.toLowerCase() !== StateEnum.unopened.name.toLowerCase()))}
                    />
                    <span className="checkmark"></span>
                        Description contains NO Personal Information
                    </label>      
                    </div>
                    { Object.entries(masterProgramAreaList).length !== 0 ?
                    <MinistriesList masterProgramAreaList={masterProgramAreaList} handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList} disableInput={disableInput} />
                    :null}
            </CardContent>
        </Card>
       
    );
  });

export default RequestDescription;