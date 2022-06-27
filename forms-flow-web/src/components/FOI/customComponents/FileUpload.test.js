import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import FileUpload from './FileUpload';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI FileUpload component', () => {
  
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
   
    it("FOI FileUpload Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            multipleFiles: false,
            updateFilesCb:  jest.fn(),            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><FileUpload multipleFiles={localState.multipleFiles} updateFilesCb={localState.updateFilesCb} /></Provider>)
      });

      it('FOI FileUpload snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            multipleFiles: false,
            updateFilesCb:  jest.fn(),            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><FileUpload multipleFiles={localState.multipleFiles} updateFilesCb={localState.updateFilesCb} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  