import React from "react";
import { Route, Switch } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Home from "./Home";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import FOIAuthenticateRouting from "./FOIAuthenticateRouting";


const FOIBaseRouting = React.memo(({store}) => {
  
    return (
      <>
              
              <ToastContainer />
              <Switch>

                <Route path="/Dashboard">
                    <FOIAuthenticateRouting store={store} />
                </Route>
               
                <Route exact path="/">
                    <FOIHeader /> 
                    <Home />
                    <FOIFooter />
                </Route>

              </Switch>   
        
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  