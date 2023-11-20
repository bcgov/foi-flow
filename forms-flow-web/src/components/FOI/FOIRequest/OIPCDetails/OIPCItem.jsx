import { TextField, FormControlLabel, MenuItem, Grid, Checkbox } from '@material-ui/core';
import { useState } from "react";
import { formatDate } from "../../../../helper/FOI/helper";


const OIPCItem = (props) => {
    const {oipcObj, updateOIPC} = props;

    const [oipc, setOipc] = useState({
        oipcNumber: oipcObj?.oipcNumber, 
        reviewType: oipcObj?.reviewType, 
        reason: oipcObj?.reason, 
        status: oipcObj?.status, 
        isInquiry: oipcObj?.isInquiry, 
        receivedDate: oipcObj?.receivedDate, 
        investigator: oipcObj?.investigator, 
        outcome: oipcObj?.outcome, 
        isJudicalReview: oipcObj?.isJudicalReview, 
        isSubAppeal: oipcObj?.isSubAppeal, 
    });

    console.log(oipcObj);
    
    const handleReviewType = (value) => {
        updateOIPC({...oipc, reviewType: value, reason: ""});
    }
    const handleOIPCNumber = (value) => {
        updateOIPC({...oipc, oipcNumber: value});
    }
    const handleReceivedDate = (value) => {
        updateOIPC({...oipc, receivedDate: value});
    }
    const handleReason = (value) => {
        updateOIPC({...oipc, reason: value});
    }
    const handleStatus = (value) => {
        updateOIPC({...oipc, status: value});
    }
    const handleInvestiagtor = (value) => {
        updateOIPC({...oipc, investigator: value});
    }
    const handleOutcome = (value) => {
        updateOIPC({...oipc, outcome: value});
    }
    const handleInquiry = (value) => {
        updateOIPC({...oipc, isInquiry: value});
    }
    const handleJudicalReview = (value) => {
        updateOIPC({...oipc, isJudicalReview: value});
    }
    const handleSubsequentAppeal = (value) => {
        updateOIPC({...oipc, isSubAppeal: value});
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
            return ["Other"];
        }
        return ["Adequate search","Extension", "Fee Amount", "Fee Waiver", "Duty to Assist", "Application of Exceptions", "Deemed Refusal", "TPN - 22", "TPN - 21", "TPN - 18.1", "Reg 3", "Reg 4", "Reg 5", "s. 43", "Other"];
    }

    const reasons = filterReasonOptions(oipc.reviewType);

    return (
        <>
            <Grid container spacing={1}>
            <Grid item md={3}>
                    <TextField 
                        fullWidth
                        label="OIPC No" 
                        variant="outlined" 
                        required={true}
                        value={oipc.oipcNumber}
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
                        value={oipc.receivedDate}
                        onChange = {(event) => handleReceivedDate(event.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{inputProps: { max: oipc.receivedDate || formatDate(new Date())} }}
                        type="date"
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        value={oipc.reviewType}
                        label="Review Type"
                        onChange={(event) => handleReviewType(event.target.value)}
                        required={true}
                    >
                        <MenuItem value={"Complaint"}>Complaint</MenuItem>
                        <MenuItem value={"Review"}>Review</MenuItem>
                        <MenuItem value={"Investigation"}>Investigation</MenuItem>
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        variant="outlined"
                        fullWidth
                        value={oipc.reason}
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
                        value={oipc.status}
                        label="Status"
                        onChange = {(event) => handleStatus(event.target.value)}
                        required={true}
                    >
                        <MenuItem value={"Mediation"}>Mediation</MenuItem>
                        <MenuItem value={"Investigation"}>Investigation</MenuItem>
                        <MenuItem value={"Inquiry"}>Inquiry</MenuItem>
                        <MenuItem value={"Awaiting Order"}>Awaiting Order</MenuItem>
                        <MenuItem value={"Closed"}>Closed</MenuItem>
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
                        value={oipc.outcome}
                        label="Outcome"
                        required={true}
                    >
                        <MenuItem value={"Abandoned"}>Abandoned</MenuItem>
                        <MenuItem value={"Withdrawn"}>Withdrawn</MenuItem>
                        <MenuItem value={"Resolved in Mediation"}>Resolved in Mediation</MenuItem>
                        <MenuItem value={"Closed"}>Closed</MenuItem>
                    </TextField>
                </Grid>
            </Grid>
            <div style={{display:"flex", flexDirection: "row", justifyContent: "space-between"}}>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Inquiry?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isInquiry} 
                        onChange = {() => handleInquiry(true)}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isInquiry} 
                        onChange = {() => handleInquiry(false)}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Judicial Review?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isJudicalReview} 
                        onChange = {() => handleJudicalReview(true)}
                        />} 
                        label="Yes" 
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isJudicalReview} 
                        onChange = {() => handleJudicalReview(false)}
                        />} 
                        label="No" 
                        />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Subsequent Appeal?</p>
                    <FormControlLabel control={<Checkbox 
                        checked={oipc.isSubAppeal} 
                        onChange = {() => handleSubsequentAppeal(true)}
                        />} 
                        label="Yes"
                        />
                    <FormControlLabel control={<Checkbox 
                        checked={!oipc.isSubAppeal} 
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