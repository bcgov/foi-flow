import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import Watcher from './Watcher';
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

describe('FOI Watcher component', () => {
  
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
    let store,wrapper
   
    it("FOI Watcher Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            watcherFullList: [],
            requestWatcherList: [],
            requestId: 1,
            ministryId: 1,
            userDetail: {},
            handleWatcherUpdate:  jest.fn(),
            foiRequests: {foiWatcherList: []}           
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });       
        shallow(<Provider store={store}><Watcher watcherFullList={localState.watcherFullList} requestId={localState.requestId} ministryId={localState.ministryId} userDetail={localState.userDetail}  /></Provider>)
      });

      it('FOI Watcher snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            watcherFullList: [],            
            requestId: 1,
            ministryId: 1,
            userDetail: {},           
            foiRequests: {foiWatcherList: []}    
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });        
        const tree = renderer.create(<Provider store={store}><Watcher watcherFullList={localState.watcherFullList} requestId={localState.requestId} ministryId={localState.ministryId} userDetail={localState.userDetail} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  