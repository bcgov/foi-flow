import renderer from 'react-test-renderer';
import { Provider, useSelector } from "react-redux";
import configureStore from 'redux-mock-store'
import FOIHeader from './FOIHeader';
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI Header component', () => {
  
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
    let store
   
    it("FOI Header Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith'
            },
            notifications:{
              foiNotifications:[{ created_at: "2022 JAN 13 | 11:11 AM",
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
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}><FOIHeader/></Provider>)
      });

    it('FOI header snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'John',
                preferred_username: 'John Smith'
            },
            notifications:{
              foiNotifications:[{ created_at: "2022 JAN 13 | 11:11 AM",
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
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><FOIHeader/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  