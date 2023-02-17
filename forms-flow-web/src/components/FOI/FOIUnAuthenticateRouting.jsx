import React, { useEffect } from "react";
import { Route } from "react-router-dom";
import { useDispatch } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Home from "./Home";
import Admin from "./Admin";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import { decrypt } from "../../helper/FOI/helper";

const FOIUnAuthenticateRouting = React.memo((props) => {
  let isAuth = false;

  const authToken = decrypt(localStorage.getItem("authToken"));

  if (Object.keys(authToken).length > 0) {
    isAuth = true;
  }

  const dispatch = useDispatch();

  useEffect(() => {
    if (props.store && isAuth) {
      UserService.initKeycloak(props.store, (_err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  }, [props.store, dispatch]);

  return (
    <>
      <Route path="/admin">
        <FOIHeader />
        <Admin />
        <FOIFooter />
      </Route>
      <Route exact path="/">
        <FOIHeader />
        <Home />
        <FOIFooter />
      </Route>
    </>
  );
})

export default FOIUnAuthenticateRouting;
