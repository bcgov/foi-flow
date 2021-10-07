import React, { useEffect, useState }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import './MinistryReview.scss'
import { StateDropDown } from '../../customComponents';
import '../foirequestheader.scss'
import "./MinistryReviewTabbedContainer.scss";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import {
  fetchFOIMinistryViewRequestDetails,
  fetchFOIRequestDescriptionList
} from "../../../../apiManager/services/FOI/foiRequestServices";
import ApplicantDetails from './ApplicantDetails';
import RequestDetails from './RequestDetails';
import RequestDescription from './RequestDescription';
import RequestHeader from './RequestHeader';

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
  btndisabled: {
    border: 'none',
    backgroundColor: '#eceaea',
    color: '#FFFFFF'
  },
  btnenabled: {
    border: 'none',
    backgroundColor: '#38598A',
    color: '#FFFFFF',
    backgroundColor: '#38598A'
  },
  btnsecondaryenabled: {
    border: '1px solid #38598A',
    backgroundColor: '#FFFFFF',
    color: '#38598A'
  }
 
}));


const MinistryReview = React.memo((props) => {

  const {requestId, ministryId, requestState} = useParams();
  const [_requestStatus, setRequestStatus] = React.useState(StateEnum.unopened.name);
  const [_tabStatus, settabStatus] = React.useState(requestState);
   //gets the request detail from the store
 
   const dispatch = useDispatch();
   useEffect(() => {
     if (ministryId) {
       dispatch(fetchFOIMinistryViewRequestDetails(requestId, ministryId));
       dispatch(fetchFOIRequestDescriptionList(requestId, ministryId));
     }     
   },[requestId, dispatch]); 

  
  let requestDetails = useSelector(state=> state.foiRequests.foiMinistryViewRequestDetail);

  console.log("Ministry view Request details")
  console.log(requestDetails)

  
  var foitabheaderBG;
  const classes = useStyles();
 

  switch (_tabStatus){
    case StateEnum.open.name:
      foitabheaderBG = "foitabheadercollection foitabheaderOpenBG"
      break;
    case StateEnum.closed.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderClosedBG"
      break;
    case StateEnum.callforrecords.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderCFRG"
      break;
    case StateEnum.callforrecordsoverdue.name:
      foitabheaderBG = "foitabheadercollection foitabheaderCFROverdueBG"
      break;
    case StateEnum.redirect.name: 
      foitabheaderBG = "foitabheadercollection foitabheaderRedirectBG"
      break;
    default:
      foitabheaderBG = "foitabheadercollection foitabheaderdefaultBG";
      break;      
  }
  const handleStateChange =(currentStatus)=>{

  }

  const returnToQueue = (e) => {
    e.preventDefault();
    window.location.href = '/foi/dashboard';
}

  const tabclick =(evt,param)=>{
   
    var i, tabcontent, tablinks;
    
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
   
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(param).style.display = "block";
    evt.currentTarget.className += " active";

  }

  const bottomTextArray = _requestStatus.split('|');

  return (

    <div className="foiformcontent">
      <div className="foitabbedContainer">

        <div className={foitabheaderBG}>
          <div className="foileftpanelheader">
            <h1><a href="/foi/dashboard">FOI</a></h1>
          </div>
          <div className="foileftpaneldropdown">
            <StateDropDown requestStatus={_requestStatus} handleStateChange={handleStateChange} requestDetail={requestDetails}/>
          </div>
          
        <div className="tab">
          <div className="tablinks active" name="Request" onClick={e => tabclick(e,'Request')}><span className="circle"></span> Request</div>
          <div className="tablinks" name="CorrespondenceLog" onClick={e=>tabclick(e,'CorrespondenceLog')}><span className="circle"></span> Correspondence Log</div>
          <div className="tablinks" name="Option3" onClick={e=>tabclick(e,'Option3')}><span className="circle"></span> Option 3</div>
        </div>
        {_requestStatus.toLowerCase().includes("days") &&  bottomTextArray.length > 1  ?
        <div className="foileftpanelstatus"> 
          <h4>{bottomTextArray[0]}</h4>
          <h4>{bottomTextArray[1]}</h4>
        </div>
        : 
        <h4 className="foileftpanelstatus">{_requestStatus.toLowerCase().includes("days") ? _requestStatus : ""}</h4>
        }

        </div>
        <div className="foitabpanelcollection"> 
          <div id="Request" className="tabcontent active">                                
            <div className="container foi-review-request-container">

              <div className="foi-review-container">
                <form className={`${classes.root} foi-request-form`} autoComplete="off">
                  <>
                    <RequestHeader requestDetails={requestDetails} />
                    <ApplicantDetails />
                    <RequestDescription />
                    <RequestDetails />
                    <div className="foi-bottom-button-group">
                      <button type="button" className="btn btn-bottom btnenabled">Save</button>
                      
                    </div>
                  </>

                </form>
              </div>
            </div>                            
          </div> 
          <div id="CorrespondenceLog" className="tabcontent">
              
              </div> 
          <div id="Option3" className="tabcontent">
           <h3>Option 3</h3>
          </div>        
        </div>
      </div>
    </div>

  );

  })

  export default MinistryReview