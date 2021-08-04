import {render, screen, cleanup} from '@testing-library/react';
import renderer from 'react-test-renderer';
import { Provider } from "react-redux";
import configureStore from 'redux-mock-store'
import FOIFooter from '../FOIFooter';

afterEach(() => {
  cleanup();
})
describe('With React Testing Library', () => {
    const initialState = {output:10}
    const mockStore = configureStore()
    let store,wrapper
  
    it('matches snapshot', () => {
        store = mockStore(initialState)
        const tree = renderer.create(<Provider store={store}><FOIFooter/></Provider>).toJSON();  
        expect(tree).toMatchSnapshot();
    })
  })


  