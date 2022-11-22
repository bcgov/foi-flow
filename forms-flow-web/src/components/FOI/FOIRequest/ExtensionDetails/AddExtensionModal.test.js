import React from "react";
import { Provider, useSelector } from "react-redux";
import configureStore from "redux-mock-store";
import AddExtensionModal from "./AddExtensionModal";
import { shallow, mount } from "enzyme";
import { formatDate } from "../../../../helper/FOI/helper";
import { useParams } from "react-router-dom";

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useContext: jest.fn(),
}));
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useSelector: jest.fn(),
}));
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useParams: jest.fn(),
}));

jest.mock("@material-ui/core/styles", () => {
  const Styles = jest.requireActual("@material-ui/core/styles");

  const createMuiTheme = jest.requireActual(
    "@material-ui/core/styles/createTheme"
  ).default;

  return {
    ...Styles,
    makeStyles: (func) => {
      const theme = createMuiTheme();
      return Styles.makeStyles(func.bind(null, theme));
    },
  };
});

const mockExtensionContext = (localState) =>
  jest.spyOn(React, "useContext").mockImplementation((context) => {
    // only stub the response if it is one of your Context
    if (context.displayName === "ExtensionContext") {
      return localState;
    }

    // continue to use original useContext for the rest use cases
    const ActualReact = jest.requireActual("react");
    return ActualReact.useContext(context);
  });

describe("FOI AddExtensionModal component", () => {


  const mockStore = configureStore();
  let store;

  it("FOI AddExtensionModal Rendering Unit test - render check", () => {
    store = mockStore({});
    const localState = {
      saveModalOpen: true,
      setSaveModalOpen: jest.fn(),
      extensionReasons: [
        {
          isactive: true,
          reason:
            "Public Body - Large Volume and/or Volume of Search and Consultation",
          extensiontype: "Public Body",
          defaultextendedduedays: 30,
          extensionreasonid: 5,
        },
        {
          isactive: true,
          reason: "OIPC - Applicant Consent",
          extensiontype: "OIPC",
          defaultextendedduedays: 0,
          extensionreasonid: 6,
        },
      ],
      dispatch: jest.fn(),
      startDate: "2020-12-01",
      currentDueDate: formatDate(new Date()),
      originalDueDate: formatDate(new Date()),
      idNumber: "EDU-",
      selectedExtension: {
        foirequestextensionid: 16,
        extensionreasonid: 5,
        extensionstatusid: 2,
        extendedduedays: 2,
        extendedduedate: "2022-03-02T00:00:00+00:00",
        decisiondate: "2022-01-18T00:00:00+00:00",
        approvednoofdays: 2,
      },
      extensionLoading: false,
      setExtensionLoading: jest.fn(),
      saveExtensionRequest: jest.fn(),
      errorToast: jest.fn(),
      extensions: [],
    };    

    mockExtensionContext(localState);

    useParams.mockImplementation(() => {
      return {ministryId: "123", requestId: "345"};
    }); 

    const wrapper = mount(
      <Provider store={store}>
        <AddExtensionModal />
      </Provider>
    );

    expect(
      wrapper.find("#extended-due-date div input")
      .prop("value"))
    .toBe("2022-03-02");

    expect(
      wrapper.contains(
        "Public Body - Large Volume and/or Volume of Search and Consultation"
      ))
    .toBe(true)

    expect(
      wrapper.find("#status-options")
      .exists()
    ).toBe(false);

  });

  it("FOI AddExtensionModal Rendering Unit test - render check OIPC", () => {
    store = mockStore({});
    const localState = {
      saveModalOpen: true,
      setSaveModalOpen: jest.fn(),
      extensionReasons: [
        {
          isactive: true,
          reason:
            "Public Body - Large Volume and/or Volume of Search and Consultation",
          extensiontype: "Public Body",
          defaultextendedduedays: 30,
          extensionreasonid: 5,
        },
        {
          isactive: true,
          reason: "OIPC - Applicant Consent",
          extensiontype: "OIPC",
          defaultextendedduedays: 0,
          extensionreasonid: 6,
        },
      ],
      dispatch: jest.fn(),
      startDate: "2020-12-01",
      currentDueDate: formatDate(new Date()),
      originalDueDate: formatDate(new Date()),
      idNumber: "EDU-",
      selectedExtension: {
        foirequestextensionid: 16,
        extensionreasonid: 6,
        extensionstatusid: 2,
        extendedduedays: 2,
        extendedduedate: "2022-03-02T00:00:00+00:00",
        decisiondate: "2022-01-18T00:00:00+00:00",
        approvednoofdays: 2,
      },
      extensionLoading: false,
      setExtensionLoading: jest.fn(),
      saveExtensionRequest: jest.fn(),
      errorToast: jest.fn(),
      extensions: [],
    };   

    mockExtensionContext(localState);

    useParams.mockImplementation(() => {
      return {ministryId: "123", requestId: "345"};
    }); 

    const wrapper = mount(
      <Provider store={store}>
        <AddExtensionModal />
      </Provider>
    );

    expect(
      wrapper.find("#extended-due-date div input")
      .prop("value"))
    .toBe(
      "2022-03-02"
    );

    expect(
      wrapper.contains(
        "OIPC - Applicant Consent"
      )
    ).toBe(true);

    expect(
      wrapper.find("#status-options")
      .exists())
    .toBe(true);
  });

});
