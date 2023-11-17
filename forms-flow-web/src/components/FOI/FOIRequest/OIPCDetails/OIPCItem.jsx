import { TextField, FormControlLabel, MenuItem, Grid, Checkbox } from '@material-ui/core';
import { useState } from "react";

const OIPCItem = (props) => {
    const {oipcObj, updateOIPC} = props;

    const [oipc, setOipc] = useState({
        oipcNumber: oipcObj?.oipcNumber, 
        reviewType: oipcObj?.reviewType, 
        reason: oipcObj?.reason, 
        status: oipcObj?.status, 
        isInquiry: oipcObj?.isInquiry, 
        inquiryDate: null, 
        receivedDate: oipcObj?.receivedDate, 
        complyDate: oipcObj?.complyDate, 
        investigator: oipcObj?.investigator, 
        outcome: oipcObj?.outcome, 
        isJudicalReview: oipcObj?.isJudicalReview, 
        isSubAppeal: oipcObj?.isSubAppeal, 
    });

    console.log(oipcObj);
    
    const handleReviewType = (value) => {
        const newOIPCObj = oipc;
        newOIPCObj.reviewType = value;
        updateOIPC(newOIPCObj);
    }
    const handleOIPCNumber = (event) => {
        console.log("BANG");
    }
    const handleReceivedDate = (event) => {
        console.log("BANG");
    }
    const handleReason = (event) => {
        console.log("BANG");
    }
    const handleStatus = (event) => {
        console.log("BANG");
    }
    const handleInvestiagtor = (event) => {
        console.log("BANG");
    }
    const handleOutcome = (event) => {
        console.log("BANG");
    }
    const handleInquiry = (event) => {
        console.log("BANG");
    }
    const handleJudicalReview = (event) => {
        console.log("BANG");
    }
    const handleSubsequentAppeal = (event) => {
        console.log("BANG");
    }

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
                        // input={<Input />}
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
                        // input={<Input />}
                        InputLabelProps={{ shrink: true }}
                        type="date"
                        InputProps={{inputProps: { max: new Date()} }}
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        // input={<Input />}
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
                        // input={<Input />}
                        variant="outlined"
                        fullWidth
                        value={oipc.reason}
                        label="Reason"
                        onChange={handleReviewType}
                        required={true}
                    >
                        <MenuItem value={"Adequate search"}>Adequate search</MenuItem>
                        <MenuItem value={"Application of Exceptions"}>Application of Exceptions</MenuItem>
                        <MenuItem value={"Deemed Refusal"}>Deemed Refusal</MenuItem>
                        <MenuItem value={"Extension"}>Extension</MenuItem>
                        <MenuItem value={"Fee Amount"}>Fee Amount</MenuItem>
                        <MenuItem value={"Fee Waiver"}>Fee Waiver</MenuItem>
                        <MenuItem value={"Records do Not Exist"}>Records do Not Exist</MenuItem>
                        <MenuItem value={"Duty to Assist"}>Duty to Assist</MenuItem>
                        <MenuItem value={"TPN - 22"}>TPN - 22</MenuItem>
                        <MenuItem value={"TPN - 21"}>TPN - 21</MenuItem>
                        <MenuItem value={"TPN - 18.1"}>TPN - 18.1</MenuItem>
                        <MenuItem value={"Reg 3"}>Reg 3</MenuItem>
                        <MenuItem value={"Reg 4"}>Reg 4</MenuItem>
                        <MenuItem value={"Reg 5"}>Reg 5</MenuItem>
                        <MenuItem value={"s. 43"}>s. 43</MenuItem>
                        <MenuItem value={"Other"}>Other</MenuItem>
                    </TextField>
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        // input={<Input />}
                        variant="outlined"
                        fullWidth
                        value={oipc.status}
                        label="Status"
                        onChange={handleReviewType}
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
                        value={oipc.investigator}
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item md={3}>
                    <TextField
                        InputLabelProps={{ shrink: true }}
                        select
                        // input={<Input />}
                        variant="outlined"
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
                    <FormControlLabel required control={<Checkbox checked={oipc.isInquiry} />} label="Yes" />
                    <FormControlLabel required control={<Checkbox checked={!oipc.isInquiry}  />} label="No" />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Judicial Review?</p>
                    <FormControlLabel required control={<Checkbox checked={oipc.isJudicalReview} />} label="Yes" />
                    <FormControlLabel required control={<Checkbox checked={!oipc.isJudicalReview} />} label="No" />
                </div>
                <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                    <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Subsequent Appeal?</p>
                    <FormControlLabel required control={<Checkbox checked={oipc.isSubAppeal} />} label="Yes" />
                    <FormControlLabel required control={<Checkbox checked={!oipc.isSubAppeal}/>} label="No" />
                </div>
            </div>
        </>
    );
}

export default OIPCItem;