import {
  httpGETRequest,
  httpPUTRequest
} from "../../httpRequestHandler";

import API from "../../endpoints";

import {
  setQueueParams
} from "../../../actions/FOI/foiRequestActions";

import {
  USER_PREFERENCES_SET,
  USER_PREFERENCES_LOAD_FAILED
} from "../../../actions/FOI/userPreferenceActions";

import {
  normalizeUserPreferenceDocument,
  buildQueuePageSizePreferenceDocument,
  fetchUserPreferences,
  saveDashboardQueuePageSize
} from "./foiUserPreferenceServices";


jest.mock("../../httpRequestHandler", () => ({
  httpGETRequest: jest.fn(),
  httpPUTRequest: jest.fn()
}));

jest.mock(
  "../../../actions/FOI/foiRequestActions",
  () => ({
    setQueueParams: jest.fn((payload) => ({
      type: "TEST_QUEUE_PARAMS",
      payload
    }))
  })
);


const queueParams = {
  rowsState: {
    page: 3,
    pageSize: 100
  },
  sortModel: false,
  keyword: null
};


describe("foiUserPreferenceServices", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });


  test("merges backend empty preferences with frontend defaults", () => {
    const document =
      normalizeUserPreferenceDocument({
        schemaVersion: 1,
        preferences: {}
      });

    expect(
      document.preferences.dashboard.queue.pageSize
    ).toBe(100);
  });


  test("preserves other preferences when changing queue page size", () => {
    const document =
      buildQueuePageSizePreferenceDocument(
        {
          schemaVersion: 1,
          preferences: {
            exampleSetting: true,
            dashboard: {
              queue: {
                pageSize: 100
              }
            }
          }
        },
        50
      );

    expect(document.preferences.exampleSetting).toBe(true);

    expect(
      document.preferences.dashboard.queue.pageSize
    ).toBe(50);
  });


  test("loads saved page size and applies it to queue params", async () => {
    httpGETRequest.mockResolvedValue({
      data: {
        schemaVersion: 1,
        preferences: {
          dashboard: {
            queue: {
              pageSize: 50
            }
          }
        }
      }
    });

    const dispatch = jest.fn();

    const getState = () => ({
      foiRequests: {
        queueParams
      }
    });

    await fetchUserPreferences()(dispatch, getState);

    expect(httpGETRequest).toHaveBeenCalledWith(
      API.FOI_USER_PREFERENCES,
      {}
    );

    expect(setQueueParams).toHaveBeenCalledWith({
      ...queueParams,
      rowsState: {
        ...queueParams.rowsState,
        page: 0,
        pageSize: 50
      }
    });

    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: USER_PREFERENCES_SET
      })
    );
  });


  test("preference load failure falls back without throwing", async () => {
    const warning = jest
      .spyOn(console, "warn")
      .mockImplementation(() => {});

    httpGETRequest.mockRejectedValue(
      new Error("preference API unavailable")
    );

    const dispatch = jest.fn();

    const result =
      await fetchUserPreferences()(
        dispatch,
        () => ({
          foiRequests: {
            queueParams
          }
        })
      );

    expect(
      result.preferences.dashboard.queue.pageSize
    ).toBe(100);

    expect(dispatch).toHaveBeenCalledWith({
      type: USER_PREFERENCES_LOAD_FAILED
    });

    warning.mockRestore();
  });


  test("saves queue page size with the whole preference document", async () => {
    const currentPreferences = {
      schemaVersion: 1,
      preferences: {
        exampleSetting: "preserved",
        dashboard: {
          queue: {
            pageSize: 100
          }
        }
      },
      isLoaded: true,
      loadError: false
    };

    httpPUTRequest.mockImplementation(
      (_url, document) =>
        Promise.resolve({
          data: document
        })
    );

    const dispatch = jest.fn();

    const saved =
      await saveDashboardQueuePageSize(50)(
        dispatch,
        () => ({
          userPreferences: currentPreferences
        })
      );

    expect(httpPUTRequest).toHaveBeenCalledWith(
      API.FOI_USER_PREFERENCES,
      expect.objectContaining({
        schemaVersion: 1
      })
    );

    const sentDocument =
      httpPUTRequest.mock.calls[0][1];

    expect(
      sentDocument.preferences.dashboard.queue.pageSize
    ).toBe(50);

    expect(
      sentDocument.preferences.exampleSetting
    ).toBe("preserved");

    expect(
      saved.preferences.dashboard.queue.pageSize
    ).toBe(50);

    expect(dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: USER_PREFERENCES_SET
      })
    );
  });


  test("does not save before preferences finish loading", async () => {
    const warning = jest
      .spyOn(console, "warn")
      .mockImplementation(() => {});

    const result =
      await saveDashboardQueuePageSize(50)(
        jest.fn(),
        () => ({
          userPreferences: {
            isLoaded: false,
            loadError: false
          }
        })
      );

    expect(result).toBeNull();
    expect(httpPUTRequest).not.toHaveBeenCalled();

    warning.mockRestore();
  });


  test("does not overwrite preferences after a load failure", async () => {
    const warning = jest
      .spyOn(console, "warn")
      .mockImplementation(() => {});

    const result =
      await saveDashboardQueuePageSize(50)(
        jest.fn(),
        () => ({
          userPreferences: {
            isLoaded: true,
            loadError: true
          }
        })
      );

    expect(result).toBeNull();
    expect(httpPUTRequest).not.toHaveBeenCalled();

    warning.mockRestore();
  });
});
