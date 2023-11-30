import { TextField, FormControlLabel, MenuItem, Grid, Checkbox } from '@material-ui/core';
import { useState, useEffect } from "react";
import { formatDate } from "../../../../helper/FOI/helper";
import { useSelector } from "react-redux";
import RemoveOIPCModal from './RemoveOIPCModal';
import OutcomeModal from './OutcomeModal';
import AmendModal from './AmendModal';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash } from '@fortawesome/free-solid-svg-icons';

const OIPCItem = (props) => {
    const {oipcObj, updateOIPC, removeOIPC} = props;
    
    //App State
    const oipcOutcomes = useSelector(state=> state.foiRequests.oipcOutcomes);
    const oipcStatuses = useSelector(state=> state.foiRequests.oipcStatuses);
    const oipcReviewtypes = useSelector(state=> state.foiRequests.oipcReviewtypes);
    const oipcInquiryoutcomes = useSelector(state=> state.foiRequests.oipcInquiryoutcomes);

    //Local State
    const [oipc, setOipc] = useState(oipcObj);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showOutcomeModal, setShowOutcomeModal] = useState(false);
    const [showAmendModal, setShowAmendModal] = useState(false);

    console.log("ITEM", oipc)
    
    //Functions
    const generateNamesFromOIPCId = (oipcObj) => {
        const reviewtype = oipcReviewtypes.find(reviewtype => reviewtype.reviewtypeid === oipcObj.reviewtypeid && reviewtype.reasonid === oipcObj.reasonid);
        const status = oipcStatuses.find(status => status.statusid === oipcObj.statusid);
        const outcome = oipcOutcomes.find(outcome => outcome.outcomeid === oipcObj.outcomeid);

        setOipc((prev) => {
            return {...prev, reviewtypeName: reviewtype ? reviewtype.type_name : ""}
        })
        setOipc((prev) => {
            return {...prev, statusName: status ? status.name : ""}
        })
        setOipc((prev) => {
            return {...prev, outcomeName: outcome ? outcome.name : ""}
        })
        setOipc((prev) => {
            return {...prev, reasonName: reviewtype ? reviewtype.reason_name : ""}
        })
    }
    const uniqueReviewTypes = (oipcReviewTypes) => {
        const uniqeValues = {};
        return oipcReviewTypes.filter(reviewtype => !uniqeValues[reviewtype.type_name] && (uniqeValues[reviewtype.type_name] = true));
    }
    const handleReviewType = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reviewtypeid = value;
        newOIPCObj.reasonid = null;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleOIPCNumber = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.oipcno = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleReceivedDate = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.receiveddate = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleClosedDate = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.closeddate = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleReason = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reasonid = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleStatus = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.statusid = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleInvestiagtor = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.investigator = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleOutcome = (value) => {
        if (value === 5) {
            return setShowAmendModal(true);
        }
        const newOIPCObj = oipc;
        newOIPCObj.outcomeid = value;
        setOipc(newOIPCObj);
        setShowOutcomeModal(true);
    }
    const handleInquiry = (value) => {
        const newOIPCObj = oipc;
        if (value === false) {
            newOIPCObj.inquiryattributes = null;
        } else {
            newOIPCObj.inquiryattributes = {
                inquirydate: null,
                orderno: "",
                inquiryoutcome: null,
            };
        }
        newOIPCObj.isinquiry = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleJudicalReview = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.isjudicialreview = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleSubsequentAppeal = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.issubsequentappeal = value;
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }
    const handleInquiryFields = (value, attribute) => {
        const newOIPCObj = oipc;
        if (attribute === "COMPLYDATE") {
            newOIPCObj.inquiryattributes.inquirydate = value;
        }
        if (attribute === "ORDERNO") {
            newOIPCObj.inquiryattributes.orderno = value;
        }
        if (attribute === "INQUIRYOUTCOME") {
            newOIPCObj.inquiryattributes.inquiryoutcome = value;
        }
        setOipc(newOIPCObj);
        updateOIPC(newOIPCObj);
    }

    useEffect(() => {
        setOipc(oipcObj);
        generateNamesFromOIPCId(oipc);
    }, [oipcObj])

    return (
        <> 
            <div key={oipc.id} style={{display: "flex", flexDirection: "row", justifyContent: "flex-end"}}>
                <button onClick={() => setShowDeleteModal(true)} style={{ border: "none", background: "none" }}>
                    <FontAwesomeIcon icon={faTrash} color="#38598A" />
                </button>
            </div>
            {showDeleteModal && <RemoveOIPCModal removeOIPC={removeOIPC} showModal={showDeleteModal} setShowModal={setShowDeleteModal} oipc={oipc} />}
            {showOutcomeModal && <OutcomeModal updateOIPC={updateOIPC} showModal={showOutcomeModal} setShowModal={setShowOutcomeModal} setOipc={setOipc} oipc={oipc} />}
            {showAmendModal && <AmendModal updateOIPC={updateOIPC} showModal={showAmendModal} setShowModal={setShowAmendModal} setOipc={setOipc} oipc={oipc} />}
            <Grid container spacing={1}>
            <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="OIPC No" 
                        variant="outlined" 
                        value={oipc.oipcno}
                        onChange = {(event) => handleOIPCNumber(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.oipcno === ""}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        placeholder="OIPC Number"
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="Received Date" 
                        variant="outlined" 
                        value={oipc.receiveddate ? formatDate(new Date(oipc.receiveddate)) : null}
                        onChange = {(event) => handleReceivedDate(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { max: formatDate(new Date())} }}
                        type="date"
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.receiveddate === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        value={oipc.reviewtypeid}
                        label="Review Type"
                        onChange={(event) => handleReviewType(event.target.value)}
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.reviewtypeid === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    >
                        {uniqueReviewTypes(oipcReviewtypes).map((reviewtype) => {
                            return <MenuItem key={reviewtype.reviewtypeid} value={reviewtype.reviewtypeid}>{reviewtype.type_name}</MenuItem>
                        })}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        value={oipc.reasonid}
                        label="Reason"
                        onChange = {(event) => handleReason(event.target.value)}
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.reasonid === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    >
                        {oipc.reviewtypeid ? 
                            oipcReviewtypes.map((reviewtype) => {
                            if (reviewtype.reviewtypeid === oipc.reviewtypeid) {
                                return <MenuItem key={reviewtype.reasonid} value={reviewtype.reasonid}>{reviewtype.reason_name}</MenuItem>
                            }
                        }) : null}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        value={oipc.statusid}
                        label="Status"
                        onChange = {(event) => handleStatus(event.target.value)}
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.statusid === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    >
                        {oipcStatuses.map((status) => {
                            return <MenuItem key={status.statusid} value={status.statusid}>{status.name}</MenuItem>
                        })}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        fullWidth 
                        label="Investigator/Adjudicator" 
                        variant="outlined" 
                        onChange = {(event) => handleInvestiagtor(event.target.value)}
                        value={oipc.investigator}
                        InputLabelProps={{ shrink: true }}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        placeholder="Firstname Lastname"
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        onChange = {(event) => handleOutcome(event.target.value)}
                        fullWidth
                        value={oipc.outcomeid}
                        label="Outcome"
                    >
                        {oipcOutcomes.map((outcome) => {
                            if (outcome.outcomeid !== 5) {
                                return <MenuItem disabled={oipc.outcomeid && oipc.outcomeid !== 5} key={outcome.outcomeid} value={outcome.outcomeid}>{outcome.name}</MenuItem>
                            } else {
                                return <MenuItem disabled={oipc.outcomeid === null} key={outcome.outcomeid} value={outcome.outcomeid}>{outcome.name}</MenuItem>
                            }
                        })}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="Closed Date" 
                        variant="outlined" 
                        value={oipc.closeddate ? formatDate(new Date(oipc.closeddate)) : null}
                        onChange = {(event) => handleClosedDate(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { max: formatDate(new Date())} }}
                        type="date"
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    />
                </Grid>
            </Grid>
            <div style={{display:"flex", flexDirection: "row", justifyContent: "space-between"}}>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Inquiry?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isinquiry} 
                        onChange = {() => handleInquiry(true)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isinquiry} 
                        onChange = {() => handleInquiry(false)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Judicial Review?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isjudicialreview} 
                        onChange = {() => handleJudicalReview(true)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isjudicialreview} 
                        onChange = {() => handleJudicalReview(false)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Subsequent Appeal?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.issubsequentappeal} 
                        onChange = {() => handleSubsequentAppeal(true)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="Yes"
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.issubsequentappeal} 
                        onChange = {() => handleSubsequentAppeal(false)}
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        />} 
                        label="No" 
                        />
                </div>
            </div>
            {oipc.isinquiry && 
            <Grid container spacing={3}>
                <Grid item md={4}>
                    <TextField 
                        fullWidth
                        label="Comply By Date" 
                        variant="outlined" 
                        value={oipc.inquiryattributes.inquirydate ? formatDate(new Date(oipc.inquiryattributes.inquirydate)) : null}
                        onChange = {(event) => handleInquiryFields(event.target.value, "COMPLYDATE")}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { min: oipc.receiveddate ? formatDate(new Date(oipc.receiveddate)) : null } }}
                        type="date"
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.inquiryattributes.inquirydate === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    />
                </Grid>
                <Grid item md={4}>
                    <TextField 
                        fullWidth
                        label="Order No" 
                        variant="outlined" 
                        value={oipc.inquiryattributes.orderno}
                        onChange = {(event) => handleInquiryFields(event.target.value, "ORDERNO")}
                        InputLabelProps={{ shrink: true }}
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.inquiryattributes.orderno === ""}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                        placeholder="Order Number"
                    />
                </Grid>
                <Grid item md={4}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        onChange = {(event) => handleInquiryFields(event.target.value, "INQUIRYOUTCOME")}
                        fullWidth
                        value={oipc.inquiryattributes.inquiryoutcome}
                        label="Outcome"
                        error={(!oipc.outcomeid || oipc.outcomeid === 5) && oipc.inquiryattributes.inquiryoutcome === null}
                        required
                        disabled={oipc.outcomeid && oipc.outcomeid !== 5}
                    >   
                        {oipcInquiryoutcomes.map((inquiryoutcome) => {
                            return <MenuItem key={inquiryoutcome.inquiryoutcomeid} value={inquiryoutcome.inquiryoutcomeid}>{inquiryoutcome.name}</MenuItem>
                        })}
                    </TextField>
                </Grid>
            </Grid>
            }
        </>
    );
}

export default OIPCItem;