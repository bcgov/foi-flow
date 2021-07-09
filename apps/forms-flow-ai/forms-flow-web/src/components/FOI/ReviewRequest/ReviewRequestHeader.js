import React, {useEffect} from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import "./reviewrequestheader.scss";

import { SelectWithLegend } from '../customComponents';

const ReviewRequestHeader = React.memo((props) => {
  
    useEffect(() => {       
        //console.log(`formdata = ${props.location.state.reviewRequestData}`)
    }, [])

    const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);

    const preventDefault = (event) => event.preventDefault();

     return (
        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h3 className="foi-review-request-text">Review Request</h3>
                    </Link>
                    <h3 className="foi-period-text">  |  </h3>
                    <Link href="#" onClick={preventDefault}>
                    <h3 className="foi-correspondence-text"> Correspondence</h3>
                    </Link>
                </div>            
            <div className="foi-request-status">
                UnOpened
            </div>
            </div>
            
            <div className="foi-assigned-to-container">
                <div className="foi-assigned-to-inner-container">
                <SelectWithLegend selectData = {assignedToList} legend="Assigned To" selectDefault="Select User" required={true} />                
                </div>
            </div>
        </div>
    );
  });

export default ReviewRequestHeader;