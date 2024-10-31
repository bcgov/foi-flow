import React, {useState} from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { formatDate } from "../../../../helper/FOI/helper";
import { StateEnum } from '../../../../constants/FOI/statusEnum';
import MinistriesCanvassed from '../../customComponents/MinistriesCanvassed/MinistriesCanvassed';


const RequestDetails = React.memo((requestDetails) => {

    const _requestDetails = requestDetails.requestDetails;    
    const [openModal, setModal] = useState(false);

    return Object.entries(_requestDetails).length > 0 &&
      _requestDetails != undefined && (
      <>
        <Card id="requestDetailsMinistry" className="foi-details-card">
          <div className="row foi-details-row">
            <div className="col-lg-8 foi-details-col ">
              <label className="foi-details-label">REQUEST DETAILS</label>
            </div>
            <div className="col-lg-4 foi-details-col ">
              <button type="button" className={`btn btn-link btn-description-history`} onClick={() => setModal(true)} disabled={!(!!_requestDetails.linkedRequests) || (!!_requestDetails.linkedRequests &&!_requestDetails.linkedRequests.length >0)}>
                Linked Requests
              </button>
              {/* <a href="#" className="foi-floatright foi-link" onClick={() => setModal(true)} disabled={!(!!_requestDetails.linkedRequests)}>
                Ministries Canvassed
              </a> */}
              <MinistriesCanvassed openModal={openModal} selectedMinistries={_requestDetails?.linkedRequests} setModal={setModal} isLinkedRequest={true}/>
            </div>
          </div>
          <CardContent>
            <div className="row foi-details-row foi-justifyleft">
              <div className="col-lg-10 foi-details-col ">
                <b>
                  Selected Ministry:{" "}
                  {_requestDetails.selectedMinistries &&
                    _requestDetails.selectedMinistries[0].name}
                </b>
              </div>
            </div>
            <div className="row foi-details-row foi-justifyleft"></div>
            <div className="row foi-details-row foi-rowtoppadding foi-justify-spacyaround">
              <div className="col-lg-4 foi-details-col foi-inline-grid">
                <span>
                  <b>Request Opened</b>
                </span>
                <span className="foi-rowtoppadding">
                  {formatDate(
                    _requestDetails.requestProcessStart,
                    "MMM dd yyyy"
                  ).toUpperCase()}
                </span>
              </div>
              <div className="col-lg-4 foi-details-col foi-inline-grid">
                <span>
                  <b>Records Due Date</b>
                </span>
                <span className="foi-rowtoppadding">
                  {(_requestDetails?.currentState?.toLowerCase() !==
                    StateEnum.onhold.name.toLowerCase() && _requestDetails?.currentState?.toLowerCase() !==
                    StateEnum.onholdother.name.toLowerCase())
                    ? formatDate(
                        _requestDetails.cfrDueDate,
                        "MMM dd yyyy"
                      ).toUpperCase()
                    : "N/A"}
                </span>
              </div>
              <div className="col-lg-4 foi-details-col foi-inline-grid">
                <span>
                  <b>Legislated Due Date</b>
                </span>
                <span className="foi-rowtoppadding">
                  {(_requestDetails?.currentState?.toLowerCase() !==
                    StateEnum.onhold.name.toLowerCase() && _requestDetails?.currentState?.toLowerCase() !==
                    StateEnum.onholdother.name.toLowerCase())
                    ? formatDate(
                        _requestDetails.dueDate,
                        "MMM dd yyyy"
                      ).toUpperCase()
                    : "N/A"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>{" "}
      </>
    );


})


export default RequestDetails;