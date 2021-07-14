import React, {useEffect} from 'react';
import Link from '@material-ui/core/Link';
import { useSelector } from "react-redux";
import "./reviewrequestheader.scss";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';

import { SelectWithLegend } from '../customComponents';

const ReviewRequestHeader = React.memo(({selectAssignedToValue, handleAssignedToOnChange}) => {
  
    useEffect(() => {       
        //console.log(`formdata = ${props.location.state.reviewRequestData}`)
    }, [])

   
    const assignedToList = useSelector(state=> state.foiRequests.foiAssignedToList);
    const menuItems = assignedToList.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("unassigned")}>{item.name}</MenuItem> )
     });
    const preventDefault = (event) => event.preventDefault();

     return (
        <div className="foi-request-review-header-row1">
            <div className="foi-request-review-header-col1">
                <div className="foi-request-review-header-col1-row">
                    <Link href="#" onClick={preventDefault}>
                        <h3 className="foi-review-request-text">Review Request</h3>
                    </Link>
                    <h3 className="foi-period-text">  |  </h3>
                    <Link href="#" onClick={preventDefault}>
                    <h3 className="foi-correspondence-text"> Correspondence</h3>
                    </Link>
                </div>            
            <div className="foi-request-status">
                UnOpened
            </div>
            </div>
            
            <div className="foi-assigned-to-container">
                <div className="foi-assigned-to-inner-container">
                {/* <SelectWithLegend id="assignedTo" selectData = {assignedToList} legend="Assigned To" selectDefault="Unassigned" required={true} />                 */}
                <TextField
                    id="assignedTo"
                    label="Assigned To"
                    InputLabelProps={{ shrink: true, }}          
                    select
                    value={selectAssignedToValue}
                    onChange={handleAssignedToOnChange}
                    input={<Input />} 
                    variant="outlined"
                    fullWidth
                    required
                    error={selectAssignedToValue.toLowerCase().includes("unassigned")}
                >            
                    {menuItems}
                </TextField> 
                </div>
            </div>
        </div>
    );
  });

export default ReviewRequestHeader;