import React from "react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import ExtensionsTable from "./ExtensionsTable";
import { shallow, mount } from "enzyme";
import { formatDate } from "../../../../helper/FOI/helper";

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useContext: jest.fn(),
}));
jest.mock("react-redux", () => ({
  ...jest.requireActual("react-redux"),
  useSelector: jest.fn(),
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

describe("FOI ExtensionsTable component", () => {
  const mockStore = configureStore();
  let store;

  it("FOI ExtensionsTable Rendering Unit test - render check extensions table", () => {
    store = mockStore({});
    const localState = {
      extensions: [
        {
          foirequestextensionid: 77,
          extensionreasonid: 10,
          extensionreson:
            "OIPC - Large Volume and/or Volume of Search and Consultation",
          extensiontype: "OIPC",
          extensionstatusid: 1,
          extensionstatus: "Pending",
          extendedduedays: 10,
          extendedduedate: "2023-03-06",
          decisiondate: null,
          approvednoofdays: null,
          created_at: "2022-01-1311: 08: 01.499067",
          createdby: "foisuper@idir",
        },
        {
          foirequestextensionid: 78,
          extensionreasonid: 5,
          extensionreson:
            "Public Body - Large Volume and/or Volume of Search and Consultation",
          extensiontype: "Public Body",
          extensionstatusid: 2,
          extensionstatus: "Approved",
          extendedduedays: 20,
          extendedduedate: "2023-02-17",
          decisiondate: null,
          approvednoofdays: null,
          created_at: "2022-01-13 11:07:35.551871",
          createdby: "foisuper@idir",
        },
        {
          foirequestextensionid: 79,
          extensionreasonid: 6,
          extensionreson: "OIPC - Applicant Consent",
          extensiontype: "OIPC",
          extensionstatusid: 1,
          extensionstatus: "Pending",
          extendedduedays: 5,
          extendedduedate: "2023-01-27",
          decisiondate: null,
          approvednoofdays: null,
          created_at: "2022-01-12 19:39:37.423485",
          createdby: "foisuper@idir",
        },
      ],
      setSaveModalOpen: jest.fn(),
      setDeleteModalOpen: jest.fn(),
      setExtensionId: jest.fn(),
    };

    mockExtensionContext(localState);

    const wrapper = mount(
      <Provider store={store}>
        <ExtensionsTable />
      </Provider>
    );

    const rows = wrapper
    .find("tr")
    //remove title row
    .slice(1);

    expect(rows).toHaveLength(3);
    expect(rows.at(0).find("tr td button").prop("disabled")).toBeFalsy();
    expect(rows.at(1).find("tr td button").prop("disabled")).toBeTruthy();
    expect(rows.at(2).find("tr td button").prop("disabled")).toBeTruthy();

    const dates = rows
      .map((row) => row.childAt(2).text())
      .map((date) => new Date(date).getTime());

    //expect date at first row to be the maximum i.e. expect rows are sorted by extended date DESC
    expect(Math.max(...dates)).toBe(dates[0]);
  });
});
