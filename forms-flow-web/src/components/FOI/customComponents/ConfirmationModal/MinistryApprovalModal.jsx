import TextField from '@mui/material/TextField';

const MinistryApprovalModal = (props) => {
  const {handleApprovalInputs} = props;

  return (
    <div className="ministry-approver-main" style={{display: "flex", flexDirection: "row", justifyContent: "center", alignItems: "center", padding: "10px 0px 30px 0px"}}>
      <TextField 
        variant="outlined" 
        name="name" 
        label="Approver Name"
        InputLabelProps={{required: true}}
        style={{paddingRight:"20px"}}
        size="small"
        inputProps={{style: {width: "200px",}}}  
        onChange={(event) => {handleApprovalInputs(event)}}/>
      <TextField 
        variant="outlined" 
        name="title" 
        label="Approver Title"
        InputLabelProps={{required: true}}
        style={{paddingRight:"20px"}}
        size="small"
        inputProps={{style: {width: "200px",}}}  
        onChange={(event) => {handleApprovalInputs(event)}}/>
      <TextField 
        type="date" 
        name="datePicker"
        label="Date Approved"  
        onChange={(event) => {handleApprovalInputs(event)}}
        inputProps={{style: {width: "200px",}}}  
        InputLabelProps={{ shrink: true, required: true}}
        size="small"
        />
    </div>
    );
}

export default MinistryApprovalModal;