import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import MinistryReview from './MinistryReview';
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

describe('FOI MinistryReview component', () => {
  
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
   
    it("FOI MinistryReview Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            foiRequests: {foiMinistryViewRequestDetail: {}},
            user: {userDetail: {}},
            requestDetails: {
                assignedTo: '',
                assignedGroup: '',
                assignedministrygroup: '',
                assignedministryperson: '',
                currentState: 'Call For Records'
            },
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {requestId: "123", ministryId: "234", requestState: "Call For Records"};
        });   
        shallow(<Provider store={store}><MinistryReview userDetail={localState.userDetail} /></Provider>)
      });

      it('FOI MinistryReview snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            foiRequests: {foiMinistryViewRequestDetail: {}},
            user: {userDetail: {}},
            requestDetails: {
                assignedTo: '',
                assignedGroup: '',
                assignedministrygroup: '',
                assignedministryperson: '',
                currentState: 'Call For Records'
            },
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {requestId: "123", ministryId: "234", requestState: "Call For Records"};
        }); 
        const tree = renderer.create(<Provider store={store}><MinistryReview userDetail={localState.userDetail} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  