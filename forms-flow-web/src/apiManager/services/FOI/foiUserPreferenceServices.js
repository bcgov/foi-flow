import {
  httpGETRequest,
  httpPUTRequest
} from "../../httpRequestHandler";

import API from "../../endpoints";

import {
  setQueueParams
} from "../../../actions/FOI/foiRequestActions";

import {
  setUserPreferences,
  setUserPreferencesLoadFailed
} from "../../../actions/FOI/userPreferenceActions";

import {
  USER_PREFERENCE_SCHEMA_VERSION,
  DEFAULT_DASHBOARD_QUEUE_PAGE_SIZE,
  DEFAULT_USER_PREFERENCE_DOCUMENT
} from "../../../constants/FOI/userPreferences";


const normalizePageSize = (pageSize) => {
  const numericPageSize = Number(pageSize);

  if (
    Number.isInteger(numericPageSize) &&
    numericPageSize > 0
  ) {
    return numericPageSize;
  }

  return DEFAULT_DASHBOARD_QUEUE_PAGE_SIZE;
};


export const normalizeUserPreferenceDocument = (document = {}) => {
  const sourcePreferences =
    document &&
    typeof document.preferences === "object" &&
    document.preferences !== null
      ? document.preferences
      : {};

  const sourceDashboard =
    sourcePreferences.dashboard &&
    typeof sourcePreferences.dashboard === "object"
      ? sourcePreferences.dashboard
      : {};

  const sourceQueue =
    sourceDashboard.queue &&
    typeof sourceDashboard.queue === "object"
      ? sourceDashboard.queue
      : {};

  return {
    schemaVersion: USER_PREFERENCE_SCHEMA_VERSION,
    preferences: {
      ...sourcePreferences,
      dashboard: {
        ...sourceDashboard,
        queue: {
          ...sourceQueue,
          pageSize: normalizePageSize(sourceQueue.pageSize)
        }
      }
    }
  };
};


export const buildQueuePageSizePreferenceDocument = (
  currentDocument,
  pageSize
) => {
  const normalized =
    normalizeUserPreferenceDocument(currentDocument);

  return {
    schemaVersion: USER_PREFERENCE_SCHEMA_VERSION,
    preferences: {
      ...normalized.preferences,
      dashboard: {
        ...normalized.preferences.dashboard,
        queue: {
          ...normalized.preferences.dashboard.queue,
          pageSize: normalizePageSize(pageSize)
        }
      }
    }
  };
};


export const fetchUserPreferences = () => {
  return (dispatch, getState) => {
    return httpGETRequest(
      API.FOI_USER_PREFERENCES,
      {}
    )
      .then((res) => {
        const document =
          normalizeUserPreferenceDocument(res.data);

        dispatch(setUserPreferences(document));

        const currentQueueParams =
          getState().foiRequests?.queueParams || {};

        const currentRowsState =
          currentQueueParams.rowsState || {
            page: 0,
            pageSize: DEFAULT_DASHBOARD_QUEUE_PAGE_SIZE
          };

        dispatch(
          setQueueParams({
            ...currentQueueParams,
            rowsState: {
              ...currentRowsState,
              page: 0,
              pageSize:
                document.preferences.dashboard.queue.pageSize
            }
          })
        );

        return document;
      })
      .catch((error) => {
        console.warn(
          "Unable to load user preferences; using defaults.",
          error
        );

        dispatch(setUserPreferencesLoadFailed());

        return DEFAULT_USER_PREFERENCE_DOCUMENT;
      });
  };
};


// One in-flight PUT per Redux store: later changes must not be saved
// or applied out of order. Use dispatch as the per-store identity.
const pendingPageSizeSaves = new WeakMap();


export const saveDashboardQueuePageSize = (pageSize) => {
  return (dispatch, getState) => {
    const previousSave =
      pendingPageSizeSaves.get(dispatch) || Promise.resolve();

    // Read the current document when this save reaches the front of
    // the queue so other preference fields from prior saves survive.
    const save = previousSave.catch(() => null).then(() => {
      const currentPreferences = getState().userPreferences;

      if (
        !currentPreferences?.isLoaded ||
        currentPreferences?.loadError
      ) {
        console.warn(
          "User preferences are not available; page size was not persisted."
        );

        return null;
      }

      const document =
        buildQueuePageSizePreferenceDocument(
          currentPreferences,
          pageSize
        );

      return httpPUTRequest(
        API.FOI_USER_PREFERENCES,
        document
      )
        .then((res) => {
          const savedDocument =
            normalizeUserPreferenceDocument(res.data);

          dispatch(setUserPreferences(savedDocument));

          return savedDocument;
        })
        .catch((error) => {
          console.warn(
            "Unable to save dashboard queue page size.",
            error
          );

          return null;
        });
    });

    pendingPageSizeSaves.set(dispatch, save);
    return save;
  };
};
