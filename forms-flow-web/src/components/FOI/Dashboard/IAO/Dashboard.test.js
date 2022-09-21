import React from "react";
import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import Dashboard from './Dashboard';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';
import thunk from "redux-thunk";

const middlewares = [thunk];

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
}));
jest.mock("react", () => ({
    ...jest.requireActual("react"),
    useContext: jest.fn(),
}));

const mockAdvancedSearchContext = (localState) =>
  jest.spyOn(React, "useContext").mockImplementation((context) => {
    // only stub the response if it is one of your Context
    if (context.displayName === "AdvancedSearchContext") {
      return localState;
    }

    // continue to use original useContext for the rest use cases
    const ActualReact = jest.requireActual("react");
    return ActualReact.useContext(context);
});

describe('FOI Dashboard component', () => {
  
    beforeEach(() => {
        useSelector.mockImplementation(callback => {
          return callback(mockAppState);
        });
      });
      afterEach(() => {
        useSelector.mockClear();
      });

    const initialState = {
      output:10,
      foiRequests: {
        foiProgramAreaList: [],
        foiProcessingTeamList: []
      },
      queueParams: {
        rowsState: {
          page: 1,
          pageSize: 100
        },
        keyword: ""
      },
      advancedSearchParams: {
        rowsState: {
          page: 1,
          pageSize: 100
        },
        keywords: [],
        requestState: [],
        requestType: [],
        requestStatus: []
      },
      setAdvancedSearchComponentLoading: jest.fn(),
      setSearchLoading: jest.fn(),
      handleUpdateSearchFilter: jest.fn(),
    }
    const mockStore = configureStore(middlewares)
    let store,wrapper
   
    it("FOI Dashboard Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        mockAdvancedSearchContext(initialState);

        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith',
                userDetail: {
                  groups: ['/Flex Team', '/Intake Team']
                }
            },
            userDetail: {
              groups: ['/Flex Team', '/Intake Team']
            },
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><Dashboard userDetail={localState.userDetail} /></Provider>)
      });

      it('FOI header snapshot check', () => {
        store = mockStore(initialState)
        mockAdvancedSearchContext(initialState);

        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith',
                userDetail: {
                  groups: ['/Flex Team', '/Intake Team']
                }
            },
            foiRequests:{foiProgramAreaList:[], queueParams: { rowsState: {page: 0, pageSize: 100} } },
            userDetail: {
              groups: ['/Flex Team', '/Intake Team']
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><Dashboard userDetail={localState.userDetail} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  