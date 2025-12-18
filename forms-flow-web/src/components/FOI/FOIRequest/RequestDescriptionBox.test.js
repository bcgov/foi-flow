import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import RequestDescriptionBox from './RequestDescriptionBox';
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

describe('FOI RequestDescriptionBox component', () => {
  
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
   
    it("FOI RequestDescriptionBox Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            programAreaList: [{"programareaid": 1, "iaocode": "AED", "isactive": true, "name": "Ministry of Advanced Education and Skills Training",
            "type": "BC GOV Ministry", "bcgovcode": "AEST"}, {"programareaid": 2, "iaocode": "AGR", "isactive": true, "name":
            "Ministry of Agriculture, Food and Fisheries", "type": "BC GOV Ministry", "bcgovcode": "AFF"}, {"programareaid": 3,
            "iaocode": "MAG", "isactive": true, "name": "Ministry of Attorney General", "type": "BC GOV Ministry", "bcgovcode":
            "AG"}, {"programareaid": 4, "iaocode": "CFD", "isactive": true, "name": "Ministry of Children and Family Development",
            "type": "BC GOV Ministry", "bcgovcode": "MCF"}, {"programareaid": 5, "iaocode": "CTZ", "isactive": true, "name":
            "Ministry of Citizens\u2019 Services", "type": "BC GOV Ministry", "bcgovcode": "CITZ"}, {"programareaid": 6, "iaocode":
            "EDU", "isactive": true, "name": "Ministry of Education", "type": "BC GOV Ministry", "bcgovcode": "EDUC"},
            {"programareaid": 7, "iaocode": "EML", "isactive": true, "name": "Ministry of Energy, Mines and Low Carbon Innovation",
            "type": "BC GOV Ministry", "bcgovcode": "EMLI"}, {"programareaid": 8, "iaocode": "MOE", "isactive": true, "name":
            "Ministry of Environment and Climate Change Strategy", "type": "BC GOV Ministry", "bcgovcode": "ENV"}
            ],       
            handleOnChangeRequiredRequestDescriptionValues:  jest.fn(),
            handleInitialRequiredRequestDescriptionValues:  jest.fn(),
            handleUpdatedProgramAreaList:  jest.fn(),                                  
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                fromDate: '2021-08-01',
                toDate: '2021-08-31',
                description: 'test request',
                selectedMinistries: [
                    {code:"AEST",name:"Ministry of Advanced Education and Skills Training",selected:"true"}
                ],
                ispiiredacted: '2021-08-02'
            },
            foiRequests: { 
                foiProgramAreaList: [],
                foiRequestDescriptionHistoryList: []
            }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        });   
        shallow(<Provider store={store}><RequestDescriptionBox handleUpdatedProgramAreaList={localState.handleUpdatedProgramAreaList} handleInitialRequiredRequestDescriptionValues={localState.handleInitialRequiredRequestDescriptionValues} handleOnChangeRequiredRequestDescriptionValues={localState.handleOnChangeRequiredRequestDescriptionValues} programAreaList={localState.programAreaList} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} /></Provider>)
      });

      it('FOI RequestDescriptionBox snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            programAreaList: [{"programareaid": 1, "iaocode": "AED", "isactive": true, "name": "Ministry of Advanced Education and Skills Training",
            "type": "BC GOV Ministry", "bcgovcode": "AEST"}, {"programareaid": 2, "iaocode": "AGR", "isactive": true, "name":
            "Ministry of Agriculture, Food and Fisheries", "type": "BC GOV Ministry", "bcgovcode": "AFF"}, {"programareaid": 3,
            "iaocode": "MAG", "isactive": true, "name": "Ministry of Attorney General", "type": "BC GOV Ministry", "bcgovcode":
            "AG"}, {"programareaid": 4, "iaocode": "CFD", "isactive": true, "name": "Ministry of Children and Family Development",
            "type": "BC GOV Ministry", "bcgovcode": "MCF"}, {"programareaid": 5, "iaocode": "CTZ", "isactive": true, "name":
            "Ministry of Citizens\u2019 Services", "type": "BC GOV Ministry", "bcgovcode": "CITZ"}, {"programareaid": 6, "iaocode":
            "EDU", "isactive": true, "name": "Ministry of Education", "type": "BC GOV Ministry", "bcgovcode": "EDUC"},
            {"programareaid": 7, "iaocode": "EML", "isactive": true, "name": "Ministry of Energy, Mines and Low Carbon Innovation",
            "type": "BC GOV Ministry", "bcgovcode": "EMLI"}, {"programareaid": 8, "iaocode": "MOE", "isactive": true, "name":
            "Ministry of Environment and Climate Change Strategy", "type": "BC GOV Ministry", "bcgovcode": "ENV"}
            ],       
            handleOnChangeRequiredRequestDescriptionValues:  jest.fn(),
            handleInitialRequiredRequestDescriptionValues:  jest.fn(),
            handleUpdatedProgramAreaList:  jest.fn(),                                  
            createSaveRequestObject:  jest.fn(),
            requestDetails: {
                fromDate: '2021-08-01',
                toDate: '2021-08-31',
                description: 'test request',
                selectedMinistries: [
                    {code:"AEST",name:"Ministry of Advanced Education and Skills Training",selected:"true"}
                ],
                ispiiredacted: '2021-08-02'
            },
            foiRequests: { 
                foiProgramAreaList: [],
                foiRequestDescriptionHistoryList: []
            },
            requiredRequestDetailsValues: { requestType: "general" }
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        useParams.mockImplementation(() => {
            return {ministryId: "123"};
        }); 
        const tree = renderer.create(<Provider store={store}><RequestDescriptionBox handleUpdatedProgramAreaList={localState.handleUpdatedProgramAreaList} handleInitialRequiredRequestDescriptionValues={localState.handleInitialRequiredRequestDescriptionValues} handleOnChangeRequiredRequestDescriptionValues={localState.handleOnChangeRequiredRequestDescriptionValues} programAreaList={localState.programAreaList} requestDetails={localState.requestDetails} createSaveRequestObject={localState.createSaveRequestObject} requiredRequestDetailsValues={localState.requiredRequestDetailsValues} /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  