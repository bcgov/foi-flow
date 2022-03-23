import React, {useEffect} from 'react';
import Alert from 'react-bootstrap/Alert';
import './axismessagebanner.scss';
import { formatDate } from "../../../../helper/FOI/helper";


const AxisMessageBanner = ({axisMessage, requestDetails}) => {


  const warningMessage = () => {
    if(axisMessage === "WARNING")
      return "Updates to this request have been made in AXIS. Please sync to AXIS before continuing."
    else if(axisMessage === "ERROR")
      return "System is unable to connect with AXIS, please update request in both systems"
  }

    return (
        <div style={{marginLeft: '-10%'}}>
           <Alert style={{backgroundColor: axisMessage === "ERROR"? "#F97957 !important" : " #FFC709; !important"}}>
            <Alert.Heading>
             <div className='axis-banner-div'>
               <span className='axis-message'>WARNING!</span>
               <span>{warningMessage()}</span>
               <span className='axis-sync-date'>Last Updated {formatDate(requestDetails.axisSyncDate, "MMM dd yyyy | hh:mm aa")}</span>
             </div>
             
            </Alert.Heading>
          </Alert>
        </div>
      );
}

export default AxisMessageBanner;
