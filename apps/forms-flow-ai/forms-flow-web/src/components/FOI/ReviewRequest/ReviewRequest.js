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



const ReviewRequest = React.memo((props) => {
  const selectedCategory = useSelector(state=> state.foiRequests.foiSelectedCategory);
  const requestDetails = useSelector(state=> state.foiRequests.foiRequestDetail);
  
  const dispatch = useDispatch();
  useEffect(()=>{    
    dispatch(fetchFOICategoryList());
    dispatch(fetchFOIProgramAreaList());
  },[dispatch]);

     return (
      <div className="container foi-review-request-container">           
        <div className="col-sm-12 col-md-12 foi-review-container">
          <ReviewRequestHeader />
          <ApplicantDetails requestDetails={requestDetails} />
          <ChildDetails />
          <OnBehalfOfDetails />
          <AddressContactDetails />
          <RequestDescriptionBox selectedCategory = {selectedCategory} />
          <RequestDetails />
          <AdditionalApplicantDetails />
          <RequestNotes />
          <BottomButtonGroup selectedCategory = {selectedCategory}/>
        </div>
      </div>
    
    );
  });

export default ReviewRequest;