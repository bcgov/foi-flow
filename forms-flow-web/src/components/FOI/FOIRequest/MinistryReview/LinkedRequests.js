import React, { useState } from 'react';
import Card from '@material-ui/core/Card';
import { makeStyles } from '@material-ui/core/styles';
import './LinkedRequests.scss'
import { LinkedRequestsTable } from '../LinkedRequestsTable';

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

const LinkedRequests = ({isMinistry, linkedRequests, linkedRequestsInfo}) => {
    return (
      <Card id="linkedrequestMinistry" className="foi-details-card">
        <div className="row foi-details-row">
          <div style={{paddingBottom: "7px"}} className="col-lg-8 foi-details-col">
            <label className="foi-details-label">LINKED REQUESTS</label>
          </div>
        </div>
        <div>
          <LinkedRequestsTable
            isMinistry={isMinistry}
            linkedRequests={linkedRequests}
            linkedRequestsInfo={linkedRequestsInfo}
          />
        </div>
      </Card>
    );
}

export default LinkedRequests;