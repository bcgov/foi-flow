import React from 'react';
import Input from '@material-ui/core/Input';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import './selectwithlegend.scss';
import { useDispatch } from "react-redux";
import {
  setFOISelectedCategory,
  setIsRequiredError,
  setRequiredFields
} from "../../../actions/FOI/foiRequestActions";

const SelectWithLegend = React.memo(({
  id,
  selectData,
  selectDefault,
  legend,
  required
}) => {
   const menuItems = selectData.map((item) => {    
     return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
  });
 //item.applicantcategoryid === 0 || item.countryid === 0 || item.provinceid === 0 || item.requesttypeid || item.receivemodeid || item.deliverymodeid
  const dispatch = useDispatch();
   const [selectValue, setSelectValue] = React.useState(selectDefault);   
    const handleChange = (event) => {   
      setSelectValue(event.target.value);
      if (id === "category") {
        dispatch(setFOISelectedCategory(event.target.value));
        dispatch(setRequiredFields({property:id, value:event.target.value}));
      }
      // else if (id === "assignedTo") {

      // }
      // else if (id === "requestType") {

      // }
      // else if (id === "receivedMode") {

      // }
      // else if (id === "deliveryMode") {

      // }
      else {
        dispatch(setRequiredFields({property:id, value:event.target.value}));   
      }      
    };

//     const [isError, setIsError] = React.useState((legend === "Assigned To" || legend==="Category" || legend === "Request Type" || legend === "Received Mode" || legend === "Delivery Mode") && selectValue.toLowerCase().includes("select"));
// console.log(`legend = ${legend} selectValue = ${selectValue}`)
// console.log(`error = ${(legend === "Assigned To" || legend==="Category" || legend === "Request Type" || legend === "Received Mode" || legend === "Delivery Mode") && selectValue.toLowerCase().includes("select")}`)
   
     return (
        <TextField
          id={id}
          label={legend}
          InputLabelProps={{ shrink: true, }}          
          select
          value={selectValue}
          onChange={handleChange}
          input={<Input />} 
          variant="outlined"
          fullWidth
          required={required}
          error={(legend === "Assigned To" || legend === "Category" || legend === "Request Type" || legend === "Received Mode" || legend === "Delivery Mode") && selectValue.toLowerCase().includes("select")}
        >         
          {menuItems}
        </TextField> 
    );
  });

export default SelectWithLegend;