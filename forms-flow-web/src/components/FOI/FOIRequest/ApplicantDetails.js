import React from 'react';
import { useSelector } from "react-redux";
import TextField from '@material-ui/core/TextField';
import MenuItem from '@material-ui/core/MenuItem';
import Input from '@material-ui/core/Input';
import FOI_COMPONENT_CONSTANTS from '../../../constants/FOI/foiComponentConstants';
import { formatDate } from "../../../helper/FOI/helper";
import { shouldDisableFieldForMinistryRequests } from "./utils";
import { makeStyles } from '@material-ui/styles';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

const ApplicantDetails = React.memo(
  ({
    requestDetails,
    handleApplicantDetailsInitialValue,
    handleApplicantDetailsValue,
    createSaveRequestObject,
    disableInput,
    requestStatus,
    defaultExpanded,
    showHistory,
  }) => {

    const useStyles = makeStyles({
      heading: {
        color: '#FFF',
        fontSize: '16px !important',
        fontWeight: 'bold !important'
      },
      accordionSummary: {
        flexDirection: 'row-reverse'
      }
    });
    const classes = useStyles();
    const disableFieldForMinistryRequest =
      shouldDisableFieldForMinistryRequests(requestStatus);
    /**
     *  Applicant Details box in the UI
     *  FirstName, LastName and Category - Mandatory fields
     */

    //gets the category list master data
    const category = useSelector((state) => state.foiRequests.foiCategoryList);

    const validateFields = (
      data,
      name,
      options = {
        dateFormat: false,
        defaultValue: "",
      }
    ) => {
      options.defaultValue = options.defaultValue || "";

      options.defaultValue = options.defaultValue || "";

      if (!data) {
        return options.defaultValue;
      }

      if (options.dateFormat) {
        return data[name] ? formatDate(data[name]) : options.defaultValue;
      }

      if (name === "category") {
        if (category.length > 0) {
          let categoryValue = category.filter(
            (item) => item.name === data[name]
          );
          if (categoryValue.length <= 0) return options.defaultValue;
        }
      }

      return data[name] || options.defaultValue;
    };

    //state management of Applicant FirstName, MiddleName, LastName, Organization and Category
    const [applicantFirstNameText, setApplicantFirstName] = React.useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME
      )
    );
    const [applicantMiddleNameText, setApplicantMiddleName] = React.useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME
      )
    );
    const [applicantLastNameText, setApplicantLastName] = React.useState(
      validateFields(
        requestDetails,
        FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME
      )
    );
    const [organizationText, setOrganization] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.ORGANIZATION)
    );
    const [selectedCategory, setCategoryValue] = React.useState(
      validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.FOI_CATEGORY, {
        dateFormat: false,
        defaultValue: "Select Category",
      })
    );

    //handle initial value for required field validation
    React.useEffect(() => {
      setApplicantFirstName(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME
        )
      );
      setApplicantMiddleName(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME
        )
      );
      setApplicantLastName(
        validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME
        )
      );
      setOrganization(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.ORGANIZATION)
      );
      setCategoryValue(
        validateFields(requestDetails, FOI_COMPONENT_CONSTANTS.FOI_CATEGORY, {
          dateFormat: false,
          defaultValue: "Select Category",
        })
      );

      const applicantDetailsObject = {
        firstName: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME
        ),
        lastName: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME
        ),
        category: validateFields(
          requestDetails,
          FOI_COMPONENT_CONSTANTS.FOI_CATEGORY,
          {
            dateFormat: false,
            defaultValue: "Select Category",
          }
        ),
      };
      handleApplicantDetailsInitialValue(applicantDetailsObject);
    }, [requestDetails, handleApplicantDetailsInitialValue]);

    //handle onchange of firstName
    const handleFirtNameChange = (e) => {
      setApplicantFirstName(e.target.value);
      handleApplicantDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.APPLICANT_FIRST_NAME,
        e.target.value
      );
    };
    //handle onchange of middleName
    const handleMiddleNameChange = (e) => {
      setApplicantMiddleName(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.APPLICANT_MIDDLE_NAME,
        e.target.value
      );
    };
    //handle onchange of lastName
    const handleLastNameChange = (e) => {
      setApplicantLastName(e.target.value);
      handleApplicantDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.APPLICANT_LAST_NAME,
        e.target.value
      );
    };
    //handle onchange of organization
    const handleOrganizationChange = (e) => {
      setOrganization(e.target.value);
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.ORGANIZATION,
        e.target.value
      );
    };

    //handle category change
    const handleCategoryOnChange = (e) => {
      setCategoryValue(e.target.value);
      //event bubble up - send the updated category for required field validation
      handleApplicantDetailsValue(
        e.target.value,
        FOI_COMPONENT_CONSTANTS.FOI_CATEGORY
      );
      createSaveRequestObject(
        FOI_COMPONENT_CONSTANTS.FOI_CATEGORY,
        e.target.value
      );
    };

    //generate the menu items for the category
    const menuItems = category.map((item) => {
      return (
        <MenuItem
          key={item.name}
          value={item.name}
          disabled={item.name.toLowerCase().includes("select")}
        >
          {item.name}
        </MenuItem>
      );
    });

    return (
      <div className='request-accordian'>
        <Accordion defaultExpanded={defaultExpanded}>
          <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="applicantDetails-header">
            <Typography className={classes.heading}>APPLICANT DETAILS</Typography>
          </AccordionSummary>
        <AccordionDetails>
          <div>
            {showHistory && <button type="button" className={`btn btn-link btn-description-history`} onClick={showHistory}>
                Applicant Contact History
            </button>}
          </div>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="firstName"
                label="Applicant First Name"
                inputProps={{ "aria-labelledby": "firstName-label"}}
                InputLabelProps={{ shrink: true }}
                variant="outlined"
                value={applicantFirstNameText}
                fullWidth
                onChange={handleFirtNameChange}
                required={true}
                disabled={disableInput}
                error={applicantFirstNameText === ""}
              />
              <TextField
                id="middleName"
                label="Applicant Middle Name"
                inputProps={{ "aria-labelledby": "middleName-label"}}
                InputLabelProps={{ shrink: true }}
                value={applicantMiddleNameText}
                variant="outlined"
                fullWidth
                disabled={disableInput}
                onChange={handleMiddleNameChange}
              />
              <TextField
                id="lastName"
                label="Applicant Last Name"
                inputProps={{ "aria-labelledby": "lastName-label"}}
                InputLabelProps={{ shrink: true }}
                value={applicantLastNameText}
                variant="outlined"
                fullWidth
                onChange={handleLastNameChange}
                required={true}
                disabled={disableInput}
                error={applicantLastNameText === ""}
              />
            </div>
            <div className="col-lg-6 foi-details-col">
              <TextField
                id="organization"
                label="Organization"
                inputProps={{ "aria-labelledby": "organization-label"}}
                InputLabelProps={{ shrink: true }}
                value={organizationText}
                variant="outlined"
                fullWidth
                disabled={disableInput}
                onChange={handleOrganizationChange}
              />
              <TextField
                id="category"
                label="Category"
                inputProps={{ "aria-labelledby": "category-label"}}
                InputLabelProps={{ shrink: true }}
                select
                value={selectedCategory}
                onChange={handleCategoryOnChange}
                input={<Input />}
                variant="outlined"
                fullWidth
                required
                disabled={disableInput || disableFieldForMinistryRequest}
                error={selectedCategory.toLowerCase().includes("select")}
              >
                {menuItems}
              </TextField>
            </div>
          </div>
        </AccordionDetails>
      </Accordion>
      </div>
    );
  }
);

export default ApplicantDetails;