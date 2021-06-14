import React from "react";
import { Route, Switch } from "react-router-dom";
import {useSelector} from "react-redux";

import Header from "./Header";
import Home from "./Home";
import FOIFooter from "./Footer";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'


const FOIBaseRouting = React.memo(({store}) => {
    const isAuth = useSelector((state) => state.user.isAuthenticated);
  
    return (
      <>
        <Header/>
       
              <ToastContainer />
              <Switch>
               
                <Route exact path="/">
                <Home/>
                </Route>
              </Switch>
              
        
        <FOIFooter/>
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  