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
    
    const provinceText = !!requestDetails.province ? requestDetails.province : "Select Province";
    const countryText = !!requestDetails.country ? requestDetails.country : "Select Country";

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
                            value={homePhoneText}
                            onChange={handleHomePhoneChange}
                        />
                        <TextField 
                            id="outlined-mobilePhone" 
                            label="Mobile Phone" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={mobilePhoneText}
                            onChange={handleMobilePhoneChange}
                        />
                        <TextField 
                            id="outlined-streetAddress" 
                            label="Street Address" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={streetAddressText}
                            onChange={handleStreetAddressChange}
                        />
                        <TextField 
                            id="outlined-city" 
                            label="City" 
                            InputLabelProps={{ shrink: true, }}                             
                            variant="outlined" 
                            value={CityText}
                            onChange={handleCityChange}
                        />
                        <TextField 
                            id="outlined-postalCode" 
                            label="Postal Code" 
                            InputLabelProps={{ shrink: true, }}                         
                            variant="outlined" 
                            value={PostalText}
                            onChange={handlePostalChange}
                        />                                                
                    </div>
                    <div className="col-lg-6 foi-address-details-col">                       
                    <TextField 
                            id="outlined-workPhone1" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }} 
                            variant="outlined" 
                           value={workPhonePrimaryText}
                           onChange={handleWorkPhonePrimaryChange}
                        />
                        <TextField 
                            id="outlined-workPhone2" 
                            label="Work Phone" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={workPhoneSecondaryText}
                            onChange={handleWorkPhoneSecondarChange}
                        />
                        <TextField 
                            id="outlined-scondaryStreetAddress" 
                            label="Secondary Street Address" 
                            InputLabelProps={{ shrink: true, }}                            
                            variant="outlined" 
                            value={secondaryStreetAddressText}
                            onChange={handleScondaryStreetAddressChange}
                        />                        
                         <SelectWithLegend selectData = {provinceList} legend="Province" selectDefault={provinceText} required={false}/>
                         <SelectWithLegend selectData = {countryList} legend="Country" selectDefault={countryText} required={false}/>
                    </div>
                </div> 
                </form>             
            </CardContent>
        </Card>
       
    );
  });

export default AddressContactDetails;