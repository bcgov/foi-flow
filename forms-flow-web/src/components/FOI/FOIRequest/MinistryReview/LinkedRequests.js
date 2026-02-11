import React, { useState, useEffect } from 'react';
import Card from '@material-ui/core/Card';
import { useSelector } from "react-redux";
import { makeStyles } from '@material-ui/core/styles';
import './LinkedRequests.scss'

const useStyles = makeStyles((_theme) => ({
    headingError: {
        color: "#ff0000"
    },
    headingNormal: {
        color: "000000"
    },
    btndisabled: {
        color: "#808080"
    }
}));

const LinkedRequests = React.memo((requestDetails) => {
    const classes = useStyles();
    const _requestDetails = requestDetails.requestDetails;
    const [linkedRequestObjs, setLinkedRequestObjs] = useState(_requestDetails.linkedRequests);

    useEffect(() => {
      

    }, [linkedRequestObjs]);


    return (
      <Card id="linkedrequestMinistry" className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col">
            <label className="foi-details-label">LINKED REQUESTS</label>
          </div>
        </div>
        <div>
            <ul className="linked-request-list">
                {linkedRequestObjs?.map((reqObj, index) => {
                    return (
                    <li key={index} className="linked-request-item">
                      {reqObj.axisrequestid}
                    </li>
                  );
                })}
            </ul>
        </div>
      </Card>
    );

})


export default LinkedRequests;