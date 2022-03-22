import {
  Keycloak_Client,
  ANONYMOUS_USER
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
import {
  isMinistryLogin,
  isProcessingTeam,
  isIntakeTeam,
  isFlexTeam,
} from "../helper/FOI/helper";

const jwt = require("jsonwebtoken");

/**
 * Initializes Keycloak instance and calls the provided callback function if successfully authenticated.
 *
 * @param onAuthenticatedCallback
 */

const initKeycloak = (store, ...rest) => {
  const done = rest.length ? rest[0] : () => {};
  KeycloakData.init({
    onLoad: "check-sso",
    promiseType: "native",
    silentCheckSsoRedirectUri:
      window.location.origin + "/silent-check-sso.html",
    pkceMethod: "S256",
    checkLoginIframe: false,
  }).then((authenticated) => {
    if (authenticated) {
      if (KeycloakData.resourceAccess[Keycloak_Client]) {
        const UserRoles = KeycloakData.resourceAccess[Keycloak_Client].roles;
        store.dispatch(setUserRole(UserRoles));
        store.dispatch(setUserToken(KeycloakData.token));
        //Set Cammunda/Formio Base URL
        setApiBaseUrlToLocalStorage();

        KeycloakData.loadUserInfo().then((res) => {
          store.dispatch(setUserDetails(res));
          const userGroups = res.groups.map((group) => group.slice(1));
          const authorized =
            isIntakeTeam(userGroups) ||
            isFlexTeam(userGroups) ||
            isProcessingTeam(userGroups) ||
            isMinistryLogin(userGroups);
          store.dispatch(setUserAuthorization(authorized));
        });
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
    KeycloakData &&
      //updateToken(x), update token if expiry date is under x seconds
      KeycloakData.updateToken(5)
        .then((refreshed) => {
          if (refreshed) {
            store.dispatch(setUserToken(KeycloakData.token));
          }
        })
        .catch((error) => {
          console.log(error);
          userLogout();
        });        
  }, 6000);
};

/**
 * Logout function
 */
const userLogout = () => {
  localStorage.clear();
  sessionStorage.clear();
  clearInterval(refreshInterval);
  doLogout();
};

const setApiBaseUrlToLocalStorage = () => {
  localStorage.setItem("formioApiUrl", AppConfig.projectUrl);
  localStorage.setItem("formsflow.ai.url", window.location.origin);
  localStorage.setItem("formsflow.ai.api.url", WEB_BASE_URL);
};

const authenticateAnonymousUser = (store) => {
  const user = ANONYMOUS_USER;
  store.dispatch(setUserRole([user]));
};

const KeycloakData= _kc;

const doLogin = KeycloakData.login;
const doLogout = KeycloakData.logout;
const getToken = () => KeycloakData.token;

const UserService ={
  initKeycloak,
  userLogout,
  getToken, 
  authenticateAnonymousUser
};

export default UserService;
