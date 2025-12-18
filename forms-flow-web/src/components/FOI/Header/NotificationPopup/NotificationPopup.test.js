import renderer from 'react-test-renderer';
import { Provider, useSelector } from "react-redux";
import configureStore from 'redux-mock-store'
import NotificationPopup from './NotificationPopup';
import { shallow } from 'enzyme';
import { useParams } from "react-router-dom";

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
}));
jest.mock("react-router-dom", () => ({
    ...jest.requireActual("react-router-dom"),
    useParams: jest.fn(),
}));

describe('Notification Popup component', () => {
  
    const mockAppState = {
        'ministryId': ""
      }
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
   
    it("Notification Popup Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            foiRequests: { 
                foiFullAssignedToList: [],
                foiMinistryAssignedToList: [],
                foiRequestDetail: {}
            },
            notifications: 
                [{created_at: "2022 JAN 13 | 11:11 AM",
                createdby: "foiintake@idir",
                foirequestid: 1,
                idnumber: "CITZ-2022-121786",
                notification: "Moved to Call For Records State",
                notificationid: 5,
                notificationtype: "State",
                notificationusertype: "Assignee",
                requestid: 1,
                requesttype: "ministryrequest"}]
              
        }        
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        shallow(<Provider store={store}><NotificationPopup /></Provider>)
      });

      it('Notification Popup snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            foiRequests: { 
                foiFullAssignedToList: [],
                foiMinistryAssignedToList: [],
                foiRequestDetail: {}
            },
            notifications:[{ created_at: "2022 JAN 13 | 11:11 AM",
            createdby: "foiintake@idir",
            foirequestid: 1,
            idnumber: "CITZ-2022-121786",
            notification: "Moved to Call For Records State",
            notificationid: 5,
            notificationtype: "State",
            notificationusertype: "Assignee",
            requestid: 1,
            requesttype: "ministryrequest"}]
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
        });
        const tree = renderer.create(<Provider store={store}><NotificationPopup notifications={localState.notifications}/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  