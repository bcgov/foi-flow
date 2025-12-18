import renderer from 'react-test-renderer';
import { Provider ,useSelector } from "react-redux";
import configureStore from 'redux-mock-store'
import CommentSection from './index';
import { shallow } from 'enzyme';

jest.mock("react-redux", () => ({
    ...jest.requireActual("react-redux"),
    useSelector: jest.fn()
  }));

describe('FOI Comments component', () => {
  
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
   
    it("FOI Comments Rendering Unit test - shallow check", () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'Abin Antony',
                preferred_username: 'aantony@idir'
            },
            setComment:  jest.fn(),
            userDetail: {name: 'Abin Antony',
            preferred_username: 'aantony@idir'},
            requestNotes:  [{"userId": "sumathi", "commentId": 16, "text": "test", "date": "2021-11-08 10:36:51.866321", "replies": []}, {"userId":
            "sumathi", "commentId": 15, "text": "test", "date": "2021-11-08 10:20:15.848376", "replies": []}, {"userId": "sumathi",
            "commentId": 14, "text": "test-child22222", "date": "2021-11-08 10:17:30.792839", "replies": []}]
            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });    
        shallow(<Provider store={store}>
            <CommentSection currentUser={localState.userDetail && { userId: localState.userDetail.preferred_username, avatarUrl: '', name: 'Abin Antony' }} commentsArray={localState.requestNotes}
                    setComment={localState.setComment} signinUrl={'url'} signupUrl={'url'} requestid={1} ministryId={1} bcgovcode={'EDUC'}  />
        </Provider>)
      });

      it('FOI header snapshot check', () => {
        store = mockStore(initialState)
        const localState = {
            isAuthenticated: true,
            user: {
                name: 'Abin Antony',
                preferred_username: 'aantony@idir'
            },
            setComment:  jest.fn(),
            userDetail: {name: 'Abin Antony',
            preferred_username: 'aantony@idir'},
            requestNotes:  [{"userId": "sumathi", "commentId": 16, "text": "test", "date": "2021-11-08 10:36:51.866321", "replies": []}, {"userId":
            "sumathi", "commentId": 15, "text": "test", "date": "2021-11-08 10:20:15.848376", "replies": []}, {"userId": "sumathi",
            "commentId": 14, "text": "test-child22222", "date": "2021-11-08 10:17:30.792839", "replies": []}]
            
        }
        useSelector.mockImplementation(callback => {
            return callback(localState);
          });
        const tree = renderer.create(<Provider store={store}><CommentSection currentUser={localState.userDetail && { userId: localState.userDetail.preferred_username, avatarUrl: '', name: 'Abin Antony' }} commentsArray={localState.requestNotes}
        setComment={localState.setComment} signinUrl={'url'} signupUrl={'url'} requestid={1} ministryId={1} bcgovcode={'EDUC'}  /></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  