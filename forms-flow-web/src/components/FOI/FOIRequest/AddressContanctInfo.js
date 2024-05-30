import React, { memo } from "react";
import TextField from "@material-ui/core/TextField";
import FOI_COMPONENT_CONSTANTS from "../../../constants/FOI/foiComponentConstants";
import { makeStyles } from "@material-ui/core/styles";
import * as EmailValidator from "email-validator";
import clsx from "clsx";
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { isBeforeOpen } from "./utils";

const useStyles = makeStyles((_theme) => ({
  row: {
    marginBottom: "2em",
  },
  heading: {
    color: '#FFF',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  },
  accordionSummary: {
      flexDirection: 'row-reverse'
  },
  warning: {
    '& fieldset': {
      borderColor: '#ed6c02 !important'
    },
    '& label': {
      color: '#ed6c02 !important'
    }
  
  }
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
    defaultExpanded,
    moreInfoAction,
    warning
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

    //local state management for email, homePhone, mobilePhone, workPhone1, workPhone2, streetAddress1, streetAddress2, city, postalcode, province and country
    const [homePhoneText, setHomePhone] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.HOME_PHONE)
    );
    const [mobilePhoneText, setMobilePhone] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.MOBILE_PHONE)
    );
    const [workPhonePrimaryText, setWorkPhonePrimary] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY)
    );
    const [workPhoneSecondaryText, setWorkPhoneSecondary] = React.useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY
      )
    );
    const [streetAddressText, setStreetAddress] = React.useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY
      )
    );
    const [secondaryStreetAddressText, setSecondaryStreetAddress] =
      React.useState(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY
        )
      );
    const [CityText, setCity] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY)
    );
    const [PostalText, setPostal] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE)
    );
    const [ProvinceText, setProvince] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.PROVINCE)
    );
    const [CountryText, setCountry] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.COUNTRY)
    );
    const [emailText, setEmail] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL)
    );

    //state management for email validation
    const [validation, setValidation] = React.useState({});

  //   const [modalOpen, setModalOpen] = React.useState(false);

    
  //   const handleModalClose = () => {
  //     setModalOpen(false);
  // }

    React.useEffect(() => {
      setFieldValues();
      const contanctDetailsObject = {
        address: validateFields(
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
        postal: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.POSTALCODE
        ),
        email: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL
        ),
      };
      handleContactDetailsInitialValue(contanctDetailsObject);
    }, [requestDetails, handleContactDetailsInitialValue]);

    const setFieldValues = () => {
      setHomePhone(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.HOME_PHONE)
      );
      setMobilePhone(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.MOBILE_PHONE)
      );
      setWorkPhonePrimary(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY
        )
      );
      setWorkPhoneSecondary(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY
        )
      );
      setStreetAddress(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY
        )
      );
      setSecondaryStreetAddress(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY
        )
      );
      setCity(validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.CITY));
      setPostal(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.POSTALCODE)
      );
      setProvince(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.PROVINCE)
      );
      setCountry(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.COUNTRY)
      );
      setEmail(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL)
      );
    };

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

    //handle onchange of email and the validation
    const handleEmailChange = (e) => {
      let emailValidation = {};
      if (e.target.value) {
        const helperText = EmailValidator.validate(e.target.value)
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
    return (
      <div className='request-accordian' id="addressContactInfo">
      <Accordion defaultExpanded={defaultExpanded}>
      <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} 
          id="addressContactInfo-header">
          <Typography className={classes.heading}>ADDRESS AND CONTACT INFORMATION</Typography>
      </AccordionSummary>
      <AccordionDetails>        
          <div>
              {/* {moreInfoAction && // comment back in after axis decommission
                <button
                  type="button"
                  className={`btn btn-link btn-description-history`}
                  onClick={moreInfoAction}
                  style={(isBeforeOpen(requestDetails) && !requestDetails.foiRequestApplicantID) ? {color: "#9E2929"} : {}}
                >
                  {(isBeforeOpen(requestDetails)) && 'Search' } Applicant Profiles
                </button>
              } */}
          </div>
          <div className={clsx("row", "foi-details-row", classes.row)}>
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="email"
                label="Email"
                InputLabelProps={{ shrink: true }}
                value={emailText}
                variant="outlined"
                className={warning && warning(FOI_COMPONENT_CONSTANTS.APPLICANT_EMAIL) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.HOME_PHONE) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.MOBILE_PHONE) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.WORK_PHONE_PRIMARY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.WORK_PHONE_SECONDARY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_PRIMARY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.STREET_ADDRESS_SECONDARY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.CITY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.PROVINCE) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.COUNTRY) && classes.warning}
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
                className={warning && warning(FOI_COMPONENT_CONSTANTS.POSTALCODE) && classes.warning}
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
          </AccordionDetails>
    </Accordion>
  </div>
    );
  }
);

export default AddressContactDetails;
