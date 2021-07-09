import React, {useEffect}from "react";
import { Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import Dashboard from "./Dashboard";
import ReviewRequest from "./ReviewRequest";
const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated);

  useEffect(()=>{
    console.log('authenticate')
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);

  return (
      <>
        {isAuth ? (
          <>
          <FOIHeader /> 
          
            <Route exact path="/foi/dashboard">                
                <Dashboard />                
            </Route>
            <Route path="/foi/reviewrequest">   
                   
                <ReviewRequest />  
                       
            </Route>
           
            <FOIFooter />
            </>
         ) : (
          <Loading />
        )} 
      </>
    );
})

export default FOIAuthenticateRouting;
