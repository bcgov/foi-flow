import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import FOIRequest from './FOIRequest';
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

describe('FOI FOIRequest component', () => {
  
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
   
    it("FOI FOIRequest Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            requestDetails: {
                assignedTo: '',
                assignedGroup: '',
                currentState: 'Open'
            },
            foiRequests: { 
                foiRequestDetail: {}
            },
            user: {"userDetail": {}}        
        }        
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123", requestId: "234"};
        });   
        shallow(<Provider store={store}><FOIRequest /></Provider>)
      });

      it('FOI FOIRequest snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            requestDetails: {
                assignedTo: '',
                assignedGroup: '',
                currentState: 'Open'
            },
            foiRequests: { 
                foiRequestDetail: {}
            },
            user: {"userDetail": {}}
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123", requestId: "345"};
        }); 
        const tree = renderer.create(<Provider store={store}><FOIRequest /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  