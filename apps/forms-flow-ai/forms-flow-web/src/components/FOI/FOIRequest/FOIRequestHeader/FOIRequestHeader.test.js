import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import FOIRequestHeader from '.';
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

describe('FOI FOIRequestHeader component', () => {
  
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
   
    it("FOI FOIRequestHeader Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            headerValue: '',                  
            createSaveRequestObject:  jest.fn(),
            handleAssignedToInitialValue:  jest.fn(), 
            handleAssignedToValue:  jest.fn(),
            handlestatusudpate:  jest.fn(),
            requestDetails: {
                currentState: 'Open',                
                dueDate: '2021-09-15'
            },
            foiRequests: { 
                foiAssignedToList: []
            },
            user: {"userDetail": {}}
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><FOIRequestHeader handlestatusudpate={localState.handlestatusudpate} handleAssignedToValue={localState.handleAssignedToValue} handleAssignedToInitialValue={localState.handleAssignedToInitialValue} headerValue={localState.headerValue} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI FOIRequestHeader snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            headerValue: '',                  
            createSaveRequestObject:  jest.fn(),
            handleAssignedToInitialValue:  jest.fn(), 
            handleAssignedToValue:  jest.fn(),
            handlestatusudpate:  jest.fn(),
            requestDetails: {
                currentState: 'Open',                
                dueDate: '2021-09-15'
            },
            foiRequests: { 
                foiAssignedToList: []
            },
            user: {"userDetail": {}}
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><FOIRequestHeader handlestatusudpate={localState.handlestatusudpate} handleAssignedToValue={localState.handleAssignedToValue} handleAssignedToInitialValue={localState.handleAssignedToInitialValue} headerValue={localState.headerValue} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  