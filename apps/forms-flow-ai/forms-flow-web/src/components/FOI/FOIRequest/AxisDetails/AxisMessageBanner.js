import React from 'react';
import Alert from 'react-bootstrap/Alert';
import './axismessagebanner.scss';
import { formatDateInPst } from "../../../../helper/FOI/helper";


const AxisMessageBanner = ({axisMessage, requestDetails}) => {


  const warningMessage = () => {
    if(axisMessage === "WARNING")
      return "Updates to this request have been made in AXIS. Please sync to AXIS before continuing."
    else if(axisMessage === "ERROR")
      return "System is unable to connect with AXIS, please update request in both systems"
  }

    return (
      axisMessage &&
        <div className='axis-banner'>
           <Alert className={axisMessage === "WARNING" ? 'update-warning' : 'no-connection'}>
            <Alert.Heading>
             <div className='axis-banner-div'>
               <span className='axis-message'>WARNING!</span>
               <span>{warningMessage()}</span>
               {requestDetails?.axisSyncDate &&
                <span className='axis-sync-date'>Last Updated {formatDateInPst(requestDetails.axisSyncDate, "MMM dd yyyy | hh:mm aa")}</span>    
                }
             </div>
             
            </Alert.Heading>
          </Alert>
        </div>
      );
}

export default AxisMessageBanner;
