import 'reactjs-popup/dist/index.css';
import ApplicantDetails from '../../../FOIRequest/MinistryReview/ApplicantDetails';
import ChildDetails from '../../../FOIRequest/MinistryReview/ChildDetails';
import OnBehalfDetails from '../../../FOIRequest/MinistryReview/OnBehalfDetails';
import RequestDescription from '../../../FOIRequest/MinistryReview/RequestDescription';
import RequestDetails from '../../../FOIRequest/MinistryReview/RequestDetails';
import AdditionalApplicantDetails from '../../../FOIRequest/MinistryReview/AdditionalApplicantDetails';
import ExtensionDetails from '../../../FOIRequest/MinistryReview/ExtensionDetails';
import OIPCDetails from '../../../FOIRequest/OIPCDetails/Index';
import { getHeaderText } from '../../../FOIRequest/MinistryReview/utils';
import RequestFlag from '../../RequestFlag';
import RequestMinistryRestriction from '../../RequestMinistryRestriction';
import { StateEnum } from '../../../../../constants/FOI/statusEnum';
import _ from "lodash";
import { Card, CardContent, Grid } from '@material-ui/core';
import './exportrequestdetails.scss';
import { Col, Row } from 'react-bootstrap';



const ExportRequestDetailsHistory = ({
    iaoassignedToList,
    requestDetails,
    requestState,
}) => {

    const showDivisionalTracking =
        requestDetails &&
        requestDetails.divisions?.length > 0 &&
        requestState &&
        requestState.toLowerCase() !== StateEnum.open.name.toLowerCase() &&
        requestState.toLowerCase() !==
        StateEnum.intakeinprogress.name.toLowerCase();
    const getGroupName = () => {
        if (requestDetails.assignedGroup)
            return requestDetails.assignedGroup;
        return "Unassigned";
    }

    const getAssignedTo = (groupName) => {
        if (requestDetails.assignedTo)
            return requestDetails.assignedTo;
        return groupName;
    }
    function getFullName() {
        const groupName = getGroupName();
        const assignedTo = getAssignedTo(groupName);
        if (iaoassignedToList?.length > 0) {
            const assigneeGroup = iaoassignedToList.find(_assigneeGroup => _assigneeGroup.name === groupName);
            const assignee = assigneeGroup?.members?.find(_assignee => _assignee.username === assignedTo);
            if (groupName === assignedTo)
                return groupName;
            return assignee !== undefined ? `${assignee.lastname}, ${assignee.firstname}` : "invalid user";
        }
        return groupName;
    }
    let assigneeDetails = _.pick(requestDetails, ['assignedGroup', 'assignedTo', 'assignedToFirstName', 'assignedToLastName',
        'assignedministrygroup', 'assignedministryperson', 'assignedministrypersonFirstName', 'assignedministrypersonLastName']);

    const minsitryAssignedToGroup = assigneeDetails.assignedministrygroup ? assigneeDetails.assignedministrygroup : "";
    const ministryAssignedTo = assigneeDetails.assignedministryperson ? `${minsitryAssignedToGroup}|${assigneeDetails.assignedministryperson}|${assigneeDetails.assignedministrypersonFirstName}|${assigneeDetails.assignedministrypersonLastName}` : `|Unassigned`;

    return (
        <div id='RequestDetails'>
            <div className="row" >
                <div className="col-lg-6">
                    <h1 className="foi-review-request-text foi-ministry-requestheadertext">{getHeaderText(requestDetails)}</h1>
                </div>
                <div className="col-lg-6">
                    <Grid container columns={16}>
                        <Grid>
                            <span className='request-details-assignee'>IAO Assigned To -</span>
                        </Grid>
                        <Grid>
                            <span>{" " + getFullName()}</span>
                        </Grid>
                    </Grid>
                </div>
            </div>
            <div className="row">
                <div className="col-lg-6">
                    <Grid container columns={16}>
                        <Grid>
                            <RequestMinistryRestriction
                                isministryrestricted={requestDetails?.ministryrestricteddetails?.isrestricted()}
                                requestDetails={requestDetails}
                            />
                        </Grid>
                        <Grid>
                            <div className="foi-request-review-header-col1-row">
                                <RequestFlag
                                    type="oipcreview"
                                    requestDetails={requestDetails}
                                    isActive={requestDetails.isoipcreview}
                                    isDisabled={true}
                                />
                            </div>
                        </Grid>
                    </Grid>
                </div>
                <div className="col-lg-6">
                    <Grid container columns={16}>
                        <Grid>
                            <span className='request-details-assignee'>Ministry Assigned To - </span>
                        </Grid>
                        <Grid>
                            <span>{" " + ministryAssignedTo}</span>
                        </Grid>
                    </Grid>
                </div>
            </div>
            <ApplicantDetails requestDetails={requestDetails} />
            <ChildDetails requestDetails={requestDetails} />
            <OnBehalfDetails requestDetails={requestDetails} />
            <RequestDescription requestDetails={requestDetails} />
            <RequestDetails requestDetails={requestDetails} />
            <AdditionalApplicantDetails
                requestDetails={requestDetails}
            />
            <ExtensionDetails
                style={{ pageBreakInside: 'avoid' }}
                requestDetails={requestDetails}
                requestState={requestState}
            />
            {showDivisionalTracking && (
                <Card className="foi-details-card"
                    style={{ pageBreakInside: 'avoid' }}>
                    <div className="row foi-details-row">
                        <div className="col-lg-8 foi-details-col ">
                            <label className="foi-details-label">DIVISIONAL TRACKING</label>
                        </div>
                    </div>
                    <CardContent>
                        {requestDetails.divisions?.map((division, index) =>
                            <Row key={index} className='divisions-row'>
                                <Col className='text-right'>{division.divisionname}</Col>
                                <Col style={{ marginTop: '-4px' }}>
                                    <div className='arrow'>
                                        <div className='line'></div>
                                        <div className='point'></div>
                                    </div>
                                </Col>
                                <Col className='text-left'>{division.stagename}</Col>
                            </Row>
                        )}
                    </CardContent>
                </Card>
            )}
            {requestDetails.isoipcreview && requestState && requestState.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase() && requestState.toLowerCase() !== StateEnum.unopened.name.toLowerCase() && (
                <OIPCDetails
                    style={{ pageBreakInside: 'avoid' }}
                    oipcData={requestDetails.oipcdetails}
                    isMinistry={true}
                />
            )}
        </div>
    );
};

export default ExportRequestDetailsHistory;