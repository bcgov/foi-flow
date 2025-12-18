import React from "react";
import { Route, Switch } from "react-router-dom";
import {useSelector} from "react-redux";

import PublicRoute from "./PublicRoute";
import PrivateRoute from "./PrivateRoute";

import NavBar from "../containers/NavBar";
import Footer from "./Footer";
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
  privatestyle: {
    backgroundImage: "none !important",
  },
}));

const BaseRouting = React.memo(({store}) => {
  const isAuth = useSelector((state) => state.user.isAuthenticated);
  const classes = useStyles();
  const getStyle = () => {
    if (isAuth)
      return classes.privatestyle;
    return "";
  }

  return (
    <>
      {isAuth?<NavBar/>:null}
      <div className="wrapper" id="content" role="main" aria-label="main">
          <div className={`container-fluid content main-container ${getStyle()}`}>
            <ToastContainer />
            <Switch>
              <Route path="/public"><PublicRoute store={store}/></Route>
              <Route path="/">
                <PrivateRoute store={store} />
              </Route>
            </Switch>            
          </div>
      </div>
      {isAuth?<Footer />:null}
    </>
  );
});


export default BaseRouting;
