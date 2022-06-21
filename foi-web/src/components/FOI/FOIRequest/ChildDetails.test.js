import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import ChildDetails from './ChildDetails';
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

describe('FOI ChildDetails component', () => {
  
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
   
    it("FOI ChildDetails Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {                       
            createSaveRequestObject:  jest.fn(),
            additionalInfo: {
                childFirstName: 'Emma',
                childMiddleName: 'Geller',             
                childLastName: 'Green',
                childAlsoKnownAs: 'Emma',
                childBirthDate: '2018-01-01'
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><ChildDetails additionalInfo={localState.additionalInfo} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI ChildDetails snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            createSaveRequestObject:  jest.fn(),
            additionalInfo: {
                childFirstName: 'Emma',
                childMiddleName: 'Geller',             
                childLastName: 'Green',
                childAlsoKnownAs: 'Emma',
                childBirthDate: '2018-01-01'
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><ChildDetails additionalInfo={localState.additionalInfo} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  