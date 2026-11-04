export const USER_PREFERENCES_SET = "USER_PREFERENCES_SET";
export const USER_PREFERENCES_LOAD_FAILED =
  "USER_PREFERENCES_LOAD_FAILED";

export const setUserPreferences = (document) => ({
  type: USER_PREFERENCES_SET,
  payload: document
});

export const setUserPreferencesLoadFailed = () => ({
  type: USER_PREFERENCES_LOAD_FAILED
});
