export const USER_PREFERENCE_SCHEMA_VERSION = 1;

export const DEFAULT_REQUEST_QUEUE_PAGE_SIZE = 100;

export const DEFAULT_USER_PREFERENCE_DOCUMENT = {
  schemaVersion: USER_PREFERENCE_SCHEMA_VERSION,
  preferences: {
    requestQueue: {
      pageSize: DEFAULT_REQUEST_QUEUE_PAGE_SIZE
    }
  }
};
