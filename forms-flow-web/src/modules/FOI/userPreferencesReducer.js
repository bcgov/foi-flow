import {
  USER_PREFERENCES_SET,
  USER_PREFERENCES_LOAD_FAILED
} from "../../actions/FOI/userPreferenceActions";

import {
  DEFAULT_USER_PREFERENCE_DOCUMENT
} from "../../constants/FOI/userPreferences";


const initialState = {
  ...DEFAULT_USER_PREFERENCE_DOCUMENT,
  isLoaded: false,
  loadError: false
};


const userPreferences = (state = initialState, action) => {
  switch (action.type) {
    case USER_PREFERENCES_SET:
      return {
        ...state,
        ...action.payload,
        isLoaded: true,
        loadError: false
      };

    case USER_PREFERENCES_LOAD_FAILED:
      return {
        ...state,
        isLoaded: true,
        loadError: true
      };

    default:
      return state;
  }
};


export default userPreferences;
