import { Divider, Card, CardContent } from '@material-ui/core';
import './oipcdetails.scss';

const OIPCDetailsMinistry = (props) => {
    const {oipcData} = props;

    return (
        <Card id="applicantDetailsMinistry" className="foi-details-card">
            <label className="foi-details-label">OIPC Details</label>
            <CardContent >
            {oipcData.map((oipc, index) => {
                return (
                    <>
                    <div className="row foi-details-row " key={oipc.id}>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Order No</b>
                             </div>
                            <div>
                                <span>{oipc.oipcno}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Received Date</b>
                             </div>
                            <div>
                                <span>{oipc.receiveddate}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Review Type</b>
                             </div>
                            <div>
                                <span>{oipc.reviewetype}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Reason</b>
                             </div>
                            <div>
                                <span>{oipc.reason}</span>
                            </div>
                        </div>
  
                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Status</b>
                             </div>
                            <div>
                                <span>{oipc.status}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Investigator/Adjudicator</b>
                             </div>
                            <div>
                                <span>{oipc.investigator ? oipc.investigator : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Outcome</b>
                             </div>
                            <div>
                                <span>{oipc.outcome ? oipc.outcome : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Closed Date</b>
                             </div>
                            <div>
                                <span>{oipc.closedate ? oipc.closedate : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>In Inquiry?</b>
                             </div>
                            <div>
                                <span>{oipc.isinquiry ? "Yes" : "No"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Inquiry Order Comply Date</b>
                            </div>
                            <div>
                                <span>{oipc.inquiryattributes?.inquirydate ? oipc.inquiryattributes.inquirydate : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Inquiry Order No</b>
                            </div>
                            <div>
                                <span>{oipc.inquiryattributes?.orderno ? oipc.inquiryattributes.orderno : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>Inquiry Outcome</b>
                            </div>
                            <div>
                                <span>{oipc.inquiryattributes?.inquiryoutcome ? oipc.inquiryattributes.inquiryoutcome : "N/A"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>In Judical Review?</b>
                             </div>
                            <div>
                                <span>{oipc.isjudicialreview ? "Yes" : "No"}</span>
                            </div>
                        </div>

                        <div className="col-lg-3 foi-details-col"  style={{paddingBottom: "15px"}}>
                            <div>
                                <b>In Subsequent Appeal?</b>
                             </div>
                            <div>
                                <span>{oipc.issubsequentappeal ? "Yes" : "No"}</span>
                            </div>
                        </div>
                    </div>
                    {index !== (oipcData?.length - 1)  && <Divider style={{margin: "20px"}} />}
                    </>
                )
            })}
            </CardContent>
        </Card>
    );
}

export default OIPCDetailsMinistry;