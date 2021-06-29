import React from "react";
import { Route, Switch } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";

import FOIAuthenticateRouting from "./FOIAuthenticateRouting";
import FOIUnAuthenticateRouting from "./FOIUnAuthenticateRouting";

const FOIBaseRouting = React.memo(({store}) => {
    return (
      <>
              
              <ToastContainer />
              <Switch>

                <Route path="/foi">
                    <FOIAuthenticateRouting store={store} />
                </Route>
               
                <Route exact path="/">                   
                    <FOIUnAuthenticateRouting store={store}/>
                </Route>

              </Switch>   
        
      </>
    );
  });
  
  
  export default FOIBaseRouting;
  