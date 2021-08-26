import React from 'react';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import TextField from '@material-ui/core/TextField';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';

const AddressContactDetails = React.memo(({
  requestDetails,
  contactDetailsNotGiven,
  createSaveRequestObject, 
  handleContactDetailsInitialValue, 
  handleContanctDetailsValue
}) => {

    /**
     *  Address and Contact box in the UI
     *  No mandatory fields here
     */ 
    
    
    const validateFields = (request, name) => {
        if (request !== undefined) {
          if (name === FOI_COMPONENT_CONSTANTS.HOME_PHONE) {
            return !!request.phonePrimary ? request.phonePrimary : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.MOBILE_PHONE) {
            return !!request.phoneSecondary ? request.phoneSecondary : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY) {
            return !!request.workPhonePrimary ? request.workPhonePrimary : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY) {
            return !!request.workPhoneSecondary ? request.workPhoneSecondary : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) {
            return !!request.address ? request.address : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY) {
            return !!request.addressSecondary ? request.addressSecondary : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.CITY) {
            return !!request.city ? request.city : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.POSTALCODE) {
            return !!request.postal ? request.postal : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.PROVINCE) {
            return !!request.province ? request.province : "";
          }
          else if (name === FOI_COMPONENT_CONSTANTS.COUNTRY) {
            return !!request.country ? request.country : "";
          }
        }
        else {
          return "";
        }
    }
    
    //local state management for homePhone, mobilePhone, workPhone1, workPhone2, streetAddress1, streetAddress2, city, postalcode, province and country
    const [homePhoneText, setHomePhone] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.HOME_PHONE));
    const [mobilePhoneText, setMobilePhone] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.MOBILE_PHONE));
    const [workPhonePrimaryText, setWorkPhonePrimary] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY));
    const [workPhoneSecondaryText, setWorkPhoneSecondary] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY));
    const [streetAddressText, setStreetAddress] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY));
    const [secondaryStreetAddressText, setSecondaryStreetAddress] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY));
    const [CityText, setCity] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY));
    const [PostalText, setPostal] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE));
    const [ProvinceText, setProvince] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.PROVINCE));
    const [CountryText, setCountry] = React.useState(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.COUNTRY)); 
    React.useEffect(() => {
      const contanctDetailsObject = {
          primaryAddress: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY),
          city: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY),
          province: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE),
          country: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.COUNTRY),
          postalCode: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE),
        }
        handleContactDetailsInitialValue(contanctDetailsObject);
    },[requestDetails, handleContactDetailsInitialValue])
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
        handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY, e.target.value);
    }
    const handleScondaryStreetAddressChange = (e) => {
        setSecondaryStreetAddress(e.target.value);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY, e.target.value);
    }
    const handleCityChange = (e) => {
        setCity(e.target.value);
        handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.CITY);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CITY, e.target.value);
    }
    const handlePostalChange = (e) => {
        setPostal(e.target.value);
        handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.POSTALCODE);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.POSTALCODE, e.target.value);
    }

    const handleProvinceChange = (e) => {
        setProvince(e.target.value);
        handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.PROVINCE);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROVINCE, e.target.value);
    }

    const handleCountryChange = (e) => {
        setCountry(e.target.value);
        handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.COUNTRY);
        createSaveRequestObject(FOI_COMPONENT_CONSTANTS.COUNTRY, e.target.value);
    }

     return (
        
        <Card className="foi-details-card">            
            <label className="foi-details-label">ADDRESS AND CONTACT INFORMATION</label>
            <CardContent>         
                <div className="row foi-details-row">
                    <div className="col-lg-6 foi-details-col">
                        <TextField 
                            id="outlined-streetAddress" 
                            label="Street Address" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={streetAddressText}
                            onChange={handleStreetAddressChange}
                            fullWidth
                            required={true}
                            error={streetAddressText === "" && contactDetailsNotGiven}
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
                            id="outlined-city" 
                            label="City" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={CityText}
                            onChange={handleCityChange}
                            fullWidth
                            required={true}
                            error={CityText === "" && contactDetailsNotGiven}
                        />
                        <TextField 
                            id="outlined-province" 
                            label="Province" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={ProvinceText}
                            onChange={handleProvinceChange}
                            fullWidth
                            required={true}
                            error={ProvinceText === "" && contactDetailsNotGiven}
                        />
                        <TextField 
                            id="outlined-country" 
                            label="Country" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={CountryText}
                            onChange={handleCountryChange}
                            fullWidth
                            required={true}
                            error={CountryText === "" && contactDetailsNotGiven}
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
                            required={true}
                            error={PostalText === "" && contactDetailsNotGiven}
                        />                                     
                    </div>
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
                        
                    </div>
                </div>               
            </CardContent>
        </Card>
       
    );
  });

export default AddressContactDetails;