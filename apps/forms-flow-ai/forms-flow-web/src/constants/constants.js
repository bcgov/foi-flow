
//application details
export const APPLICATION_NAME =
  (window._env_ && window._env_.REACT_APP_APPLICATION_NAME) ||
  process.env.REACT_APP_APPLICATION_NAME ||
  "formsflow.ai";
//keycloak
export const Keycloak_Client =
  (window._env_ && window._env_.REACT_APP_KEYCLOAK_CLIENT) ||
  process.env.REACT_APP_KEYCLOAK_CLIENT ||
  "forms-flow-web";
export const KEYCLOAK_REALM =
  (window._env_ && window._env_.REACT_APP_KEYCLOAK_URL_REALM) ||
  process.env.REACT_APP_KEYCLOAK_URL_REALM ||
  "forms-flow-ai";
export const KEYCLOAK_URL =(window._env_ && window._env_.REACT_APP_KEYCLOAK_URL) || process.env.REACT_APP_KEYCLOAK_URL;
export const KEYCLOAK_AUTH_URL = `${KEYCLOAK_URL}/auth`;
export const ANONYMOUS_USER = "anonymous";
export const SESSION_SECURITY_KEY = "u7x!A%D*G-KaNdRgUkXp2s5v8y/B?E(H";
//6 hour in milliseconds
export const SESSION_LIFETIME = 21600000;
export const SOCKETIO_CONNECT_URL =
  (window._env_ && window._env_.REACT_APP_SOCKETIO_CONNECT_URL) ||
  process.env.REACT_APP_SOCKETIO_CONNECT_URL;

export const SOCKETIO_RECONNECTION_DELAY =
  (window._env_ && window._env_.REACT_APP_SOCKETIO_RECONNECTION_DELAY) ||
  process.env.REACT_APP_SOCKETIO_RECONNECTION_DELAY;
  
export const SOCKETIO_RECONNECTION_DELAY_MAX =
  (window._env_ && window._env_.REACT_APP_SOCKETIO_RECONNECTION_DELAY_MAX) ||
  process.env.REACT_APP_SOCKETIO_RECONNECTION_DELAY_MAX;

export const FOI_FLOW_REPORTING_URL =  (window._env_ && window._env_.REACT_APP_FOI_FLOW_REPORTING_URL) ||
process.env.REACT_APP_FOI_FLOW_REPORTING_URL;
