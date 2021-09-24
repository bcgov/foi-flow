import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import OnBehalfOfDetails from './OnBehalfOfDetails';
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

describe('FOI OnBehalfOfDetails component', () => {
  
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
   
    it("FOI OnBehalfOfDetails Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {                       
            createSaveRequestObject:  jest.fn(),
            additionalInfo: {
                anotherFirstName: 'Jack',
                anotherMiddleName: 'M',
                anotherLastName: 'Smith',
                anotherAlsoKnownAs: 'Jack',
                anotherBirthDate: '2000-01-01'
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><OnBehalfOfDetails additionalInfo={localState.additionalInfo} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI OnBehalfOfDetails snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            createSaveRequestObject:  jest.fn(),
            additionalInfo: {
                anotherFirstName: 'Jack',
                anotherMiddleName: 'M',
                anotherLastName: 'Smith',
                anotherAlsoKnownAs: 'Jack',
                anotherBirthDate: '2000-01-01'
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><OnBehalfOfDetails additionalInfo={localState.additionalInfo} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  