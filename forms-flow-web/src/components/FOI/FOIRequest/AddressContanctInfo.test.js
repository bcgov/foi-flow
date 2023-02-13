import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import AddressContanctInfo from './AddressContanctInfo';
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

describe('FOI AddressContanctInfo component', () => {
  
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
   
    it("FOI AddressContanctInfo Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = { 
            contactDetailsNotGiven: false,   
            handleContactDetailsInitialValue:  jest.fn(), 
            handleContanctDetailsValue:  jest.fn(),            
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                phonePrimary: '1234567890',
                phoneSecondary: '',
                workPhonePrimary: '',
                workPhoneSecondary: '',
                address: '123 Main Street',
                addressSecondary: '',
                city: 'Toronto',
                postal: 'Q1E3A2',
                province: 'Ontario',
                country: 'Canada',
                
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><AddressContanctInfo requestDetails={localState.requestDetails} contactDetailsNotGiven={localState.contactDetailsNotGiven} handleContactDetailsInitialValue={localState.handleContactDetailsInitialValue} handleContanctDetailsValue={localState.handleContanctDetailsValue} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI AddressContanctInfo snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            contactDetailsNotGiven: false,   
            handleContactDetailsInitialValue:  jest.fn(), 
            handleContanctDetailsValue:  jest.fn(),            
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                phonePrimary: '1234567890',
                phoneSecondary: '',
                workPhonePrimary: '',
                workPhoneSecondary: '',
                address: '123 Main Street',
                addressSecondary: '',
                city: 'Toronto',
                postal: 'Q1E3A2',
                province: 'Ontario',
                country: 'Canada',
            },
            userDetail: {
                groups: ['/Flex Team', '/Intake Team']
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><AddressContanctInfo requestDetails={localState.requestDetails} contactDetailsNotGiven={localState.contactDetailsNotGiven} handleContactDetailsInitialValue={localState.handleContactDetailsInitialValue} handleContanctDetailsValue={localState.handleContanctDetailsValue} createSaveRequestObject={localState.createSaveRequestObject}/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  