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
        reasonName: "", 
        statusName: oipcObj?.statusName, 
        outcomeName: oipcObj?.outcomeName,
    });

    console.log(oipc);
    
    //Functions
    const handleReviewType = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reviewtypeid = value;
        newOIPCObj.reasonid = -1;
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
    const generateNamesFromOIPCId = (oipcObj) => {
        const reviewtype = oipcReviewtypes.find(reviewtype => reviewtype.reviewtypeid === oipcObj.reviewtypeid);
        const status = oipcStatuses.find(status => status.statusid === oipcObj.statusid);
        const outcome = oipcOutcomes.find(outcome => outcome.outcomeid === oipcObj.outcomeid);

        oipcObj.reviewtypeName = reviewtype ? reviewtype.name : "";
        oipcObj.statusName = status ? status.name : "";
        oipcObj.outcomeName = outcome ? outcome.name : "";
    }

    //REFACTOR THIS!!!
    const filterReasonOptions = (reviewType) => {
        if (reviewType === "Complaint") {
            return ["Adequate search","Extension", "Fee Amount", "Fee Waiver", "Duty to Assist", "Other"];
        }
        if (reviewType === "Review") {
            return ["Application of Exceptions", "Deemed Refusal", "TPN - 22", "TPN - 21", "TPN - 18.1", "Reg 3", "Reg 4", "Reg 5", "s. 43", "Other"];
        }
        if (reviewType === "Investigation") {
            return ["Other"]
        }
        return ["Adequate search","Extension", "Fee Amount", "Fee Waiver", "Duty to Assist", "Application of Exceptions", "Deemed Refusal", "TPN - 22", "TPN - 21", "TPN - 18.1", "Reg 3", "Reg 4", "Reg 5", "s. 43", "Other"];
    }
    const reasons = filterReasonOptions(oipc.reviewType)

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
                    >
                        {oipcReviewtypes.map((reviewtype) => {
                            return <MenuItem key={reviewtype.reviewtypeid} value={reviewtype.reviewtypeid}>{reviewtype.name}</MenuItem>
                        })}
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        // value={getNameFromId("REASON", oipc.reasonid)}
                        label="Reason"
                        onChange = {(event) => handleReason(event.target.value)}
                        required={true}
                    >
                        {reasons.map((reason) => {
                            return <MenuItem key={reason} value={reason}>{reason}</MenuItem>
                        })}
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
                        required={true}
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
                        required={true}
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
                        required={true}
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
        </>
    );
}

export default OIPCItem;