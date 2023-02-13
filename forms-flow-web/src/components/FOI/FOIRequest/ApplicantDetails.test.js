import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import ApplicantDetails from './ApplicantDetails';
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

describe('FOI ApplicantDetails component', () => {
  
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
   
    it("FOI ApplicantDetails Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            contactDetailsNotGiven: false,  
            handleEmailValidation:  jest.fn(),                      
            createSaveRequestObject:  jest.fn(),
            handleApplicantDetailsValue:  jest.fn(), 
            handleApplicantDetailsInitialValue:  jest.fn(),
            requestDetails: {
                firstName: 'Sally',
                middleName: 'M',
                lastName: 'Smith',
                businessName: '',
                email: 'sally@email.com',
                category: 'Individual'
            },
            foiRequests: { 
                foiCategoryList: []
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><ApplicantDetails handleEmailValidation={localState.handleEmailValidation} contactDetailsNotGiven={localState.contactDetailsNotGiven} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} handleApplicantDetailsValue={localState.handleApplicantDetailsValue} handleApplicantDetailsInitialValue={localState.handleApplicantDetailsInitialValue} /></Provider>)
      });

      it('FOI ApplicantDetails snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            contactDetailsNotGiven: false,  
            handleEmailValidation:  jest.fn(),                      
            createSaveRequestObject:  jest.fn(),
            handleApplicantDetailsValue:  jest.fn(), 
            handleApplicantDetailsInitialValue:  jest.fn(),
            requestDetails: {
                firstName: 'Sally',
                middleName: 'M',
                lastName: 'Smith',
                businessName: '',
                email: 'sally@email.com',
                category: 'Individual'
            },
            foiRequests: { 
                foiCategoryList: []
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><ApplicantDetails handleEmailValidation={localState.handleEmailValidation} contactDetailsNotGiven={localState.contactDetailsNotGiven} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} handleApplicantDetailsValue={localState.handleApplicantDetailsValue} handleApplicantDetailsInitialValue={localState.handleApplicantDetailsInitialValue} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  