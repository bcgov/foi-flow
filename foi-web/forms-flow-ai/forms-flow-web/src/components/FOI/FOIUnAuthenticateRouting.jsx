import React, {useEffect}from "react";
import { Route, Redirect } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import 'semantic-ui-css/semantic.min.css';

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import Home from "./Home";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";

const FOIUnAuthenticateRouting = React.memo((props) => {
  let isAuth = false;

  const authToken = localStorage.getItem("authToken"); 
  
  if(authToken !== null && authToken !== '' && authToken !== undefined) {
    isAuth = true;
  }

  const dispatch = useDispatch();

  useEffect(()=>{
    if(props.store && isAuth){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);

  console.log(`UnAuth isAuth = ${isAuth}`);
  return (
      <>
       
         
            <Route exact path="/">
                <FOIHeader /> 
                <Home />
                <FOIFooter />
            </Route>
         
        ) 
      </>
    );
})

export default FOIUnAuthenticateRouting;
