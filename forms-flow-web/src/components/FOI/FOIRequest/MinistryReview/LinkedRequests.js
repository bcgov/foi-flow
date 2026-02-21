import Card from '@material-ui/core/Card';
import { LinkedRequestsTable } from '../LinkedRequestsTable';

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