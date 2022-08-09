import './index.scss'
import  { params } from './types'
import {
  ClickableChip  
} from "../../../Dashboard/utils";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";

export  const CommentFilter = ({oncommentfilterchange, filterValue,oncommentfilterkeychange}:params) => {

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
  xs={11}
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
    <label className="hideContent">Search Comments</label>
    <InputBase
      id="foicommentfilter"
      placeholder="Search Comments ..."
      defaultValue={""}
      onChange={(e)=>{oncommentfilterkeychange(e.target.value.trim())}}
      sx={{
        color: "#38598A",
      }}
      startAdornment={
        <InputAdornment position="start">
          <IconButton sx={{ color: "#38598A" }}>
            <span className="hideContent">Search Comments</span>
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
  >
    <Stack direction="row" sx={{ overflowX: "hidden" }} spacing={1}>
      <ClickableChip
        id="myRequests"
        key={`my-requests`}
        label={"User Comments"}
        color="primary"
        size="small"
        onClick={()=>{oncommentfilterchange(1)}}
        clicked={filterValue == 1}
      />
      <ClickableChip
        id="teamRequests"
        key={`team-requests`}
        label={"Request History Comments"}
        color="primary"
        size="small"
        onClick={()=>{oncommentfilterchange(2)}}
        clicked={filterValue == 2}
      />
      <ClickableChip
        id="watchingRequests"
        key={`watching-requests`}
        label={"Divisional Tracking"}
        color="primary"
        size="small"
        onClick={()=>{oncommentfilterchange(3)}}
        clicked={filterValue == 3}
      />
       
      <ClickableChip
        id="allComments"
        key={`all-requests`}
        label={"All"}
        color="primary"
        size="small"
        onClick={()=>{oncommentfilterchange(-1)}}
        clicked={filterValue == -1}
      />
    </Stack>
  </Grid>
</Paper>
</Grid>  
);

}

export default CommentFilter;