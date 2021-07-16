import React, { useEffect }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import './reviewrequest.scss';
import ReviewRequestHeader from './ReviewRequestHeader';
import ApplicantDetails from './ApplicantDetails';
import ChildDetails from './ChildDetails';
import OnBehalfOfDetails from './OnBehalfOfDetails';
import AddressContactDetails from './AddressContanctInfo';
import RequestDescriptionBox from './RequestDescriptionBox';
import RequestDetails from './RequestDetails';
import AdditionalApplicantDetails from './AdditionalApplicantDetails';
import RequestNotes from './RequestNotes';
import BottomButtonGroup from './BottomButtonGroup';
import { useParams } from 'react-router-dom';
import { fetchFOIRequestDetails, fetchFOICategoryList, fetchFOIProgramAreaList } from "../../../apiManager/services/FOI/foiRequestServices";
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
    //   width: '25ch',
    },
  },
}));
const ReviewRequest = React.memo((props) => {
  const {requestId} = useParams();

  //gets the request detail from the store
  const requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
  
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchFOIRequestDetails(requestId));   
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
  },[requestId, dispatch]); 

  const requiredRequestDescriptionDefaultData = {
    "startDate": "",
    "endDate": "",
    "description": "",
    "isProgramAreaSelected": false
  }  

  const requiredRequestDetailsInitialValues = {
    "requestType":"",
    "receivedMode": "",
    "deliveryMode": "",
    "receivedDate": "",
    "requestStartDate": "",
  }
  
  //below states are used to find if required fields are set or not
  const [requiredRequestDescriptionValues, setRequiredRequestDescriptionValues] = React.useState(requiredRequestDescriptionDefaultData);
  const [requiredRequestDetailsValues, setRequiredRequestDetailsValues] = React.useState(requiredRequestDetailsInitialValues);
  const [selectCategoryValue, setSelectCategoryValue] = React.useState("Select Category");
  const [assignedToValue, setAssignedToValue] = React.useState("Unassigned");

  //get the initial value of the required fields to enable/disable bottom button at the initial load of review request
  const handleInitialRequiredRequestDescriptionValues = React.useCallback((requestDescriptionObject) => {
    setRequiredRequestDescriptionValues(requestDescriptionObject);
  },[])
  const handleRequestDetailsInitialValue = React.useCallback((value) => {    
    setRequiredRequestDetailsValues(value);
  },[])
  const handleAssignedToInitialValue = React.useCallback((value) => {    
    setAssignedToValue(value);
  },[])
  const handleCategoryInitialValue = React.useCallback((value) => {    
    setSelectCategoryValue(value);
  },[])

  //Update required fields of request description box with latest value
  const handleOnChangeRequiredRequestDescriptionValues = (value, name) => {
    const descriptionData = {...requiredRequestDescriptionValues};
    if(name === "startDate") {      
      descriptionData.startDate = value;      
    }    
    else if(name === "endDate") {    
      descriptionData.endDate = value;      
    }
    else if (name === "description") {     
      descriptionData.description = value;      
    }
    else if (name === "isProgramAreaSelected") {
      descriptionData.isProgramAreaSelected = value;      
    }
    setRequiredRequestDescriptionValues(descriptionData);
  }
  
  //Update required fields of request details box with latest value
  const handleRequestDetailsValue = (value, name) => {
    const detailsData = {...requiredRequestDetailsValues};
    if (name === "requestTpe") {
      detailsData.requestType = value;
    }
    else if (name === "receivedMode") {
      detailsData.receivedMode = value;
    }
    else if (name === "deliveryMode") {
      detailsData.deliveryMode = value;
    }
    setRequiredRequestDetailsValues(detailsData);
  }

  //gets the latest assigned to value
  const handleAssignedToValue = (value) => {
    setAssignedToValue(value);
  }

  //gets the latest category value
  const handleCategoryValue = (value) => {
    setSelectCategoryValue(value);
  }

  //handle email validation
  const [validation, setValidation] = React.useState({});
  const handleEmailValidation = (validationObj) => {    
    setValidation(validationObj);
  }

  //to get the updated program area list with isChecked=true/false
  const [programAreaList, setProgramAreaList] = React.useState([]);
  
  const handleUpdatedProgramAreaList = (programAreaList) => {    
    //get the updated program area list with isChecked=true/false
    setProgramAreaList(programAreaList); 
  } 

  //Variable to find if all required fields are filled or not
  const isValidationError = (
    requiredRequestDescriptionValues.startDate === undefined || requiredRequestDescriptionValues.endDate === undefined 
    || requiredRequestDescriptionValues.description === ""
    || !requiredRequestDescriptionValues.isProgramAreaSelected
    || selectCategoryValue.toLowerCase().includes("select")
    || (validation.helperTextValue !== undefined && validation.helperTextValue !== "")
    || assignedToValue.toLowerCase().includes("unassigned")
    || requiredRequestDetailsValues.requestType.toLowerCase().includes("select")
    || requiredRequestDetailsValues.receivedMode.toLowerCase().includes("select")
    || requiredRequestDetailsValues.deliveryMode.toLowerCase().includes("select")
    || requiredRequestDetailsValues.receivedDate === undefined
    || requiredRequestDetailsValues.requestStartDate === undefined 
    );

  const classes = useStyles();
     return (
      <div className="container foi-review-request-container">      
        <div className="col-sm-12 col-md-12 foi-review-container">
        <form className={classes.root} autoComplete="off">        
        {Object.entries(requestDetails).length !== 0 ? (
          <>
          <ReviewRequestHeader requestDetails={requestDetails} handleAssignedToInitialValue={handleAssignedToInitialValue} handleAssignedToValue={handleAssignedToValue}/>
          <ApplicantDetails requestDetails={requestDetails} handleCategoryInitialValue={handleCategoryInitialValue} handleEmailValidation={handleEmailValidation} handleCategoryValue={handleCategoryValue} /> 
          {requestDetails.additionalPersonalInfo !== undefined && requestDetails.additionalPersonalInfo.childFirstName !== undefined ?
          <ChildDetails additionalInfo={requestDetails.additionalPersonalInfo}/> : null }          
           {requestDetails.additionalPersonalInfo !== undefined && requestDetails.additionalPersonalInfo.anotherFirstName !== undefined ?
          <OnBehalfOfDetails additionalInfo={requestDetails.additionalPersonalInfo} /> : null }          
          <AddressContactDetails requestDetails={requestDetails} />
          <RequestDescriptionBox programAreaList={programAreaList} requestDetails = {requestDetails} handleUpdatedProgramAreaList={handleUpdatedProgramAreaList} handleOnChangeRequiredRequestDescriptionValues={handleOnChangeRequiredRequestDescriptionValues} handleInitialRequiredRequestDescriptionValues={handleInitialRequiredRequestDescriptionValues} />
          <RequestDetails  requestDetails={requestDetails} handleRequestDetailsValue={handleRequestDetailsValue} handleRequestDetailsInitialValue={handleRequestDetailsInitialValue}/>
          {requestDetails.additionalPersonalInfo !== undefined ?
          <AdditionalApplicantDetails additionalInfo={requestDetails.additionalPersonalInfo}/>: null }
          <RequestNotes />
          
          <BottomButtonGroup isValidationError = {isValidationError}/>
          </>
           ): null}
           </form>
        </div>
      </div>
    
    );
  });

export default ReviewRequest;