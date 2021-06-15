import React, { memo } from 'react';
import "./home.scss";
const Home = memo((props) => { 
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
          <div className="card rounded-rectangle">     
            <div className="card-body login-container">
              <h1 className="card-title">Welcome, Sign In</h1>
              <button type="button" className="btn btn-primary login-btn">Log In</button>
            </div>
          </div>     
        </div>
    );
  });

export default Home;