import React, { useState } from 'react';
import TextField from '@mui/material/TextField';

const MinistryApprovalModal = (props) => {
  const {setApprovalState} = props;

  const handleInputs = (event) => {
    if(event.target.name === "name") {
      setApprovalState((prevState) => {
        return {...prevState, name: event.target.value}
      })
    }
    if(event.target.name === "title") {
      setApprovalState((prevState) => {
        return {...prevState, title: event.target.value}
      })
    }
    if(event.target.name === "datePicker") {
      setApprovalState((prevState) => {
        return {...prevState, date: event.target.value}
      })
    }
  }
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
        onChange={handleInputs}/>
      <TextField 
        variant="outlined" 
        name="title" 
        label="Approver Title"
        InputLabelProps={{required: true}}
        style={{paddingRight:"20px"}}
        size="small"
        inputProps={{style: {width: "200px",}}}  
        onChange={handleInputs}/>
      <TextField 
        type="date" 
        name="datePicker"
        label="Date Approved"  
        onChange={handleInputs}
        inputProps={{style: {width: "200px",}}}  
        InputLabelProps={{ shrink: true, required: true}}
        size="small"
        />
    </div>
    );
}

export default MinistryApprovalModal;