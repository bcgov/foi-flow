import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import RequestHeader from './RequestHeader';
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

describe('FOI RequestHeader component', () => {
  
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
   
    it("FOI RequestHeader Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            requestDetails: {requestDetails: {}},
            foiRequests: {foiFullAssignedToList: []},
            user: {userDetail: {}}
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><RequestHeader requestDetails={localState.requestDetails} /></Provider>)
      });

      it('FOI RequestHeader snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            requestDetails: {requestDetails: {}, currentState: ""},
            foiRequests: {foiFullAssignedToList: [], foiMinistryAssignedToList: []},
            user: {userDetail: {}}
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123",requestState: "Call For Records"};
        }); 
        const tree = renderer.create(<Provider store={store}><RequestHeader requestDetails={localState.requestDetails} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  