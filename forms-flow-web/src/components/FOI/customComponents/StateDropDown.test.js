import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import StateDropDown from './StateDropDown';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';
import Router, { useParams } from "react-router-dom";

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

jest.mock("react-router-dom", () => ({
    ...jest.requireActual("react-router-dom"),
    useParams: jest.fn(),
}));

describe('FOI StateDropDown component', () => {
  
    beforeEach(() => {
        useSelector.mockImplementation(callback => {
          return callback(mockAppState);
        });
        useParams.mockImplementation(() => {
          return mockAppState;
        });
      });
      afterEach(() => {
        useSelector.mockClear();
        useParams.mockClear();
      });

    const initialState = {output:10}
    const mockStore = configureStore()
    let store,wrapper
   
    it("FOI StateDropDown Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            requestStatus: 'Open',
            handleStateChange:  jest.fn(),
            requestDetail: {
              selectedMinistries: ["AEST"]
            },
            user: {"userDetail": {}},
            isValidationError: false,
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
          useParams.mockImplementation(() => {
            return {requestState: "Open"};
        }); 
        shallow(<Provider store={store}><StateDropDown requestStatus={localState.requestStatus} handleStateChange={localState.handleStateChange} requestDetail={localState.requestDetail} isValidationError={localState.isValidationError} /></Provider>)
      });

      it('FOI StateDropDown snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            requestStatus: 'Open',
            handleStateChange:  jest.fn(),
            requestDetail: {
              selectedMinistries: ["AEST"]
            },
            user: {"userDetail": {}},
            foiRequests: { foiRequestCFRForm: { feedata:{}, status: "" } }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
          useParams.mockImplementation(() => {
            return {requestState: "Open"};
        });
        const tree = renderer.create(<Provider store={store}><StateDropDown requestStatus={localState.requestStatus} handleStateChange={localState.handleStateChange} requestDetail={localState.requestDetail} isValidationError={localState.isValidationError} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  