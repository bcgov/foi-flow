import React from "react";
import { Route, Switch } from "react-router-dom";
import {useSelector} from "react-redux";

import FOIHeader from "./Header";
import Home from "./Home";
import Dashboard from "./Dashboard";
import FOIFooter from "./Footer";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'


const FOIBaseRouting = React.memo(({store}) => {
    const isAuth = useSelector((state) => state.user.isAuthenticated);
    console.log("Debug is authenticated "+ isAuth);
    return (
      <>
        <FOIHeader/>
       
              <ToastContainer />
              <Switch>
               
                <Route exact path="/">
                    <Home/>
                </Route>
                <Route exact path="/Dashboard">
                    <Dashboard store={store}/>
                </Route>
              </Switch>
              
        
        <FOIFooter/>
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  