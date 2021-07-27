import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import Input from '@material-ui/core/Input';
import MenuItem from '@material-ui/core/MenuItem';
import { useSelector } from "react-redux";
import {getCountryList, getProvinceList} from '../../../services/FOI/CountryProvinceListervice';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const AddressContactDetails = React.memo(({requestDetails, createSaveRequestObject}) => {

    /**
     *  Address and Contact box in the UI
     *  No mandatory fields here
     */ 
    
    //get the master data for country and province
    const countryList = getCountryList();//useSelector(state=> state.foiRequests.foiCountryList);
    //const provinceList = useSelector(state=> state.foiRequests.foiProvinceList);
    
    //local state management for homePhone, mobilePhone, workPhone1, workPhone2, streetAddress1, streetAddress2, city, postalcode, province and country
    const [homePhoneText, setHomePhone] = React.useState(!!requestDetails.phonePrimary ? requestDetails.phonePrimary : "() -");
    const [mobilePhoneText, setMobilePhone] = React.useState(!!requestDetails.phoneSecondary ? requestDetails.phoneSecondary : "() -");
    const [workPhonePrimaryText, setWorkPhonePrimary] = React.useState("() -");
    const [workPhoneSecondaryText, setWorkPhoneSecondary] = React.useState("() -");
    const [streetAddressText, setStreetAddress] = React.useState(!!requestDetails.address ? requestDetails.address : "");
    const [secondaryStreetAddressText, setSecondaryStreetAddress] = React.useState("");
    const [CityText, setCity] = React.useState(!!requestDetails.city ? requestDetails.city : "");
    const [PostalText, setPostal] = React.useState(!!requestDetails.postal ? requestDetails.postal : "");
    const [ProvinceText, setProvince] = React.useState(!!requestDetails.province ? requestDetails.province : "");
    const [CountryText, setCountry] = React.useState(!!requestDetails.country ? requestDetails.country : ""); 
    
    const handleHomePhoneChange = (e) => {
        setHomePhone(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.HOME_PHONE, e.target.value);
    }
    const handleMobilePhoneChange = (e) => {
        setMobilePhone(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.MOBILE_PHONE, e.target.value);
    }
    const handleWorkPhonePrimaryChange = (e) => {
        setWorkPhonePrimary(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY, e.target.value);
    }
    const handleWorkPhoneSecondarChange = (e) => {
        setWorkPhoneSecondary(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY, e.target.value);
    }

    const handleStreetAddressChange = (e) => {
        setStreetAddress(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY, e.target.value);
    }
    const handleScondaryStreetAddressChange = (e) => {
        setSecondaryStreetAddress(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY, e.target.value);
    }
    const handleCityChange = (e) => {
        setCity(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CITY, e.target.value);
    }
    const handlePostalChange = (e) => {
        setPostal(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.POSTALCODE, e.target.value);
    }

    const handleProvinceChange = (e) => {
        setProvince(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROVINCE, e.target.value);
    }

    const handleCountryChange = (e) => {
        setCountry(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.COUNTRY, e.target.value);
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
                            id="outlined-province" 
                            label="Province" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={ProvinceText}
                            onChange={handleProvinceChange}
                            fullWidth
                        />
                        <TextField 
                            id="outlined-country" 
                            label="Country" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={CountryText}
                            onChange={handleCountryChange}
                            fullWidth
                        /> 
                    </div>
                </div>               
            </CardContent>
        </Card>
       
    );
  });

export default AddressContactDetails;