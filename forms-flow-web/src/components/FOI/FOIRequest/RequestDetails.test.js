import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import RequestDetails from './RequestDetails';
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

describe('FOI RequestDetails component', () => {
  
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
   
    it("FOI RequestDetails Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {                       
            createSaveRequestObject:  jest.fn(),
            handleRequestDetailsValue:  jest.fn(), 
            handleRequestDetailsInitialValue:  jest.fn(),
            requestDetails: {
                requestType: 'general',
                receivedMode: 'Online Form',
                deliveryMode: 'Secure File Transfer',
                sourceOfSubmission: 'onlineform',
                requestProcessStart: '2021-08-02',
                receivedDateUF: '2021-09-22 21:01:35.902089',
                dueDate: '2021-09-15'
            },
            foiRequests: { 
                foiRequestTypeList: [],
                foiReceivedModeList: [],
                foiDeliveryModeList: []
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><RequestDetails requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} handleRequestDetailsValue={localState.handleRequestDetailsValue} handleRequestDetailsInitialValue={localState.handleRequestDetailsInitialValue} /></Provider>)
      });

      it('FOI RequestDetails snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            createSaveRequestObject:  jest.fn(),
            handleRequestDetailsValue:  jest.fn(), 
            handleRequestDetailsInitialValue:  jest.fn(),
            requestDetails: {
                requestType: 'general',
                receivedMode: 'Online Form',
                deliveryMode: 'Secure File Transfer',
                sourceOfSubmission: 'onlineform',
                requestProcessStart: '2021-08-02',
                receivedDateUF: '2021-09-22 21:01:35.902089',
                dueDate: '2021-09-15'
            },
            foiRequests: { 
                foiRequestTypeList: [],
                foiReceivedModeList: [],
                foiDeliveryModeList: []
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><RequestDetails requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} handleRequestDetailsValue={localState.handleRequestDetailsValue} handleRequestDetailsInitialValue={localState.handleRequestDetailsInitialValue} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  