import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import RequestDescriptionHistory from './RequestDescriptionHistory';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI RequestDescriptionHistory component', () => {
  
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
   
    it("FOI RequestDescriptionHistory Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            requestDescriptionHistoryList : [{ createdAt:"2021-09-21 07:45:02",
                        createdBy:"dviswana@idir",
                        description:"new request for the applicant",
                        fromDate:"2021-08-01",
                        status:"Intake in Progress",
                        toDate:"2021-09-16"
                    },
                    { createdAt:"2021-09-22 07:45:02",
                    createdBy:"dviswana@idir",
                    description:"new request for the applicant",
                    fromDate:"2021-08-01",
                    status:"Intake in Progress",
                    toDate:"2021-08-31"
                }],
            openModal : true,
            handleModalClose :  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><RequestDescriptionHistory requestDescriptionHistoryList={localState.requestDescriptionHistoryList} openModal={localState.openModal} handleModalClose={localState.handleModalClose} /></Provider>)
      });

      it('FOI RequestDescriptionHistory snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            requestDescriptionHistoryList : [{ createdAt:"2021-09-21 07:45:02",
                        createdBy:"dviswana@idir",
                        description:"new request for the applicant",
                        fromDate:"2021-08-01",
                        status:"Intake in Progress",
                        toDate:"2021-09-16"
                    },
                    { createdAt:"2021-09-22 07:45:02",
                    createdBy:"dviswana@idir",
                    description:"new request for the applicant",
                    fromDate:"2021-08-01",
                    status:"Intake in Progress",
                    toDate:"2021-08-31"
                }],
            openModal : false,
            handleModalClose :  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><RequestDescriptionHistory requestDescriptionHistoryList={localState.requestDescriptionHistoryList} openModal={localState.openModal} handleModalClose={localState.handleModalClose} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  