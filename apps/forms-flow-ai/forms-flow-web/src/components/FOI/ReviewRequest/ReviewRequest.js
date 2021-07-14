import React, { useEffect }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import moment from 'moment';
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
import { fetchFOICategoryList, fetchFOIProgramAreaList } from "../../../apiManager/services/FOI/foiRequestServices";
import { useParams } from 'react-router-dom';
import { fetchFOIRequestDetails } from "../../../apiManager/services/FOI/foiRequestServices";

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
  const selectedCategory = useSelector(state=> state.foiRequests.foiSelectedCategory);
  const requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);  
  const requiredFields = useSelector(state=> state.foiRequests.foirequiredFields);

  const dispatch = useDispatch(); 
  useEffect(()=>{    
    dispatch(fetchFOIRequestDetails(requestId));   
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
  },[requestId, dispatch]);

  const selectDefaultCategoryValue = Object.entries(requestDetails).length !== 0 && requestDetails.currentState !== "Unopened"? "Select Category":"Select Category";
  const selectDefaultAssignedToValue = Object.entries(requestDetails).length !== 0 && requestDetails.currentState !== "Unopened"? requestDetails.assignedTo:"Unassigned";
  const [selectCategoryValue, setSelectCategoryValue] = React.useState(selectDefaultCategoryValue);
  const [selectAssignedToValue, setSelectAssignedToValue] = React.useState(selectDefaultAssignedToValue);

  // const requestStartDate = Object.entries(requestDetails).length !== 0 ? new Date(requestDetails.fromDate):"";
  // const requestEndDate = Object.entries(requestDetails).length !== 0 ? new Date(requestDetails.fromDate):"";
  // const description = Object.entries(requestDetails).length !== 0 && !!requestDetails.description ? requestDetails.description : "";
  // const [startDate, setStartDate] = React.useState(moment(requestStartDate).format("YYYY-MM-DD"));
  // const [endDate, setEndDate] = React.useState(moment(requestEndDate).format("YYYY-MM-DD"));
  // const [requestDescriptionText, setRequestDescription] = React.useState(Object.entries(requestDetails).length !== 0 && !!requestDetails.description ? requestDetails.description : "");

  
  const requestDescriptionBoxDefaultData = {
    "startDate": "",
    "endDate": "",
    "description": "",
    "isMinistrySelected": false
  }  

  const [requestDescriptionBoxData, setRequestDescriptionBoxData] = React.useState(requestDescriptionBoxDefaultData);
  
  const handleCategoryOnChange = (e) => {
    setSelectCategoryValue(e.target.value);
  }
  const handleAssignedToOnChange = (e) => {
    setSelectAssignedToValue(e.target.value);
  }

  const handleOnChangeRequestDescription = (value, name) => {

    console.log(`value = ${value}, name = ${name}`);
    if(name === "startDate") {
      const descriptionData = {...requestDescriptionBoxData};
      descriptionData.startDate = value;
      setRequestDescriptionBoxData(descriptionData);
    }    
    else if(name === "endDate") {
      const descriptionData = {...requestDescriptionBoxData};
      descriptionData.endDate = value;
      setRequestDescriptionBoxData(descriptionData);
    }
    else if (name === "description") {
      const descriptionData = {...requestDescriptionBoxData};
      descriptionData.description = value;
      setRequestDescriptionBoxData(descriptionData);
    }
    else if (name === "isMinistrySelected") {
      
      const descriptionData = {...requestDescriptionBoxData};
      descriptionData.isMinistrySelected = value;
      console.log(`descriptionData == ${JSON.stringify(descriptionData)}`);
      // setRequestDescriptionBoxData(descriptionData);
    }
  }
  const handleInitialValue = (requestDescriptionObject) => {
    setRequestDescriptionBoxData(requestDescriptionObject);
  }
  // console.log(`descriptionData = ${JSON.stringify(requestDescriptionBoxData)}`);
  const isRequieredError = (requestDescriptionBoxData.startDate === undefined || requestDescriptionBoxData.endDate === undefined 
    || requestDescriptionBoxData.description === ""
    || selectCategoryValue.toLowerCase().includes("select") 
    || selectAssignedToValue.toLowerCase().includes("unassigned"));

  const classes = useStyles();
     return (
      <div className="container foi-review-request-container">           
        <div className="col-sm-12 col-md-12 foi-review-container">
        <form className={classes.root} autoComplete="off">
        {requestDetails.description !== undefined ? (
          <>
          <ReviewRequestHeader selectAssignedToValue={selectAssignedToValue} handleAssignedToOnChange={handleAssignedToOnChange} />
          <ApplicantDetails requestDetails={requestDetails} handleCategoryOnChange={handleCategoryOnChange} selectCategoryValue={selectCategoryValue} />
          {requestDetails.additionalpersonalInfo !== undefined && requestDetails.additionalpersonalInfo.childFirstName !== undefined ?
          <ChildDetails additionalInfo={requestDetails.additionalpersonalInfo}/> : null }          
           {requestDetails.additionalpersonalInfo !== undefined && requestDetails.additionalpersonalInfo.anotherFirstName !== undefined ?
          <OnBehalfOfDetails additionalInfo={requestDetails.additionalpersonalInfo} /> : null }          
          <AddressContactDetails requestDetails={requestDetails} />
          <RequestDescriptionBox requestDetails = {requestDetails} isRequieredError = {isRequieredError} requestDescriptionBoxData={requestDescriptionBoxData} handleOnChangeRequestDescription={handleOnChangeRequestDescription} handleInitialValue={handleInitialValue} />
          <RequestDetails  requestDetails={requestDetails}/>
          {requestDetails.additionalpersonalInfo !== undefined ?
          <AdditionalApplicantDetails additionalInfo={requestDetails.additionalpersonalInfo}/>: null }
          <RequestNotes />
          
          <BottomButtonGroup selectedCategory = {selectedCategory} isRequieredError = {isRequieredError}/>
          </>
           ): null}
           </form>
        </div>
      </div>
    
    );
  });

export default ReviewRequest;