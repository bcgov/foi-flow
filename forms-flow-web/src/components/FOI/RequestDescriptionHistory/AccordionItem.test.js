import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import AccordionItem from './AccordionItem';
import { useSelector } from "react-redux";
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI AccordionItem component', () => {
  
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
   
    it("FOI AccordionItem Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            details : { createdAt:"2021-09-21 07:45:02",
                        createdBy:"aandrews@idir",
                        description:"new request for the applicant",
                        fromDate:"2021-08-01",
                        status:"Intake in Progress",
                        toDate:"2021-09-16"
                    },
            index : 0,
            expanded : 'panel1',
            handleChange :  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><AccordionItem details={localState.details} index={localState.index} expanded={localState.expanded} handleChange={localState.handleChange} /></Provider>)
      });

      it('FOI AccordionItem snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            details : { createdAt:"2021-09-21 07:45:02",
                        createdBy:"aandrews@idir",
                        description:"new request for the applicant",
                        fromDate:"2021-08-01",
                        status:"Intake in Progress",
                        toDate:"2021-09-16"
                    },
            index : 0,
            expanded : 'panel1',
            handleChange :  jest.fn()
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><AccordionItem details={localState.details} index={localState.index} expanded={localState.expanded} handleChange={localState.handleChange} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  