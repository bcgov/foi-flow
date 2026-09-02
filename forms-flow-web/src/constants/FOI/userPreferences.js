export const USER_PREFERENCE_SCHEMA_VERSION = 1;

export const DEFAULT_DASHBOARD_QUEUE_PAGE_SIZE = 100;

export const DEFAULT_USER_PREFERENCE_DOCUMENT = {
  schemaVersion: USER_PREFERENCE_SCHEMA_VERSION,
  preferences: {
    dashboard: {
      queue: {
        pageSize: DEFAULT_DASHBOARD_QUEUE_PAGE_SIZE
      }
    }
  }
};
