import React from "react";
import { Provider } from "react-redux";
import configureStore from "redux-mock-store";
import DeleteExtensionModal from "./DeleteExtensionModal";
import { mount } from "enzyme";
import Router, { useParams } from "react-router-dom";

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

describe("FOI DeleteExtensionModal component", () => {
  
    beforeEach(() => {
      useParams.mockImplementation(() => {
        return {
            requestId: 1,
            ministryId: 1
        };
      });
    });
    afterEach(() => {
      useParams.mockClear();
    });

  const mockStore = configureStore();
  let store;

  it("FOI DeleteExtensionModal Rendering Unit test - render check", () => {
    store = mockStore({});
    const localState = {
      deleteModalOpen: true,
      setDeleteModalOpen: jest.fn(),
      extensionId: 1,
      setExtensionId: jest.fn(),
      dispatch: jest.fn(),
    };

    mockExtensionContext(localState);

    const wrapper = mount(
      <Provider store={store}>
        <DeleteExtensionModal/>
      </Provider>
    );

    expect(wrapper.find("#delete-extension-dialog").exists()).toBe(true);
    
  });
});
