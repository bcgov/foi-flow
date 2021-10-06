import React, { useEffect, useState }  from 'react';
import { useDispatch, useSelector } from "react-redux";
import '../foirequest.scss'
import { StateDropDown } from '../../customComponents';
import FOIRequestHeader from '../FOIRequestHeader';
import "../TabbedContainer.scss";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import { useParams } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';

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


const MinistryReview = React.memo((props) => {

  const {requestId, ministryId, requestState} = useParams();
  const [_requestStatus, setRequestStatus] = React.useState(StateEnum.unopened.name);
  const [_tabStatus, settabStatus] = React.useState(requestState);
   //gets the request detail from the store
 

  let requestDetails = {
    "assignedGroup": "Intake Team",
    "assignedTo": "dviswana@idir",
    "category": "Interest Group",
    "categoryid": 3,
    "cfrDueDate": "2021-10-21",
    "currentState": "Call For Records",
    "deliveryMode": "Secure File Transfer",
    "deliverymodeid": 1,
    "description": "TEST",
    "dueDate": "2021-11-18",
    "fromDate": "",
    "id": 1,
    "idNumber": "AEST-2021-16057",
    "programareaid": 1,
    "receivedDate": "2021 Oct, 05",
    "receivedDateUF": "2021-10-05 00:00:00.000000",
    "receivedMode": "Fax",
    "receivedmodeid": 2,
    "requestProcessStart": "2021-10-05",
    "requestType": "general",
    "requeststatusid": 2,
    "selectedMinistries": [
      {
        "code": "AEST",
        "name": "Ministry of Advanced Education and Skills Training",
        "selected": "true"
      }
    ],
    "toDate": ""
  }
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