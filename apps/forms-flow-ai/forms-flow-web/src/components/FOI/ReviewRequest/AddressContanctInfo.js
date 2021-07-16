import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import Input from '@material-ui/core/Input';
import MenuItem from '@material-ui/core/MenuItem';
import { useSelector } from "react-redux";


const AddressContactDetails = React.memo(({requestDetails}) => {
    const countryList = useSelector(state=> state.foiRequests.foiCountryList);
    const provinceList = useSelector(state=> state.foiRequests.foiProvinceList);
    
    const [homePhoneText, setHomePhone] = React.useState(!!requestDetails.phonePrimary ? requestDetails.phonePrimary : "() -");
    const [mobilePhoneText, setMobilePhone] = React.useState(!!requestDetails.phoneSecondary ? requestDetails.phoneSecondary : "() -");
    const [workPhonePrimaryText, setWorkPhonePrimary] = React.useState("() -");
    const [workPhoneSecondaryText, setWorkPhoneSecondary] = React.useState("() -");

    const [streetAddressText, setStreetAddress] = React.useState(!!requestDetails.address ? requestDetails.address : "");
    const [secondaryStreetAddressText, setSecondaryStreetAddress] = React.useState("");
    const [CityText, setCity] = React.useState(!!requestDetails.city ? requestDetails.city : "");
    const [PostalText, setPostal] = React.useState(!!requestDetails.postal ? requestDetails.postal : "");    
    const [selectProvinceValue, setProvinceValue] = React.useState(!!requestDetails.province ? requestDetails.province : "Select Province");
    const [selectCountryValue, setCountryValue] = React.useState(!!requestDetails.country ? requestDetails.country : "Select Country");    

    
    const provinceItems = provinceList.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
     });
     const countryItems = countryList.map((item) => {    
        return ( <MenuItem key={item.name} value={item.name} disabled={item.name.toLowerCase().includes("select")}>{item.name}</MenuItem> )
     });

    const handleHomePhoneChange = (e) => {
        setHomePhone(e.target.value);
    }
    const handleMobilePhoneChange = (e) => {
        setMobilePhone(e.target.value);
    }
    const handleWorkPhonePrimaryChange = (e) => {
        setWorkPhonePrimary(e.target.value);
    }
    const handleWorkPhoneSecondarChange = (e) => {
        setWorkPhoneSecondary(e.target.value);
    }

    const handleStreetAddressChange = (e) => {
        setStreetAddress(e.target.value);
    }
    const handleScondaryStreetAddressChange = (e) => {
        setSecondaryStreetAddress(e.target.value);
    }
    const handleCityChange = (e) => {
        setCity(e.target.value);
    }
    const handlePostalChange = (e) => {
        setPostal(e.target.value);
    }

    const handleProvinceOnChange = (e) => {
        setProvinceValue(e.target.value);
    }

    const handleCountryOnChange = (e) => {
        setCountryValue(e.target.value);
    }

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">ADDRESS AND CONTACT INFORMATION</label>
            <CardContent>         
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">                       
                        <TextField 
                            id="outlined-homePhone" 
                            label="Home Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                            value={homePhoneText}
                            onChange={handleHomePhoneChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-mobilePhone" 
                            label="Mobile Phone" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={mobilePhoneText}
                            onChange={handleMobilePhoneChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-streetAddress" 
                            label="Street Address" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={streetAddressText}
                            onChange={handleStreetAddressChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-city" 
                            label="City" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={CityText}
                            onChange={handleCityChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-postalCode" 
                            label="Postal Code" 
                            InputLabelProps={{ shrink: true, }}                         
                            variant="outlined" 
                            value={PostalText}
                            onChange={handlePostalChange}
                            inputProps={{ maxLength: 6 }}
                            fullWidth
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-details-col">                       
                    <TextField 
                            id="outlined-workPhone1" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                           value={workPhonePrimaryText}
                           onChange={handleWorkPhonePrimaryChange}
                           fullWidth
                        />
                        <TextField 
                            id="outlined-workPhone2" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={workPhoneSecondaryText}
                            onChange={handleWorkPhoneSecondarChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-scondaryStreetAddress" 
                            label="Secondary Street Address" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={secondaryStreetAddressText}
                            onChange={handleScondaryStreetAddressChange}
                            fullWidth
                        />                        
                         <TextField
                            id="province"
                            label="Province"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectProvinceValue}
                            onChange={handleProvinceOnChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth                            
                        >            
                            {provinceItems}
                        </TextField> 
                         <TextField
                            id="country"
                            label="Country"
                            InputLabelProps={{ shrink: true, }}          
                            select
                            value={selectCountryValue}
                            onChange={handleCountryOnChange}
                            input={<Input />} 
                            variant="outlined"
                            fullWidth                            
                        >            
                            {countryItems}
                        </TextField> 
                    </div>
                </div>               
            </CardContent>
        </Card>
       
    );
  });

export default AddressContactDetails;