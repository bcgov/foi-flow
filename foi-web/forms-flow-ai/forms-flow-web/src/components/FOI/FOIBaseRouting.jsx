import React from "react";
import { Route, Switch } from "react-router-dom";
import {useSelector} from "react-redux";

import FOIFooter from "./Footer";
import FOIHeader from "./Header";

import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'


const FOIBaseRouting = React.memo(({store}) => {
    const isAuth = useSelector((state) => state.user.isAuthenticated);
  
    return (
      <>
        <FOIHeader/>
        <div className="wrapper">
          
            <div className="container-fluid content main-container">
              <ToastContainer />
              <Switch>
               
                <Route path="/">
                <div><h3>Content Area!</h3></div>
                </Route>
              </Switch>
              
            </div>
        </div>
        <FOIFooter/>
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  