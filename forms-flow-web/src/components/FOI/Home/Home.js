import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import {push} from "connected-react-router";
import {Redirect} from "react-router-dom";


import "./home.scss";
const Home = React.memo(() => {
  
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const isAuthorized = useSelector(state=> state.user.isAuthorized);
  const dispatch = useDispatch();
  const user = useSelector((state) => state.user.userDetail);
  const login = () => {
    dispatch(push(`/foi/dashboard`));
}
    return (      
      <div className="home-page">
        <div className="card rounded-rectangle foiroundedrectangle">
          <div className="card-body login-container">
            {isAuthenticated && user && isAuthorized ? 
              <Redirect to='/foi/dashboard' /> 
              : isAuthenticated && user && !isAuthorized ?
                <Redirect to='/foi' /> 
                : <div> <h1 className="card-title">Welcome, Sign In</h1> <button type="button" className="btn btn-primary foi-btn foibtn" onClick={login}>Log In</button> </div>}

          </div>
        </div>
      </div>
    );
  });

export default Home;