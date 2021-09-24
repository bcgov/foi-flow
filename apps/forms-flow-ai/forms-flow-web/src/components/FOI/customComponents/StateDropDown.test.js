import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import StateDropDown from './StateDropDown';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI StateDropDown component', () => {
  
    beforeEach(() => {
        useSelector.mockImplementation(callback => {
          return callback(mockAppState);
        });
      });
      afterEach(() => {
        useSelector.mockClear();
      });

    const initialState = {output:10}
    const mockStore = configureStore()
    let store,wrapper
   
    it("FOI StateDropDown Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            requestStatus: 'Open',
            handleStateChange:  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><StateDropDown requestStatus={localState.requestStatus} handleStateChange={localState.handleStateChange} /></Provider>)
      });

      it('FOI StateDropDown snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            requestStatus: 'Open',
            handleStateChange:  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><StateDropDown requestStatus={localState.requestStatus} handleStateChange={localState.handleStateChange}  /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  