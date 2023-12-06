import { TextField, FormControlLabel, Grid, Checkbox, Divider } from '@material-ui/core';
import './oipcdetails.scss';

const OIPCDetailsMinistry = (props) => {
    const {oipcData} = props;

    return (
        <div> 
            {oipcData.map((oipc, index) => {
                return (
                    <>
                    <Grid container spacing={1} key={oipc.id}>
                        <Grid item md={3}>
                            <TextField 
                            fullWidth
                            label="OIPC No" 
                            variant="standard" 
                            value={oipc.oipcno}
                            InputProps={{ readOnly: true}}  
                        />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Received Date" 
                                variant="standard" 
                                value={oipc.receiveddate}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Review Type"
                                variant="standard" 
                                value={oipc.reviewtype}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Reason"
                                variant="standard" 
                                value={oipc.reason}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Status"
                                variant="standard" 
                                value={oipc.status}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Investigator/Adjudicator" 
                                variant="standard" 
                                value={oipc.investigator}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Outcome"
                                variant="standard" 
                                value={oipc.outcome}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        <Grid item md={3}>
                            <TextField 
                                fullWidth
                                label="Closed Date" 
                                variant="standard" 
                                value={oipc.closeddate}
                                InputProps={{ readOnly: true}}  
                            />
                        </Grid>
                        </Grid>
                        <div style={{display:"flex", flexDirection: "row", justifyContent: "space-between"}}>
                        <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                            <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Inquiry?</p>
                            <FormControlLabel control={<Checkbox 
                                checked={oipc.isinquiry} 
                                disabled
                                />} 
                                label="Yes" 
                                />
                            <FormControlLabel control={<Checkbox 
                                checked={!oipc.isinquiry} 
                                disabled
                                />} 
                                label="No" 
                                />
                        </div>
                        <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                            <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Judicial Review?</p>
                            <FormControlLabel control={<Checkbox 
                                checked={oipc.isjudicialreview} 
                                disabled
                                />} 
                                label="Yes" 
                                />
                            <FormControlLabel control={<Checkbox 
                                checked={!oipc.isjudicialreview} 
                                disabled
                                />} 
                                label="No" 
                                />
                        </div>
                        <div style={{display:"flex", flexDirection: "row", alignItems: "center"}}>
                            <p style={{padding: "7px 15px 0px", fontSize: "15px"}}>In Subsequent Appeal?</p>
                            <FormControlLabel control={<Checkbox 
                                checked={oipc.issubsequentappeal} 
                                disabled
                                />} 
                                label="Yes"
                                />
                            <FormControlLabel control={<Checkbox 
                                checked={!oipc.issubsequentappeal} 
                                disabled
                                />} 
                                label="No" 
                                />
                        </div>
                        </div>
                    {index !== (oipcData?.length - 1)  && <Divider/>}
                    </>
                )
            })}
        </div>
    );
}

export default OIPCDetailsMinistry;