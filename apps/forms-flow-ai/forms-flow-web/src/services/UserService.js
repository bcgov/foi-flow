import {
  Keycloak_Client,
  ANONYMOUS_USER,
  ANONYMOUS_ID,
} from "../constants/constants";
import {
  setUserRole,
  setUserToken,
  setUserDetails,
  setUserAuthorization,
} from "../actions/bpmActions";

import {AppConfig} from '../config';
import {WEB_BASE_URL} from "../apiManager/endpoints/config";
import {_kc} from "../constants/tenantConstant";
import { isMinistryLogin } from '../helper/FOI/helper';

const jwt = require("jsonwebtoken");

/**
 * Initializes Keycloak instance and calls the provided callback function if successfully authenticated.
 *
 * @param onAuthenticatedCallback
 */
// const KeycloakData = new Keycloak(tenantDetail);

const initKeycloak = (store, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  KeycloakData
    .init({
      onLoad: "check-sso",
      promiseType: "native",
      silentCheckSsoRedirectUri:
        window.location.origin + "/silent-check-sso.html",
      pkceMethod: "S256",
      checkLoginIframe: false
    })
    .then((authenticated) => {
      if (authenticated) {
        if (KeycloakData.resourceAccess[Keycloak_Client]) {
          const UserRoles = KeycloakData.resourceAccess[Keycloak_Client].roles;
          store.dispatch(setUserRole(UserRoles));
          store.dispatch(setUserToken(KeycloakData.token));
          //Set Cammunda/Formio Base URL
          setApiBaseUrlToLocalStorage();

          
          KeycloakData.loadUserInfo().then((res) => {
            store.dispatch(setUserDetails(res));
            const userGroups = res.groups.map(group => group.slice(1));
            const authorized = userGroups.indexOf("Intake Team") !== -1
                || userGroups.indexOf("Flex Team") !== -1
                || userGroups.indexOf("Processing Team") !== -1
                || isMinistryLogin(userGroups)
            store.dispatch(setUserAuthorization(authorized));
          });
          const email = KeycloakData.tokenParsed.email || "external";
          
          // onAuthenticatedCallback();
          done(null, KeycloakData);
          refreshToken(store);
        } else {
          doLogout();
        }
      } else {
        console.warn("not authenticated!");
        doLogin();
      }
    });
};
let refreshInterval;
const refreshToken = (store) => {
  refreshInterval = setInterval(() => {
    KeycloakData && KeycloakData.updateToken(5).then((refreshed)=> {
      if (refreshed) {
        store.dispatch(setUserToken(KeycloakData.token));
      }
    }).catch( (error)=> {
      console.log(error);
      userLogout();
    });
  }, 6000);
}


/**
 * Logout function
 */
const userLogout = () => {
  localStorage.clear();
  sessionStorage.clear();
  clearInterval(refreshInterval);
  doLogout();
};


const setApiBaseUrlToLocalStorage = ()=> {  
  localStorage.setItem("formioApiUrl", AppConfig.projectUrl);
  localStorage.setItem("formsflow.ai.url",window.location.origin)
  localStorage.setItem("formsflow.ai.api.url", WEB_BASE_URL);
}


const authenticateAnonymousUser = (store) => {
  const user = ANONYMOUS_USER;
  store.dispatch(setUserRole([user]));  
};




const KeycloakData= _kc;

const doLogin = KeycloakData.login;
const doLogout = KeycloakData.logout;
const getToken = () => 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5NmxBaVpBUi0wTXAxNy1YaFlHSEZHLUZ5XzRzdTZuc2ZWWVE3YllyMGVFIn0.eyJleHAiOjE2NDEzNDc2MzYsImlhdCI6MTY0MTM0NTgzNiwiYXV0aF90aW1lIjoxNjQxMzQ1ODM1LCJqdGkiOiI3MGRiZTI5NC0yMDM0LTRlNDAtYTBjNy0xMmRmMGI5MGRiYTMiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy81azhkYmw0aCIsImF1ZCI6WyJjYW11bmRhLXJlc3QtYXBpIiwiZm9ybXMtZmxvdy13ZWIiXSwic3ViIjoiNThhYzg3NTYtNWVhZi00NDU3LTliM2ItMTRmMWZkOWE3N2UyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZm9ybXMtZmxvdy13ZWIiLCJub25jZSI6Ijk4MjY2YjAyLWY4MjMtNDZhYy05ZjgzLTQxM2YyZDRhNWU5YiIsInNlc3Npb25fc3RhdGUiOiI3MjNlMTk2NS01YTdmLTQxZjItYjExMi1lNTI1MmJhNmM1YTUiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly8xMjcuMC4wLjE6MzAwMC8qIiwiaHR0cDovL2xvY2FsaG9zdDozMDAwLyoiLCIqIiwiaHR0cDovLzEyNy4wLjAuMToxNTAwMC8qIiwiaHR0cDovL2xvY2FsaG9zdDoxNTAwMC8qIl0sInJlc291cmNlX2FjY2VzcyI6eyJmb3Jtcy1mbG93LXdlYiI6eyJyb2xlcyI6WyJmb3Jtc2Zsb3ctY2xpZW50Il19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBjYW11bmRhLXJlc3QtYXBpIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJyb2xlIjpbImZvcm1zZmxvdy1jbGllbnQiXSwibmFtZSI6IkFwYXJuYSBTb2JoYSIsImdyb3VwcyI6WyIvZm9ybXNmbG93L2Zvcm1zZmxvdy1jbGllbnQiLCIvSW50YWtlIFRlYW0iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYXNvYmhhQGlkaXIiLCJnaXZlbl9uYW1lIjoiQXBhcm5hIiwiZmFtaWx5X25hbWUiOiJTb2JoYSIsImVtYWlsIjoiYXBhcm5hLnNvYmhhQGdvdi5iYy5jYSJ9.LLn9ny4y-jrAWXAPcv2uSJryYubXIILW7S6MacfikGenMJY-1Lxn1fxLNc1s4vrCCrxwjzwJ-4T1JAL6yQujyIDvRnBWMtTjZLRx_DsnQqDwqXHO1iU9J-t5ZH6A4GI-9HVzv9I7I9T2k7yaAVrG4znJyZGok9AjpPPCOhGa5dBw7dwBsVR9lCK9QWftdIHduUNeklpE6_BLJIpLQ94jpft1VaovpJUXzDKtn0HL-UX0P2vz8BLo4meYO8KZ9jMks35bt0hCR23j8kCTdHGq3nL1u9R6HauYvepB03TkE5rZn7CcMt2g9bh0b3PfJ3J8nT-tpFmPTrWtrwUWVI44OA';

const UserService ={
  initKeycloak,
  userLogout,
  getToken, 
  authenticateAnonymousUser
};

export default UserService;
