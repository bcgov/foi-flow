import React from 'react';
import Input from '@material-ui/core/Input';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import './selectwithlegend.scss';
import { useDispatch } from "react-redux";
import {
  setFOISelectedCategory
} from "../../../actions/FOI/foiRequestActions";

const SelectWithLegend = React.memo(({
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
      dispatch(setFOISelectedCategory(event.target.value));
    };
    

   
     return (
       <>
             {/* <fieldset className="form-group p-3 foi-select-fieldset"> */}
            
              {/* <legend className="w-auto px-2 foi-mandatory-legend">{legendValue}</legend> */}
                {/* <InputLabel id="demo-simple-select-label" className="foi-select-label">{labelValue}</InputLabel> */}
                      {/* <Select
                        labelId="demo-simple-select-label"
                        id="demo-simple-select"
                        value={selectValue}
                        renderValue={(selected) => {
                          if (selected.length === 0) {
                            return legendValue === 'Category' ? <em>Select Category</em> : <em>Placeholder</em>;
                          }
              
                          return selected.join(', ');
                        }}
                        onChange={handleChange}
                        >
                           {legendValue === 'Category'?
                            <MenuItem disabled key="0" value="">
                              <em>Select Category</em>
                            </MenuItem>
                            : null}
                          {menuItems}                          
                        </Select>                 */}
 {/* <form className={classes.root} noValidate autoComplete="off"> */}
        <TextField
          label={legend}
          InputLabelProps={{ shrink: true, }} 
          // displayEmpty
          select
          value={selectValue}
          onChange={handleChange}
          input={<Input />}         
          // MenuProps={MenuProps}          
          variant="outlined"
          // inputProps={{ 'aria-label': 'Without label' }}
          // defaultValue="SELECT"
          fullWidth
          required={required}
        >
          {/* {legend === 'Category'?
          <MenuItem selected disabled key="0" value="">
            <em>Select Category</em>            
          </MenuItem>: (legend === 'Assigned To *')?
          <MenuItem selected disabled key="0" value="">
            <em>Assigned To</em>            
          </MenuItem>:null  
        }          */}
          {menuItems}
        </TextField>
        {/* </form> */}
         {/* </fieldset> */}
          </>

    
    );
  });

export default SelectWithLegend;