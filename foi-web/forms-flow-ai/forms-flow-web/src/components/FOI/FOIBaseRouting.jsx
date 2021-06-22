import React from "react";
import { Route, Switch } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Home from "./Home";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import FOIAuthenticateRouting from "./FOIAuthenticateRouting";
import {useSelector} from "react-redux";

const FOIBaseRouting = React.memo(({store}) => {
  
  const isAuth = useSelector((state) => state.user.isAuthenticated);
  console.log("FOIBaseRouting "+ isAuth)
    return (
      <>
              
              <ToastContainer />
              <Switch>

                <Route path="/Dashboard">
                    <FOIAuthenticateRouting store={store} />
                </Route>
               
                <Route exact path="/">
                    <FOIHeader store={store}/> 
                    <Home store={store} />
                    <FOIFooter />
                </Route>

              </Switch>   
        
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  