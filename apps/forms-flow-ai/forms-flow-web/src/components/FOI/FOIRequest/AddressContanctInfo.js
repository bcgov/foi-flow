import React, { useState, useEffect, memo } from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";

const useStyles = makeStyles((theme) => ({
  row: {
    marginBottom: "2em",
  },
}));

const AddressContactDetails = memo(
  ({
    requestDetails,
    contactDetailsNotGiven,
    createSaveRequestObject,
    handleContactDetailsInitialValue,
    handleContanctDetailsValue,
    handleEmailValidation,
    disableInput,
  }) => {
    const classes = useStyles();
    /**
     *  Address and Contact box in the UI
     *  No mandatory fields here
     */

    const validateFields = (
      data,
      name,
      options = {
        dateFormat: false,
        defaultValue: "",
      }
    ) => {
      options.defaultValue = options.defaultValue || "";

      if (!data) {
        return options.defaultValue;
      }

      return data[name] || options.defaultValue;
    };

    //local state management for homePhone, mobilePhone, workPhone1, workPhone2, streetAddress1, streetAddress2, city, postalcode, province and country
    const [homePhoneText, setHomePhone] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.HOME_PHONE)
    );
    const [mobilePhoneText, setMobilePhone] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.MOBILE_PHONE)
    );
    const [workPhonePrimaryText, setWorkPhonePrimary] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY)
    );
    const [workPhoneSecondaryText, setWorkPhoneSecondary] = useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY
      )
    );
    const [streetAddressText, setStreetAddress] = useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY
      )
    );
    const [secondaryStreetAddressText, setSecondaryStreetAddress] = useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY
      )
    );
    const [CityText, setCity] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY)
    );
    const [PostalText, setPostal] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE)
    );
    const [ProvinceText, setProvince] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.PROVINCE)
    );
    const [CountryText, setCountry] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.COUNTRY)
    );

    const [emailText, setEmail] = useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL)
    );

    //state management for email validation
    const [validation, setValidation] = React.useState({});
    //handle onchange of email and the validation
    const handleEmailChange = (e) => {
      var emailValidation = {};
      if (e.target.value) {
        const helperText = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e.target.value)
          ? ""
          : "Email is not valid.";
        emailValidation = { field: "Email", helperTextValue: helperText };
        setValidation(emailValidation);
      } else {
        emailValidation = { field: "Email", helperTextValue: "" };
        setValidation(emailValidation);
      }
      handleEmailValidation(emailValidation);
      setEmail(e.target.value);
      handleContanctDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL,
        e.target.value
      );
    };

    useEffect(() => {
      const contanctDetailsObject = {
        primaryAddress: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY
        ),
        city: validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY),
        province: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.POSTALCODE
        ),
        country: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.COUNTRY
        ),
        postalCode: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.POSTALCODE
        ),
      };
      handleContactDetailsInitialValue(contanctDetailsObject);
    }, [requestDetails, handleContactDetailsInitialValue]);
    const handleHomePhoneChange = (e) => {
      setHomePhone(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.HOME_PHONE,
        e.target.value
      );
    };
    const handleMobilePhoneChange = (e) => {
      setMobilePhone(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.MOBILE_PHONE,
        e.target.value
      );
    };
    const handleWorkPhonePrimaryChange = (e) => {
      setWorkPhonePrimary(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY,
        e.target.value
      );
    };
    const handleWorkPhoneSecondarChange = (e) => {
      setWorkPhoneSecondary(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY,
        e.target.value
      );
    };

    const handleStreetAddressChange = (e) => {
      setStreetAddress(e.target.value);
      handleContanctDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY,
        e.target.value
      );
    };
    const handleScondaryStreetAddressChange = (e) => {
      setSecondaryStreetAddress(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY,
        e.target.value
      );
    };
    const handleCityChange = (e) => {
      setCity(e.target.value);
      handleContanctDetailsValue(e.target.value, FOI_COMPONENT_CONSTANTS.CITY);
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.CITY, e.target.value);
    };
    const handlePostalChange = (e) => {
      setPostal(e.target.value);
      handleContanctDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.POSTALCODE
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.POSTALCODE,
        e.target.value
      );
    };

    const handleProvinceChange = (e) => {
      setProvince(e.target.value);
      handleContanctDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.PROVINCE
      );
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.PROVINCE, e.target.value);
    };

    const handleCountryChange = (e) => {
      setCountry(e.target.value);
      handleContanctDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.COUNTRY
      );
      createSaveRequestObject(FOI_COMPONENT_CONSTANTS.COUNTRY, e.target.value);
    };

    return (
      <Card className="foi-details-card">
        <label className="foi-details-label">
          ADDRESS AND CONTACT INFORMATION
        </label>
        <CardContent>
          <div className={clsx("row", "foi-details-row", classes.row)}>
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="email"
                label="Email"
                InputLabelProps={{ shrink: true }}
                value={emailText}
                variant="outlined"
                fullWidth
                required={true}
                disabled={disableInput}
                onChange={handleEmailChange}
                error={
                  (validation.helperTextValue !== undefined &&
                    validation.helperTextValue !== "") ||
                  (emailText == "" && contactDetailsNotGiven)
                }
                helperText={validation.helperTextValue}
              />
            </div>
          </div>

          <div className={clsx("row", "foi-details-row", classes.row)}>
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-homePhone"
                label="Home Phone"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={homePhoneText}
                onChange={handleHomePhoneChange}
                fullWidth
                disabled={disableInput}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-mobilePhone"
                label="Mobile Phone"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={mobilePhoneText}
                onChange={handleMobilePhoneChange}
                fullWidth
                disabled={disableInput}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-workPhone1"
                label="Work Phone"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={workPhonePrimaryText}
                onChange={handleWorkPhonePrimaryChange}
                fullWidth
                disabled={disableInput}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-workPhone2"
                label="Alternative Phone"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={workPhoneSecondaryText}
                onChange={handleWorkPhoneSecondarChange}
                fullWidth
                disabled={disableInput}
              />
            </div>
          </div>

          <div className={clsx("row", "foi-details-row", classes.row)}>
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-streetAddress"
                label="Street Address"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={streetAddressText}
                onChange={handleStreetAddressChange}
                fullWidth
                required={true}
                disabled={disableInput}
                error={streetAddressText === "" && contactDetailsNotGiven}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-scondaryStreetAddress"
                label="Secondary Street Address"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={secondaryStreetAddressText}
                onChange={handleScondaryStreetAddressChange}
                fullWidth
                disabled={disableInput}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-city"
                label="City"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={CityText}
                onChange={handleCityChange}
                fullWidth
                required={true}
                disabled={disableInput}
                error={CityText === "" && contactDetailsNotGiven}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-province"
                label="Province"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={ProvinceText}
                onChange={handleProvinceChange}
                fullWidth
                required={true}
                disabled={disableInput}
                error={ProvinceText === "" && contactDetailsNotGiven}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-country"
                label="Country"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={CountryText}
                onChange={handleCountryChange}
                fullWidth
                required={true}
                disabled={disableInput}
                error={CountryText === "" && contactDetailsNotGiven}
              />
            </div>

            <div className="col-lg-6 foi-details-col">
              <TextField
                id="outlined-postalCode"
                label="Postal Code"
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={PostalText}
                onChange={handlePostalChange}
                inputProps={{ maxLength: 6 }}
                fullWidth
                required={true}
                disabled={disableInput}
                error={PostalText === "" && contactDetailsNotGiven}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
);

export default AddressContactDetails;
