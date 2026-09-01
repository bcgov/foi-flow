import React from "react";
import renderer from "react-test-renderer";

/*
 * These tests verify FOIMOD-4734 layout/composition rather than
 * Material UI's browser-specific rendering behaviour.
 *
 * react-test-renderer does not provide actual DOM Elements, while
 * MUI TextareaAutosize and Fade expect them during lifecycle hooks.
 */

jest.mock("@material-ui/core/TextField", () => {
  const React = require("react");

  return function MockTextField({ children, ...props }) {
    return React.createElement(
      "mock-text-field",
      props,
      children
    );
  };
});

jest.mock("@material-ui/core/Accordion", () => {
  const React = require("react");

  return function MockAccordion({ children, ...props }) {
    return React.createElement(
      "mock-accordion",
      props,
      children
    );
  };
});

jest.mock("@material-ui/core/AccordionSummary", () => {
  const React = require("react");

  return function MockAccordionSummary({ children, ...props }) {
    return React.createElement(
      "mock-accordion-summary",
      props,
      children
    );
  };
});

jest.mock("@material-ui/core/AccordionDetails", () => {
  const React = require("react");

  return function MockAccordionDetails({ children, ...props }) {
    return React.createElement(
      "mock-accordion-details",
      props,
      children
    );
  };
});

jest.mock("@material-ui/core/Typography", () => {
  const React = require("react");

  return function MockTypography({ children, ...props }) {
    return React.createElement(
      "mock-typography",
      props,
      children
    );
  };
});

jest.mock("@material-ui/icons/ExpandMore", () => {
  const React = require("react");

  return function MockExpandMoreIcon(props) {
    return React.createElement(
      "mock-expand-more-icon",
      props
    );
  };
});

jest.mock("@material-ui/core/Card", () => {
  const React = require("react");

  return function MockCard({ children, ...props }) {
    return React.createElement(
      "mock-card",
      props,
      children
    );
  };
});

jest.mock("@material-ui/core/CardContent", () => {
  const React = require("react");

  return function MockCardContent({ children, ...props }) {
    return React.createElement(
      "mock-card-content",
      props,
      children
    );
  };
});

jest.mock("@mui/material", () => {
  const React = require("react");

  return {
    Box: function MockBox({ children, ...props }) {
      return React.createElement(
        "mock-box",
        props,
        children
      );
    },

    Fade: function MockFade({ children, ...props }) {
      return React.createElement(
        "mock-fade",
        props,
        children
      );
    }
  };
});

jest.mock("@material-ui/styles", () => ({
  makeStyles: () => () => ({
    heading: "heading",
    accordionSummary: "accordionSummary",
    warning: "warning"
  })
}));

jest.mock("@material-ui/core/styles", () => ({
  makeStyles: () => () => ({
    rowMargin: "rowMargin"
  })
}));

import AdditionalApplicantDetails from "./AdditionalApplicantDetails";
import MinistryApplicantDetails from "./MinistryReview/ApplicantDetails";

describe("FOIMOD-4734 applicant details consolidation", () => {
  const personalRequestDetails = {
    firstName: "Sally",
    middleName: "M",
    lastName: "Smith",
    category: "Individual",
    requestType: "personal",
    correctionalServiceNumber: "CORR-123",
    publicServiceEmployeeNumber: "EMP-456",
    identityVerified: "Verified",
    additionalPersonalInfo: {
      alsoKnownAs: "Sam",
      birthDate: "2000-01-01",
      personalHealthNumber: "PHN-789"
    }
  };

  const createSaveRequestObject = jest.fn();
  const setError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const getTextFieldLabels = (component) => {
    return component.root
      .findAll((node) => node.type === "mock-text-field")
      .map((node) => node.props.label);
  };

  it("renders the Request-tab fields inline in the required order", () => {
    const component = renderer.create(
      <AdditionalApplicantDetails
        requestDetails={personalRequestDetails}
        createSaveRequestObject={createSaveRequestObject}
        disableInput={true}
        setError={setError}
        embedded={true}
        leftApplicantFields={
          <>
            <span>Applicant First Name</span>
            <span>Applicant Middle Name</span>
            <span>Applicant Last Name</span>
          </>
        }
        rightApplicantFields={
          <>
            <span>Organization</span>
            <span>Category</span>
          </>
        }
      />
    );

    expect(
      component.root.findAllByProps({
        id: "additionalApplicantDetails-header"
      })
    ).toHaveLength(0);

    expect(getTextFieldLabels(component)).toEqual([
      "Also Known As",
      "Date of Birth",
      "Identity Verified",
      "Corrections Number",
      "Employee Number",
      "Personal Health Number"
    ]);

    const rendered = JSON.stringify(component.toJSON());

    expect(rendered).toContain("Applicant First Name");
    expect(rendered).toContain("Applicant Middle Name");
    expect(rendered).toContain("Applicant Last Name");
    expect(rendered).toContain("Organization");
    expect(rendered).toContain("Category");
  });

  it("preserves the standalone Additional Applicant Details accordion", () => {
    const component = renderer.create(
      <AdditionalApplicantDetails
        requestDetails={personalRequestDetails}
        createSaveRequestObject={createSaveRequestObject}
        disableInput={true}
        setError={setError}
        defaultExpanded={true}
      />
    );

    expect(
      component.root.findAllByProps({
        id: "additionalApplicantDetails-header"
      }).length
    ).toBeGreaterThan(0);

    /*
     * Preserve the existing Applicant Profile ordering.
     */
    expect(getTextFieldLabels(component)).toEqual([
      "Personal Health Number",
      "Date of Birth",
      "Identity Verified",
      "Corrections Number",
      "Employee Number",
      "Also Known As"
    ]);

    expect(
      component.root.findAll(
        (node) =>
          node.type === "mock-typography" &&
          node.props.children === "ADDITIONAL APPLICANT DETAILS"
      )
    ).toHaveLength(1);
  });

  it("renders consolidated personal fields in the Ministry Applicant Details card", () => {
    const component = renderer.create(
      <MinistryApplicantDetails
        requestDetails={personalRequestDetails}
      />
    );

    const rendered = JSON.stringify(component.toJSON());

    expect(rendered).toContain("Applicant Details");

    expect(rendered).toContain("First Name");
    expect(rendered).toContain("Middle Name");
    expect(rendered).toContain("Last Name");

    expect(rendered).toContain("Also Known As");
    expect(rendered).toContain("Sam");

    expect(rendered).toContain("Date of Birth");

    expect(rendered).toContain("Corrections Number");
    expect(rendered).toContain("CORR-123");

    expect(rendered).toContain("Employee Number");
    expect(rendered).toContain("EMP-456");

    expect(rendered).toContain("Personal Health Number");
    expect(rendered).toContain("PHN-789");

    expect(rendered).toContain("Identity Verified");
    expect(rendered).toContain("Verified");

    expect(rendered).not.toContain(
      "ADDITIONAL APPLICANT DETAILS"
    );
  });
});