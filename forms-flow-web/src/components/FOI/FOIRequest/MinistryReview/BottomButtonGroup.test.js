import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import BottomButtonGroup from './BottomButtonGroup';
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

describe('FOI BottomButtonGroup component', () => {
  
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
    let store;    
   
    it("FOI BottomButtonGroup Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            isValidationError: false, 
            saveMinistryRequestObject: {}, 
            unSavedRequest: false,
            handleSaveRequest: jest.fn(),
            currentSelectedStatus: "Call For Records",
            hasStatusRequestSaved: false           
        }        
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123", requestId: "234", requestState: "Call For Records"};
        });   
        shallow(<Provider store={store}><BottomButtonGroup isValidationError={localState.isValidationError} saveMinistryRequestObject={localState.saveMinistryRequestObject} unSavedRequest={localState.unSavedRequest} handleSaveRequest={localState.handleSaveRequest} currentSelectedStatus={localState.currentSelectedStatus} hasStatusRequestSaved={localState.hasStatusRequestSaved} /></Provider>)
      });

      it('FOI BottomButtonGroup snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            isValidationError: false, 
            saveMinistryRequestObject: {}, 
            unSavedRequest: false,
            handleSaveRequest: jest.fn(),
            currentSelectedStatus: "Call For Records",
            hasStatusRequestSaved: false  
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123", requestId: "345", requestState: "Call For Records"};
        }); 
        const tree = renderer.create(<Provider store={store}><BottomButtonGroup isValidationError={localState.isValidationError} saveMinistryRequestObject={localState.saveMinistryRequestObject} unSavedRequest={localState.unSavedRequest} handleSaveRequest={localState.handleSaveRequest} currentSelectedStatus={localState.currentSelectedStatus} hasStatusRequestSaved={localState.hasStatusRequestSaved} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  