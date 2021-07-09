import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import {push} from "connected-react-router";

import "./home.scss";
const Home = React.memo(() => {
  
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const dispatch = useDispatch();
  const user = useSelector((state) => state.user.userDetail);
  const login = () => {
    dispatch(push(`/foi/dashboard`));
}
    return (      
        <div className="home-page">         
          <div className="card rounded-rectangle foiroundedrectangle">     
            <div className="card-body login-container">
            {isAuthenticated?<h1 className="card-title">Welcome {user.name || user.preferred_username || ""}</h1> : <div> <h1 className="card-title">Welcome, Sign In</h1> <button type="button" className="btn btn-primary login-btn foiLogin" onClick={login}>Log In</button> </div>}
              
            </div>
          </div>     
        </div>
    );
  });

export default Home;