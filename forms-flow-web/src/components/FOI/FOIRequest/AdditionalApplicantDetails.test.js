import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import AdditionalApplicantDetails from './AdditionalApplicantDetails';
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

describe('FOI AdditionalApplicantDetails component', () => {
  
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
   
    it("FOI AdditionalApplicantDetails Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                correctionalServiceNumber: '123',
                publicServiceEmployeeNumber: '345',
                additionalPersonalInfo: {
                    personalHealthNumber: 'HLTH123',
                    identityVerified: '',
                    birthDate: '2000-01-01'
                }
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><AdditionalApplicantDetails requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI AdditionalApplicantDetails snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                correctionalServiceNumber: '123',
                publicServiceEmployeeNumber: '345',
                additionalPersonalInfo: {
                    personalHealthNumber: 'HLTH123',
                    identityVerified: '',
                    birthDate: '2000-01-01'
                }
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><AdditionalApplicantDetails requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  