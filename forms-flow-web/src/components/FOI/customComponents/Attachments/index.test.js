import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import AttachmentSection from './index';
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

describe('FOI Request Attachments component', () => {
  
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
   
    it("FOI Request Attachments Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
          attachmentsArray: []
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {requestId: "123", ministryId: "234", requestState: "Fee Assessment"};
        });   
        shallow(<Provider store={store}><AttachmentSection attachmentsArray={localState.attachmentsArray} /></Provider>)
      });

      it('FOI Request Attachments snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
          attachmentsArray: []
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {requestId: "123", ministryId: "234", requestState: "Fee Assessment"};
        }); 
        const tree = renderer.create(<Provider store={store}><AttachmentSection attachmentsArray={localState.attachmentsArray} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  