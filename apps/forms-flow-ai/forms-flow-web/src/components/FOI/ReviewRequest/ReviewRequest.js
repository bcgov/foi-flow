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
import { fetchFOICategoryList, fetchFOIProgramAreaList } from "../../../apiManager/services/FOI/foiRequestServices";
import { useParams } from 'react-router-dom';
import { fetchFOIRequestDetails } from "../../../apiManager/services/FOI/foiRequestServices";


const ReviewRequest = React.memo((props) => {
  const {requestId} = useParams();
  const selectedCategory = useSelector(state=> state.foiRequests.foiSelectedCategory);
  const requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);  
  const dispatch = useDispatch();
  useEffect(()=>{    
    dispatch(fetchFOIRequestDetails(requestId));   
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
  },[requestId, dispatch]);
  
     return (
      <div className="container foi-review-request-container">           
        <div className="col-sm-12 col-md-12 foi-review-container">
        {requestDetails.description !== undefined ? (
          <>
          <ReviewRequestHeader />     
          <ApplicantDetails requestDetails={requestDetails} />
          {requestDetails.additionalpersonalInfo.childFirstName !== undefined ?
          <ChildDetails additionalInfo={requestDetails.additionalpersonalInfo}/> : null }
          
           {requestDetails.additionalpersonalInfo.anotherFirstName !== undefined ?
          <OnBehalfOfDetails additionalInfo={requestDetails.additionalpersonalInfo} /> : null }          
          <AddressContactDetails requestDetails={requestDetails} />
          <RequestDescriptionBox selectedCategory = {selectedCategory} requestDetails={requestDetails} />
          <RequestDetails  requestDetails={requestDetails}/>
          {requestDetails.additionalpersonalInfo.childFirstName !== undefined ?
          <AdditionalApplicantDetails additionalInfo={requestDetails.additionalpersonalInfo}/>: null }
          <RequestNotes />
          <BottomButtonGroup selectedCategory = {selectedCategory}/>
          </>
           ): null}
        </div>
      </div>
    
    );
  });

export default ReviewRequest;