import './index.scss'
import  { params } from './types'
import Grid from "@mui/material/Grid";
import SearchIcon from "@material-ui/icons/Search";
import InputAdornment from "@mui/material/InputAdornment";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";

export  const RequestFilter = ({oncommentfilterkeychange}:params) => {

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
    <label className="hideContent">Search Request History</label>
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
            <span className="hideContent">Search Request History</span>
            <SearchIcon />
          </IconButton>
        </InputAdornment>
      }
      fullWidth
    />
  </Grid>
</Paper>
</Grid>  
);
}

export default RequestFilter;