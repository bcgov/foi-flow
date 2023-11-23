import { TextField, FormControlLabel, MenuItem, Grid, Checkbox } from '@material-ui/core';
import { useState, useEffect } from "react";
import { formatDate } from "../../../../helper/FOI/helper";
import { useSelector } from "react-redux";

const OIPCItem = (props) => {
    const {oipcObj, updateOIPC} = props;
    
    //App State
    const oipcOutcomes = useSelector(state=> state.foiRequests.oipcOutcomes);
    const oipcStatuses = useSelector(state=> state.foiRequests.oipcStatuses);
    const oipcReviewtypes = useSelector(state=> state.foiRequests.oipcReviewtypes);
    const oipcInquiryoutcomes = useSelector(state=> state.foiRequests.oipcInquiryoutcomes);

    //Local State
    const [oipc, setOipc] = useState({
        id: oipcObj?.id, 
        oipcno: oipcObj?.oipcno, 
        reviewtypeid: oipcObj?.reviewtypeid, 
        reasonid: oipcObj?.reasonid, 
        statusid: oipcObj?.statusid, 
        isinquiry: oipcObj?.isinquiry, 
        inquiryattributes: oipcObj?.inquiryattributes,  
        receiveddate: oipcObj?.receiveddate,
        closeddate: oipcObj?.closeddate,
        investigator: oipcObj?.investigator, 
        outcomeid: oipcObj?.outcomeid, 
        isjudicialreview: oipcObj?.isjudicialreview, 
        reviewtypeName: oipcObj?.reviewtypeName,
        reasonName: oipcObj?.reasonName, 
        statusName: oipcObj?.statusName, 
        outcomeName: oipcObj?.outcomeName,
    });

    console.log(oipc);
    
    //Functions
    const handleReviewType = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reviewtypeid = value;
        newOIPCObj.reasonid = null;
        updateOIPC(newOIPCObj);
    }
    const handleOIPCNumber = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.oipcno = value;
        updateOIPC(newOIPCObj);
    }
    const handleReceivedDate = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.receiveddate = value;
        updateOIPC(newOIPCObj);
    }
    const handleClosedDate = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.closeddate = value;
        updateOIPC(newOIPCObj);
    }
    const handleReason = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reasonid = value;
        updateOIPC(newOIPCObj);
    }
    const handleStatus = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.statusid = value;
        updateOIPC(newOIPCObj);
    }
    const handleInvestiagtor = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.investigator = value;
        updateOIPC(newOIPCObj);
    }
    const handleOutcome = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.outcomeid = value;
        updateOIPC(newOIPCObj);
    }
    const handleInquiry = (value) => {
        const newOIPCObj = oipc;
        if (value === false) {
            newOIPCObj.inquiryattributes = null;
        } else {
            newOIPCObj.inquiryattributes = {
                inquirydate: "",
                orderno: "",
                inquiryoutcomeid: null,
            };
        }
        newOIPCObj.isinquiry = value;
        updateOIPC(newOIPCObj);
    }
    const handleJudicalReview = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.isjudicialreview = value;
        updateOIPC(newOIPCObj);
    }
    const handleSubsequentAppeal = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.issubsequentappeal = value;
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
            newOIPCObj.inquiryattributes.inquiryoutcomeid = value;
        }
        updateOIPC(newOIPCObj);
    }
    const generateNamesFromOIPCId = (oipcObj) => {
        const reviewtype = oipcReviewtypes.find(reviewtype => reviewtype.reviewtypeid === oipcObj.reviewtypeid && reviewtype.reasonid === oipcObj.reasonid);
        const status = oipcStatuses.find(status => status.statusid === oipcObj.statusid);
        const outcome = oipcOutcomes.find(outcome => outcome.outcomeid === oipcObj.outcomeid);

        oipcObj.reviewtypeName = reviewtype ? reviewtype.type_name : "";
        oipcObj.statusName = status ? status.name : "";
        oipcObj.outcomeName = outcome ? outcome.name : "";
        oipcObj.reasonName = reviewtype ? reviewtype.reason_name : "";
    }
    const uniqueReviewTypes = (oipcReviewTypes) => {
        const uniqeValues = {};
        return oipcReviewTypes.filter(reviewtype => !uniqeValues[reviewtype.type_name] && (uniqeValues[reviewtype.type_name] = true));
    }

    //useEffect to create name attributes using id's for oipcObject
    useEffect(() => {
        generateNamesFromOIPCId(oipcObj);
    }, [oipcObj])

    return (
        <>
            <Grid container spacing={1}>
            <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="OIPC No" 
                        variant="outlined" 
                        required={true}
                        value={oipc.oipcno}
                        onChange = {(event) => handleOIPCNumber(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        error={oipc.oipcno === ""}
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="Received Date" 
                        variant="outlined" 
                        required={true}
                        value={oipc.receiveddate}
                        onChange = {(event) => handleReceivedDate(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { max: oipc.receiveddate || formatDate(new Date())} }}
                        type="date"
                        error={oipc.receiveddate === ""}
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
                        required={true}
                        error={oipc.reviewtypeid === null}
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
                        required={true}
                        error={oipc.reasonid === null}
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
                        required={true}
                        error={oipc.statusid === null}
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
                            return <MenuItem key={outcome.outcomeid} value={outcome.outcomeid}>{outcome.name}</MenuItem>
                        })}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="Closed Date" 
                        variant="outlined" 
                        value={oipc.closeddate}
                        onChange = {(event) => handleClosedDate(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { max: oipc.closeddate || formatDate(new Date())} }}
                        type="date"
                    />
                </Grid>
            </Grid>
            <div style={{display:"flex", flexDirection: "row", justifyContent: "space-between"}}>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Inquiry?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isinquiry} 
                        onChange = {() => handleInquiry(true)}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isinquiry} 
                        onChange = {() => handleInquiry(false)}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Judicial Review?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isjudicialreview} 
                        onChange = {() => handleJudicalReview(true)}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isjudicialreview} 
                        onChange = {() => handleJudicalReview(false)}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Subsequent Appeal?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.issubsequentappeal} 
                        onChange = {() => handleSubsequentAppeal(true)}
                        />} 
                        label="Yes"
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.issubsequentappeal} 
                        onChange = {() => handleSubsequentAppeal(false)}
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
                        required={true}
                        value={oipc.inquiryattributes.inquirydate}
                        onChange = {(event) => handleInquiryFields(event.target.value, "COMPLYDATE")}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { min: oipc.receiveddate } }}
                        type="date"
                        error={oipc.inquiryattributes.inquirydate === ""}
                    />
                </Grid>
                <Grid item md={4}>
                    <TextField 
                        fullWidth
                        label="Order No" 
                        variant="outlined" 
                        required={true}
                        value={oipc.inquiryattributes.orderno}
                        onChange = {(event) => handleInquiryFields(event.target.value, "ORDERNO")}
                        InputLabelProps={{ shrink: true }}
                        error={oipc.inquiryattributes.orderno === ""}
                    />
                </Grid>
                <Grid item md={4}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        required={true}
                        variant="outlined"
                        onChange = {(event) => handleInquiryFields(event.target.value, "INQUIRYOUTCOME")}
                        fullWidth
                        value={oipc.inquiryattributes.inquiryoutcomeid}
                        label="Outcome"
                        error={oipc.inquiryattributes.inquiryoutcomeid === null}
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