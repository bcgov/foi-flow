import React from 'react';
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import './cfrstatus.scss';


const CFRStatus = React.memo((_props) => {

    const statusList =[{id:"0", status:"Select CFR stage"},{id:"1", status:"CFR status 1"}, {id:"2", status:"CFR status 2"}] 
    const menuItems = statusList.length > 0 && statusList.map((item) => {
        
        return (        
        <MenuItem  className="foi-cfrstate-menuitem" key={item.id} value={item.status} >
            <span className={`foi-menuitem-span ${item.status.toLowerCase().replace(/\s/g, '')}`} ></span>
            {item.status}
        </MenuItem> 
        )
     });
return(

    <TextField
                id="foi-cfrstatus-dropdown"
                className="foi-cfrstate-dropdown"
                InputLabelProps={{ shrink: true, }}         
                select                               
                input={<Input />} 
                variant="outlined"
                fullWidth
                value="Select CFR stage"
                label="Request CFR Stage"
                
            >                
            
                {menuItems}
            </TextField>


);

})


export default CFRStatus