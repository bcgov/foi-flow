import userPreferences from "./userPreferencesReducer";

import {
  setUserPreferences,
  setUserPreferencesLoadFailed
} from "../../actions/FOI/userPreferenceActions";


describe("userPreferencesReducer", () => {
  test("uses request queue page size 100 by default", () => {
    const state = userPreferences(undefined, {});

    expect(
      state.preferences.requestQueue.pageSize
    ).toBe(100);

    expect(state.isLoaded).toBe(false);
    expect(state.loadError).toBe(false);
  });


  test("stores a loaded preference document", () => {
    const state = userPreferences(
      undefined,
      setUserPreferences({
        schemaVersion: 1,
        preferences: {
          requestQueue: {
            pageSize: 50
          }
        }
      })
    );

    expect(
      state.preferences.requestQueue.pageSize
    ).toBe(50);

    expect(state.isLoaded).toBe(true);
    expect(state.loadError).toBe(false);
  });


  test("records a non-fatal load failure", () => {
    const state = userPreferences(
      undefined,
      setUserPreferencesLoadFailed()
    );

    expect(
      state.preferences.requestQueue.pageSize
    ).toBe(100);

    expect(state.isLoaded).toBe(true);
    expect(state.loadError).toBe(true);
  });
});
