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
import { fetchFOIRequestDetails, fetchFOICategoryList, fetchFOIProgramAreaList, fetchFOIAssignedToList, fetchFOIDeliveryModeList, fetchFOIReceivedModeList } from "../../../apiManager/services/FOI/foiRequestServices";
import { makeStyles } from '@material-ui/core/styles';

import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),  
    },
  },
}));

const ReviewRequest = React.memo((props) => {
  const {requestId} = useParams();  

  //gets the request detail from the store
  const requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchFOIRequestDetails(requestId));   
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
    dispatch(fetchFOIAssignedToList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
  },[requestId, dispatch]); 

  useEffect(() => {
    setSaveRequestObject(requestDetails);
  },[requestDetails]);

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
    if(name === FOI_COMPONENT_CONSTANTS.START_DATE) {      
      descriptionData.startDate = value;      
    }    
    else if(name === FOI_COMPONENT_CONSTANTS.END_DATE) {    
      descriptionData.endDate = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.DESCRIPTION) {     
      descriptionData.description = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.IS_PROGRAM_AREA_SELECTED) {
      descriptionData.isProgramAreaSelected = value;      
    }
    setRequiredRequestDescriptionValues(descriptionData);
  }
  
  //Update required fields of request details box with latest value
  const handleRequestDetailsValue = (value, name) => {
    const detailsData = {...requiredRequestDetailsValues};
    if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {      
      detailsData.requestType = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
      detailsData.receivedMode = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
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

  const createSaveRequestObject = (name, value, value2) => 
  {
    const requestObject = {...saveRequestObject};   
    if(Object.entries(requestObject).length !== 0) {      
      if (name === FOI_COMPONENT_CONSTANTS.ASSIGNED_TO) {       
        requestObject.assignedTo = value;
      }      
      else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME) {       
          requestObject.firstName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME) {        
          requestObject.middleName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME) {
          requestObject.lastName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ORGANIZATION) {
          requestObject.businessName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL) {
          requestObject.email = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.FOI_CATEGORY) {
          requestObject.category = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME) {
        requestObject.additionalPersonalInfo.childFirstName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_MIDDLE_NAME) {
        requestObject.additionalPersonalInfo.childMiddleName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_LAST_NAME) {
        requestObject.additionalPersonalInfo.childLastName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_NICKNAME) {
        requestObject.additionalPersonalInfo.childAlsoKnownAs = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CHILD_DOB) {
        requestObject.additionalPersonalInfo.childBirthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_FIRST_NAME) {
        requestObject.additionalPersonalInfo.anotherFirstName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_MIDDLE_NAME) {
        requestObject.additionalPersonalInfo.anotherMiddleName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_LAST_NAME) {
        requestObject.additionalPersonalInfo.anotherLastName = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_NICKNAME) {
        requestObject.additionalPersonalInfo.anotherAlsoKnownAs = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.ANOTHER_DOB) {
        requestObject.additionalPersonalInfo.anotherBirthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.HOME_PHONE) {
        requestObject.phonePrimary = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.MOBILE_PHONE) {
        requestObject.phoneSecondary = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY) {
        requestObject.workPhonePrimary = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY) {
        requestObject.workPhoneSecondary = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) {
        requestObject.address = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY) {
        requestObject.addressSecondary = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.CITY) {
        requestObject.city = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.POSTALCODE) {
        requestObject.postal = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.PROVINCE) {
        requestObject.province = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.COUNTRY) {
        requestObject.country = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE) {
        requestObject.receivedDate = value;
        const receivedDateUTC = new Date(value).toISOString();
        requestObject.receivedDateUF = receivedDateUTC;
        requestObject.dueDate = value2;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
        requestObject.requestProcessStart = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE) {
        requestObject.requestType = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_MODE) {
        requestObject.receivedMode = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.DELIVERY_MODE) {
        requestObject.deliveryMode = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.DOB) {
        requestObject.additionalPersonalInfo.birthDate = value;
      }      
      else if (name === FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER) {
        requestObject.correctionalServiceNumber = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER) {
        requestObject.publicServiceEmployeeNumber = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER) {
        requestObject.personalHealthNumber = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED) {
        requestObject.identityVerified = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.DESCRIPTION) {
        requestObject.description = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.START_DATE) {
        requestObject.fromDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.END_DATE) {
        requestObject.toDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.PROGRAM_AREA_LIST) {
        requestObject.selectedMinistries = [];
        const filteredData = value.filter(programArea => programArea.isChecked)
        .map(filteredProgramArea => {
          return {
            "code": filteredProgramArea.bcgovcode,
            "name": filteredProgramArea.name,
            "isSelected": filteredProgramArea.isChecked
          }
        });
        requestObject.selectedMinistries = filteredData;
      }
        
    }
    else {
      console.log(`inside else`);
    }    
    setSaveRequestObject(requestObject);    
  }

  console.log(`saveRequestObject = ${JSON.stringify(saveRequestObject)}`);
  
     return (
      <div className="container foi-review-request-container">      
        <div className="foi-review-container">
        <form className={`${classes.root} foi-request-form`} autoComplete="off">        
        {Object.entries(requestDetails).length !== 0 ? (
          <>
          <ReviewRequestHeader requestDetails={requestDetails} handleAssignedToInitialValue={handleAssignedToInitialValue} handleAssignedToValue={handleAssignedToValue} createSaveRequestObject={createSaveRequestObject}/>
          <ApplicantDetails requestDetails={requestDetails} handleCategoryInitialValue={handleCategoryInitialValue} handleEmailValidation={handleEmailValidation} handleCategoryValue={handleCategoryValue} createSaveRequestObject={createSaveRequestObject} /> 
          {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?          
          <ChildDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject}/> : null }          
           {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
          <OnBehalfOfDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject} /> : null }          
          <AddressContactDetails requestDetails={requestDetails} createSaveRequestObject={createSaveRequestObject} />
          <RequestDescriptionBox programAreaList={programAreaList} requestDetails = {requestDetails} handleUpdatedProgramAreaList={handleUpdatedProgramAreaList} handleOnChangeRequiredRequestDescriptionValues={handleOnChangeRequiredRequestDescriptionValues} handleInitialRequiredRequestDescriptionValues={handleInitialRequiredRequestDescriptionValues} createSaveRequestObject={createSaveRequestObject} />
          <RequestDetails  requestDetails={requestDetails} handleRequestDetailsValue={handleRequestDetailsValue} handleRequestDetailsInitialValue={handleRequestDetailsInitialValue} createSaveRequestObject={createSaveRequestObject} />
          {requestDetails.additionalPersonalInfo !== undefined ?
          <AdditionalApplicantDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject} />: null }
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