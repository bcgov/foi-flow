import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';
import Router, { useParams } from "react-router-dom";
import RequestTracking from './RequestTracking';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
}));
jest.mock("react-router-dom", () => ({
    ...jest.requireActual("react-router-dom"),
    useParams: jest.fn(),
}));

describe('FOI DivisionalStages component', () => {
  
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
   
    it("FOI DivisionalStages Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {            
            minDivStages: [{id:0,divisionid:1,stageid:1}],
            stageIterator:  [{id:0,divisionid:-1,stageid:-1}],
            divisionalstages:{divisions: [{divisionid: 2, name: "Deputy Minister's Office"}] , stages:[{stageid: 1, name: "Clarification"}] },      
            popminDivstatetoParent:  jest.fn(),            
            foiRequests: {foiMinistryDivisionalStages: {}},
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        
        shallow(<Provider store={store}><RequestTracking ministrycode="EDUC" existingDivStages={localState.minDivStages} pubmindivstagestomain={localState.popminDivstatetoParent} /></Provider>)
      });

      it('FOI DivisionalStages snapshot check', () => {
        store = mockStore(initialState)
        const localState = {            
            minDivStages: [{id:0,divisionid:1,stageid:1}],
            stageIterator:  [{id:0,divisionid:-1,stageid:-1}],
            divisionalstages:{divisions: [{divisionid: 2, name: "Deputy Minister's Office"}] , stages:[{stageid: 1, name: "Clarification"}] } ,
            popminDivstatetoParent:  jest.fn(),   
            foiRequests: {foiMinistryDivisionalStages: {}},     
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        
        const tree = renderer.create(<Provider store={store}><RequestTracking ministrycode="EDUC" existingDivStages={localState.minDivStages} pubmindivstagestomain={localState.popminDivstatetoParent} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })