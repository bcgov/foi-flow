import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import AttachmentModal from './AttachmentModal';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI AttachmentModal component', () => {
  
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
   
    it("FOI AttachmentModal Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            openModal: false,
            modalFor: 'add',
            handleModal:  jest.fn(),
            multipleFiles: true,
            requestNumber: '',
            requestId: 1,
            attachment: {},
            attachmentsArray: [],
            handleRename: jest.fn(),
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><AttachmentModal modalFor={localState.modalFor} openModal={localState.openModal} handleModal={localState.handleModal} multipleFiles={localState.multipleFiles} requestNumber={localState.requestNumber} requestId={localState.requestId} attachment={localState.attachment} attachmentsArray={localState.attachmentsArray} handleRename={localState.handleRename} /></Provider>)
      });

      it('FOI AttachmentModal snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            openModal: false,
            modalFor: 'add',
            handleModal:  jest.fn(),
            multipleFiles: true,
            requestNumber: '',
            requestId: 1,
            attachment: {},
            attachmentsArray: [],
            handleRename: jest.fn(),            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><AttachmentModal modalFor={localState.modalFor} openModal={localState.openModal} handleModal={localState.handleModal} multipleFiles={localState.multipleFiles} requestNumber={localState.requestNumber} requestId={localState.requestId} attachment={localState.attachment} attachmentsArray={localState.attachmentsArray} handleRename={localState.handleRename} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  