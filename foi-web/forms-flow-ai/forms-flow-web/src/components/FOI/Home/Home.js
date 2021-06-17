import React, { memo } from 'react';
import {useDispatch} from "react-redux";
import {push} from "connected-react-router";
import "./home.scss";
const Home = memo((props) => {
  const dispatch = useDispatch();
  const login = () => {
    dispatch(push(`/Dashboard`));
}
    return (      
        <div className="home-page">
          {/* <div className="rounded-rectangle">
            <div className="login-container">
              <h1 className="display-5">Welcome, Sign In</h1>
              <button className="btn btn-primary active">
                Log In
              </button>
            </div>
          </div> */}
          <div className="card rounded-rectangle foiroundedrectangle">     
            <div className="card-body login-container">
              <h1 className="card-title">Welcome, Sign In</h1>
              <button type="button" className="btn btn-primary login-btn foiLogin" onClick={login}>Log In</button>
            </div>
          </div>     
        </div>
    );
  });

export default Home;