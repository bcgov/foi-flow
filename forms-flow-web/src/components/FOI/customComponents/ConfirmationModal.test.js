import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import ConfirmationModal from './ConfirmationModal';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI ConfirmationModal component', () => {
  
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
   
    it("FOI ConfirmationModal Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            openModal: true,
            handleModal:  jest.fn(),
            state: 'Open', 
            saveRequestObject: {
                assignedTo: "dviswana@idir",
                assignedGroup: "Intake Team",
                idNumber: "U-001",
                selectedMinistries: [
                    {code:"AEST",name:"Ministry of Advanced Education and Skills Training",selected:"true"}
                ]
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><ConfirmationModal openModal={localState.openModal} handleModal={localState.handleModal} state={localState.state} saveRequestObject={localState.saveRequestObject} /></Provider>)
      });

      it('FOI ConfirmationModal snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            openModal: false,
            handleModal:  jest.fn(),
            state: 'Open', 
            saveRequestObject: {
                assignedTo: "dviswana@idir",
                assignedGroup: "Intake Team",
                assignedministrygroup: "Ministry of Advanced Education and Skills Training",
                assignedministryperson: "foiaed@idir",
                idNumber: "U-001",
                selectedMinistries: [
                    {code:"AEST",name:"Ministry of Advanced Education and Skills Training",selected:"true"}
                ]
            },
            foiRequests: {
              foiProcessingTeamList: [],
              foiRequestCFRForm: { status: "", feedata: {} }
            },
            user: { userDetail: {} }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><ConfirmationModal openModal={localState.openModal} handleModal={localState.handleModal} state={localState.state} saveRequestObject={localState.saveRequestObject} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  