import './attachments.scss'
import {
    ClickableChip  
} from "../../Dashboard/utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import type { params } from './types';

const AttachmentFilter = ({handleFilterChange, filterValue, handleKeywordChange, keyWordValue, isMinistryCoordinator}: params) => {
    return (   
        <Grid item container alignItems="center" xs={12} sx={{ display: "inline-block"}}>
            <Paper
                component={Grid}
                sx={{
                    border: "1px solid #38598A",
                    color: "#38598A", 
                    maxWidth:"100%"
                }}
                alignItems="center"
                justifyContent="center"
                direction="row"
                container
                item
                xs={12}
                elevation={0}
            >
                <Grid
                    item
                    container
                    alignItems="center"
                    direction="row"
                    xs={true}
                    sx={{
                        borderRight: "2px solid #38598A",
                        backgroundColor: "rgba(56,89,138,0.1)",
                    }}
                >
                    <label className="hideContent">Search Attachments</label>
                    <InputBase
                        id="foicommentfilter"
                        placeholder="Search Attachments..."
                        defaultValue={""}
                        onChange={(e)=>{handleKeywordChange(e.target.value.trim())}}
                        sx={{
                            color: "#38598A",
                        }}
                        startAdornment={
                            <InputAdornment position="start">
                            <IconButton sx={{ color: "#38598A" }}>
                                <span className="hideContent">Search Attachments</span>
                                <SearchIcon />
                            </IconButton>
                            </InputAdornment>
                        }
                        fullWidth
                    />
                </Grid>
                <Grid
                    item
                    container
                    alignItems="flex-start"
                    justifyContent="center"
                    xs={true}
                    sx={{
                        width: "300px",
                        maxWidth: "300px !important",
                    }}
                >
                    <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
                        <ClickableChip
                            id="generalAttachments"
                            key={`general-attachments`}
                            label={"GENERAL"}
                            color="primary"
                            size="small"
                            onClick={()=>{handleFilterChange('GENERAL')}}
                            clicked={filterValue == 'GENERAL'}
                        />
                        {!isMinistryCoordinator && (<ClickableChip
                            id="applicantAttachments"
                            key={`applicant-attachments`}
                            label={"APPLICANT"}
                            color="primary"
                            size="small"
                            onClick={()=>{handleFilterChange('APPLICANT')}}
                            clicked={filterValue == 'APPLICANT'}
                        />)}
                        <ClickableChip
                            id="extensionsAttachments"
                            key={`extensions-attachments`}
                            label={"EXTENSIONS"}
                            color="primary"
                            size="small"
                            onClick={()=>{handleFilterChange('EXTENSIONS')}}
                            clicked={filterValue == 'EXTENSIONS'}
                        />

                        <ClickableChip
                            id="allAttachments"
                            key={`all-attachments`}
                            label={"ALL"}
                            color="primary"
                            size="small"
                            onClick={()=>{handleFilterChange('')}}
                            clicked={filterValue == ''}
                        />
                    </Stack>
                </Grid>
            </Paper>
        </Grid>  
    );
}

export default AttachmentFilter;