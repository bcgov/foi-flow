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

const tokenRefreshInterval = 180000; // how often we should check for token expiry --> 180000 = 3 mins
const tokenUpdateThreshold = 600; // if token expires in less than 10 minutes (600 seconds), refresh token

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

        KeycloakData.loadUserInfo().then((res) => {  
          //Begin - Changes for IDIR mapping
          if ("identity_provider" in res && res["identity_provider"] == "idir") {
              let claim_name =  "foi_preferred_username" in res ? "foi_preferred_username" : "preferred_username"
              let claim_value =  res[claim_name].toLowerCase()
              res["preferred_username"] = claim_value.endsWith("@idir") ? claim_value : claim_value.concat("@idir")
          }  
          //End - Changed for IDIR mapping        
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
      KeycloakData.updateToken(tokenUpdateThreshold)
        .then((refreshed) => {
          if (refreshed) {
            store.dispatch(setUserToken(KeycloakData.token));
          }
        })
        .catch((error) => {
          console.log(error);
          userLogout();
        });
  }, tokenRefreshInterval);
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
