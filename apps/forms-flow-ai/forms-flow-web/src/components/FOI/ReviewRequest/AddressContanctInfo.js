import React, {useEffect} from 'react';
import "./addresscontactinfo.scss";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import { SelectWithLegend } from '../customComponents';
import { useSelector } from "react-redux";

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));
const AddressContactDetails = React.memo((props) => {
    const countryList = useSelector(state=> state.foiRequests.foiCountryList);
    const provinceList = useSelector(state=> state.foiRequests.foiProvinceList);
    useEffect(() => {       
        
    }, [])    
    const classes = useStyles();
     return (
        
        <Card className="foi-address-details-card">            
            <label className="foi-address-details-label">ADDRESS AND CONTACT INFORMATION</label>
            <CardContent>
            <form className={classes.root} noValidate autoComplete="off">
                <div className="row foi-address-details-row">
                    <div className="col-lg-6 foi-address-details-col">                       
                        <TextField 
                            id="outlined-homePhone" 
                            label="Home Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            defaultValue="(123) 456-7890"
                        />
                        <TextField 
                            id="outlined-mobilePhone" 
                            label="Mobile Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="(123) 456-7890" 
                            variant="outlined" 
                        />
                        <TextField 
                            id="outlined-streetAddress" 
                            label="Street Address" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="111 Main Street" 
                            variant="outlined" 
                        />
                        <TextField 
                            id="outlined-city" 
                            label="City" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="Vancouver" 
                            variant="outlined" 
                        />
                        <TextField 
                            id="outlined-postalCode" 
                            label="Postal Code" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="- -" 
                            variant="outlined" 
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-address-details-col">                       
                    <TextField 
                            id="outlined-workPhone1" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            defaultValue="() -"
                        />
                        <TextField 
                            id="outlined-workPhone2" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="() -" 
                            variant="outlined" 
                        />
                        <TextField 
                            id="outlined-scondaryStreetAddress" 
                            label="Secondary Street Address" 
                            InputLabelProps={{ shrink: true, }} 
                            defaultValue="111 Main Street" 
                            variant="outlined" 
                        />                        
                         <SelectWithLegend selectData = {provinceList} legend="Province" selectDefault="Select Province" required={false}/>
                         <SelectWithLegend selectData = {countryList} legend="Country" selectDefault="Select Country" required={false}/>
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default AddressContactDetails;