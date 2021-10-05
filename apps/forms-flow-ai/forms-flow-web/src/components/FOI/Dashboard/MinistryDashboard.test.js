import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import MinistryDashboard from './MinistryDashboard';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI MinistryDashboard component', () => {
  
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
   
    it("FOI MinistryDashboard Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith'
            }        
            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><MinistryDashboard/></Provider>)
      });

      it('FOI MinistryDashboard snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith'
            },
            foiRequests:{"foiMinistryRequestsList":[], "foiFullAssignedToList": []},            
            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><MinistryDashboard/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  