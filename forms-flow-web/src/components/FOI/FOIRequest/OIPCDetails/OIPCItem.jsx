import { TextField, Typography, Select, FormControl, FormControlLabel, MenuItem, InputLabel, Grid, Checkbox } from '@material-ui/core';
import { useState } from "react";

const OIPCItem = (props) => {
    const {oipcObj} = props;

    const [oipcData, setOipcData] = useState({
        oipcNumber: "", 
        reviewType: "", 
        reason: "", 
        status: "", 
        isInquiry: false, 
        inquiryDate: null, 
        receivedDate: "",
        complyDate: "",
        investigator: "", 
        outcome: "", 
        isJudicalReview: true, 
        isSubAppeal: true
    });
    
    const handleReviewType = () => {
        console.log("BANG")
    }

    return (
        <Grid container spacing={2}>
           <Grid item md={4}>
                <TextField 
                    fullWidth
                    label="OIPC No" 
                    variant="outlined" 
                    required={true}
                    value={oipcData.oipcNumber}
                    InputLabelProps={{ shrink: true }}
                />
            </Grid>
            <Grid item md={4}>
                <TextField
                    InputLabelProps={{ shrink: true }}
                    select
                    // input={<Input />}
                    variant="outlined"
                    fullWidth
                    value={oipcData.reviewType}
                    label="Review Type"
                    onChange={handleReviewType}
                    required={true}
                >
                    <MenuItem value={"Complaint"}>Complaint</MenuItem>
                    <MenuItem value={"Review"}>Review</MenuItem>
                    <MenuItem value={"Investigation"}>Investigation</MenuItem>
                </TextField>
            </Grid>
            <Grid item md={4}>
                <TextField
                    InputLabelProps={{ shrink: true }}
                    select
                    // input={<Input />}
                    variant="outlined"
                    fullWidth
                    value={oipcData.reason}
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
            <Grid item md={4}>
                <TextField
                    InputLabelProps={{ shrink: true }}
                    select
                    // input={<Input />}
                    variant="outlined"
                    fullWidth
                    value={oipcData.status}
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
            <Grid item md={4}>
                <TextField
                    fullWidth 
                    label="Investigator/Adjudicator" 
                    variant="outlined" 
                    required={true}
                    value={oipcData.investigator}
                    InputLabelProps={{ shrink: true }}
                />
            </Grid>
            <Grid item md={4}>
                <TextField
                    InputLabelProps={{ shrink: true }}
                    select
                    // input={<Input />}
                    variant="outlined"
                    fullWidth
                    value={oipcData.outcome}
                    label="Outcome"
                    onChange={handleReviewType}
                    required={true}
                >
                    <MenuItem value={"Abandoned"}>Abandoned</MenuItem>
                    <MenuItem value={"Withdrawn"}>Withdrawn</MenuItem>
                    <MenuItem value={"Resolved in Mediation"}>Resolved in Mediation</MenuItem>
                    <MenuItem value={"Closed"}>Closed</MenuItem>
                </TextField>
            </Grid>
            <Grid item md={4}>
                <Typography required={true}>In Inquiry?</Typography>
                <FormControlLabel required control={<Checkbox />} label="Yes" />
                <FormControlLabel required control={<Checkbox />} label="No" />
            </Grid>
            <Grid item md={4}>
                <Typography required={true}>In Judicial Review?</Typography>
                <FormControlLabel required control={<Checkbox />} label="Yes" />
                <FormControlLabel required control={<Checkbox />} label="No" />
            </Grid>
            <Grid item md={4}>
                <Typography required={true}>In Subsequent Appeal?</Typography>
                <FormControlLabel required control={<Checkbox />} label="Yes" />
                <FormControlLabel required control={<Checkbox />} label="No" />
            </Grid>
        </Grid>
    );
}

export default OIPCItem;