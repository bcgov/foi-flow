import React, {useEffect}from "react";
import { Route, Redirect } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import 'semantic-ui-css/semantic.min.css';

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import Dashboard from "./Dashboard";

const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated);

  useEffect(()=>{
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);

  console.log(`isAuth = ${isAuth}`);
  return (
      <>
        {isAuth ? (
         
            <Route exact path="/Dashboard">
                <FOIHeader /> 
                <Dashboard />
                <FOIFooter />
            </Route>
         
        ) : (
          <Loading />
        )}
      </>
    );
})

export default FOIAuthenticateRouting;
