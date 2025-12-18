import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import UnAuthorized from './UnAuthorized';
import { useSelector } from "react-redux";

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('Home component', () => {
  
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
   

    it('matches Home snapshot', () => {
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
        const tree = renderer.create(<Provider store={store}><UnAuthorized/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  