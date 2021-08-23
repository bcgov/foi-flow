import React, { useEffect, useState }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import './foirequest.scss';
import FOIRequestHeader from './FOIRequestHeader';
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
import {
  fetchFOIRawRequestDetails,
  fetchFOIRequestDetails, 
  fetchFOICategoryList, 
  fetchFOIProgramAreaList, 
  fetchFOIAssignedToList, 
  fetchFOIDeliveryModeList, 
  fetchFOIReceivedModeList 
} from "../../../apiManager/services/FOI/foiRequestServices";
import { makeStyles } from '@material-ui/core/styles';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { formatDate } from "../../../helper/FOI/helper";
import {push} from "connected-react-router";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),  
    },
  },
  validationErrorMessage: {
    marginTop:'30px',
    color: "#fd0404",
  },
  validationMessage: {
    marginTop:'30px',
    color: "#000000",
  },
}));

const FOIRequest = React.memo((props) => {
  const {requestId, ministryId} = useParams();
  
  const url = window.location.href;
  //gets the request detail from the store
  let requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);  
  const [saveRequestObject, setSaveRequestObject] = React.useState(requestDetails);
  const dispatch = useDispatch();
  useEffect(() => {
    if (ministryId) {
      
      dispatch(fetchFOIRequestDetails(requestId, ministryId));
    }
    else if (url.indexOf(FOI_COMPONENT_CONSTANTS.CREATE_REQUEST) === -1) {
      dispatch(fetchFOIRawRequestDetails(requestId));
    }
    else if (url.indexOf(FOI_COMPONENT_CONSTANTS.CREATE_REQUEST) > -1) {
      dispatch(fetchFOIAssignedToList("general", "unopened"));
    }
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
    // dispatch(fetchFOIAssignedToList());
    dispatch(fetchFOIReceivedModeList());
    dispatch(fetchFOIDeliveryModeList());
  },[requestId, dispatch]);

  
  useEffect(() => {    
    requestDetails = url.indexOf(FOI_COMPONENT_CONSTANTS.CREATE_REQUEST) > -1 ? {} : requestDetails;
    setSaveRequestObject(requestDetails);
  },[requestDetails]);
  
  const requiredRequestDescriptionDefaultData = {
    startDate: "",
    endDate: "",
    description: "",
    isProgramAreaSelected: false
  }  

  const requiredRequestDetailsInitialValues = {
    requestType:"",
    receivedMode: "",
    deliveryMode: "",
    receivedDate: "",
    requestStartDate: "",
    dueDate: "",
  }

  const requiredApplicantDetailsValues = {
    firstName: "",
    lastName: "",
    email: "",
    category: "",
  }

  const requiredContactDetailsValue = {
   primaryAddress: "",  
   city: "",
   province: "",
   country: "",
   postalCode: "",
  }
  
  //below states are used to find if required fields are set or not
  const [requiredRequestDescriptionValues, setRequiredRequestDescriptionValues] = React.useState(requiredRequestDescriptionDefaultData);
  const [requiredRequestDetailsValues, setRequiredRequestDetailsValues] = React.useState(requiredRequestDetailsInitialValues);  
  const [assignedToValue, setAssignedToValue] = React.useState("Unassigned");
  const [requiredApplicantDetails, setRequiredApplicantDetails] = React.useState(requiredApplicantDetailsValues);
  const [requiredContactDetails, setrequiredContactDetails] = React.useState(requiredContactDetailsValue);
  const [unSavedRequest, setUnSavedRequest] = React.useState(false);

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
  const handleApplicantDetailsInitialValue = React.useCallback((value) => {    
    setRequiredApplicantDetails(value);
  },[])
  const handleContactDetailsInitialValue = React.useCallback((value) => {    
    setrequiredContactDetails(value);
  },[])

  const handleApplicantDetailsValue = (value, name) => {
    const detailsData = {...requiredApplicantDetails};
    if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME) {
      detailsData.firstName = value;
    }    
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME) {
        detailsData.lastName = value;
    }    
    else if (name === FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL) {
        detailsData.email = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.FOI_CATEGORY) {
      detailsData.category = value
    }
    setRequiredApplicantDetails(detailsData);
  }

  const handleContanctDetailsValue = (value, name) => {
    const detailsData = {...requiredContactDetails};
    if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) {
      detailsData.primaryAddress = value;
    } 
    else if (name === FOI_COMPONENT_CONSTANTS.CITY) {
        detailsData.city = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.PROVINCE) {
      detailsData.province = value
    }
    else if (name === FOI_COMPONENT_CONSTANTS.COUNTRY) {
      detailsData.country = value
    }
    else if (name === FOI_COMPONENT_CONSTANTS.POSTALCODE) {
      detailsData.postalCode = value
    }
    setrequiredContactDetails(detailsData);
  }

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
  const handleRequestDetailsValue = (value, name, value2) => {    
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
    else if (name === FOI_COMPONENT_CONSTANTS.RECEIVED_DATE) {
      detailsData.receivedDate = value;      
    }
    else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
      detailsData.requestStartDate = value;
      detailsData.dueDate = value2;   
    }
    setRequiredRequestDetailsValues(detailsData);
  }

  //gets the latest assigned to value
  const handleAssignedToValue = (value) => {
    setAssignedToValue(value);
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

  const contactDetailsNotGiven = ((requiredContactDetails.primaryAddress === "" || requiredContactDetails.city === "" || requiredContactDetails.province === "" || requiredContactDetails.country === "" || requiredContactDetails.postalCode === "" ) && requiredApplicantDetails.email === "");

  //Variable to find if all required fields are filled or not
  const isValidationError = (
    requiredApplicantDetails.firstName === "" || requiredApplicantDetails.lastName === "" 
    || requiredApplicantDetails.category.toLowerCase().includes("select")
    || contactDetailsNotGiven
    || requiredRequestDescriptionValues.description === ""
    || !requiredRequestDescriptionValues.isProgramAreaSelected   
    || (validation.helperTextValue !== undefined && validation.helperTextValue !== "")
    || assignedToValue.toLowerCase().includes("unassigned")
    || requiredRequestDetailsValues.requestType.toLowerCase().includes("select")
    || requiredRequestDetailsValues.receivedMode.toLowerCase().includes("select")
    || requiredRequestDetailsValues.deliveryMode.toLowerCase().includes("select")
    || (requiredRequestDetailsValues.receivedDate === undefined || requiredRequestDetailsValues.receivedDate === "")
    || (requiredRequestDetailsValues.requestStartDate === undefined || requiredRequestDetailsValues.requestStartDate === "")
    );

  const classes = useStyles();
 

  const updateAdditionalInfo = (name, value, requestObject) => {
    if (requestObject.additionalPersonalInfo === undefined) {
      requestObject.additionalPersonalInfo = {
           alsoKnownAs:"",            
           birthDate:"",
           childFirstName:"",
           childMiddleName:"",
           childLastName:"",
           childAlsoKnownAs:"",
           childBirthDate:"",
           anotherFirstName:"",
           anotherMiddleName:"",
           anotherLastName:"",
           anotherAlsoKnownAs:"",
           anotherBirthDate:"",
           adoptiveMotherFirstName:"",
           adoptiveMotherLastName:"",
           adoptiveFatherLastName:"",
           adoptiveFatherFirstName:"",
           personalHealthNumber:"",
           identityVerified:"",
        };
    }
    else {
      if (name === FOI_COMPONENT_CONSTANTS.CHILD_FIRST_NAME) {
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
      else if (name === FOI_COMPONENT_CONSTANTS.DOB) {
        requestObject.additionalPersonalInfo.birthDate = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.PERSONAL_HEALTH_NUMBER) {
        requestObject.additionalPersonalInfo.personalHealthNumber = value;
      }
      else if (name === FOI_COMPONENT_CONSTANTS.IDENTITY_VERIFIED) {
        requestObject.additionalPersonalInfo.identityVerified = value;
      }
    }
  }

  const createRequestDetailsObject = (requestObject, name, value, value2) => {
    requestObject.id = requestId;
    requestObject.requestProcessStart = requiredRequestDetailsValues.requestStartDate;
    requestObject.dueDate = requiredRequestDetailsValues.dueDate;

    if (name === FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES) {     
      requestObject.receivedDate = value.receivedDate;     
      requestObject.receivedDateUF = value.receivedDate? new Date(value.receivedDate).toISOString(): "";
      requestObject.requestProcessStart = value.requestStartDate;
      requestObject.dueDate = value.dueDate;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.ASSIGNED_TO) {
      const assignedToValue = value.split("|");
      if (assignedToValue.length > 1) {
        requestObject.assignedGroup = assignedToValue[0];
        requestObject.assignedTo = assignedToValue[1];
      }
      else {
        requestObject.assignedGroup = "Unassigned";
        requestObject.assignedTo = assignedToValue[0];
      }      
      requestObject.assignedToName = value2;      
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
      requestObject.receivedDate = formatDate(value, 'yyyy MMM, dd');
      const receivedDateUTC = new Date(value).toISOString();
      requestObject.receivedDateUF = receivedDateUTC;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.REQUEST_START_DATE) {
      requestObject.requestProcessStart = value;
      requestObject.dueDate = value2;
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
          code: filteredProgramArea.bcgovcode,
          name: filteredProgramArea.name,
          isSelected: filteredProgramArea.isChecked
        }
      });
      requestObject.selectedMinistries = filteredData;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.CORRECTIONS_NUMBER) {
      requestObject.correctionalServiceNumber = value;
    }
    else if (name === FOI_COMPONENT_CONSTANTS.EMPLOYEE_NUMBER) {
      requestObject.publicServiceEmployeeNumber = value;
    }
  }

  const createSaveRequestObject = (name, value, value2) => 
  {
    const requestObject = {...saveRequestObject};      
    if (name === FOI_COMPONENT_CONSTANTS.RQUESTDETAILS_INITIALVALUES) {
      setUnSavedRequest(false);      
    }
    else {
      setUnSavedRequest(true);
    }
    updateAdditionalInfo(name, value, requestObject);
    createRequestDetailsObject(requestObject, name, value, value2); 
    setSaveRequestObject(requestObject);    
  }

  const [headerValue, setHeader] = useState("");
  const handleSaveRequest = (value, value2) => {
    setHeader(value);
    setUnSavedRequest(value2);
  }  
  const handleOpenRequest = (parendId, ministryId, unSaved) => {      
      setSaveRequestObject(unSaved);
      if (!unSaved) {
        dispatch(push(`/foi/foirequests/${parendId}/ministryrequest/${ministryId}`));
      }
  }

  const urlIndexCreateRequest = url.indexOf(FOI_COMPONENT_CONSTANTS.CREATE_REQUEST);
  return (
      <div className="container foi-review-request-container">
        <div className="foi-review-container">
        <form className={`${classes.root} foi-request-form`} autoComplete="off">        
        { (urlIndexCreateRequest === -1 && Object.entries(requestDetails).length !== 0) || urlIndexCreateRequest > -1 ? (
          <>
            <FOIRequestHeader headerValue={headerValue} requestDetails={requestDetails} handleAssignedToInitialValue={handleAssignedToInitialValue} handleAssignedToValue={handleAssignedToValue} createSaveRequestObject={createSaveRequestObject}/>
            <div className={`${contactDetailsNotGiven  ? classes.validationErrorMessage : classes.validationMessage}`}>* Please enter AT LEAST ONE form of contact information for the applicant, either EMAIL or MAILING ADDRESS.</div>
            <ApplicantDetails requestDetails={requestDetails} handleApplicantDetailsInitialValue={handleApplicantDetailsInitialValue} handleEmailValidation={handleEmailValidation} handleApplicantDetailsValue={handleApplicantDetailsValue} createSaveRequestObject={createSaveRequestObject} /> 
            {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?          
            <ChildDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject}/> : null }          
            {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
            <OnBehalfOfDetails additionalInfo={requestDetails.additionalPersonalInfo} createSaveRequestObject={createSaveRequestObject} /> : null }          
            <AddressContactDetails requestDetails={requestDetails} createSaveRequestObject={createSaveRequestObject} handleContactDetailsInitialValue={handleContactDetailsInitialValue} handleContanctDetailsValue={handleContanctDetailsValue} />
            <RequestDescriptionBox programAreaList={programAreaList} urlIndexCreateRequest={urlIndexCreateRequest} requestDetails = {requestDetails} handleUpdatedProgramAreaList={handleUpdatedProgramAreaList} handleOnChangeRequiredRequestDescriptionValues={handleOnChangeRequiredRequestDescriptionValues} handleInitialRequiredRequestDescriptionValues={handleInitialRequiredRequestDescriptionValues} createSaveRequestObject={createSaveRequestObject} />
            <RequestDetails  requestDetails={requestDetails} handleRequestDetailsValue={handleRequestDetailsValue} handleRequestDetailsInitialValue={handleRequestDetailsInitialValue} createSaveRequestObject={createSaveRequestObject} />
            {requiredRequestDetailsValues.requestType.toLowerCase() === FOI_COMPONENT_CONSTANTS.REQUEST_TYPE_PERSONAL ?
            <AdditionalApplicantDetails requestDetails={requestDetails} createSaveRequestObject={createSaveRequestObject} />: null }
            <RequestNotes />
            
            <BottomButtonGroup isValidationError = {isValidationError} urlIndexCreateRequest={urlIndexCreateRequest} saveRequestObject={saveRequestObject} unSavedRequest={unSavedRequest} handleSaveRequest={handleSaveRequest} handleOpenRequest={handleOpenRequest}/>
          </>
          ): null}
           </form>
        </div>
      </div>
    
    );
  });

export default FOIRequest;