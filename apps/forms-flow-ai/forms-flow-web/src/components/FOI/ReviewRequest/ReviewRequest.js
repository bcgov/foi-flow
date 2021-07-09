import React from 'react';
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
import { useSelector } from "react-redux";


const ReviewRequest = React.memo((props) => {
  const selectedCategory = useSelector(state=> state.foiRequests.foiSelectedCategory);
     return (
      <div className="container foi-review-request-container">           
        <div className="col-sm-12 col-md-12 foi-review-container">
          <ReviewRequestHeader />
          <ApplicantDetails />
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