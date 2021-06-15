import React, { memo } from 'react';
import "./home.scss";
const Home = memo((props) => { 
    return (      
        <div className="home-page">
          <div className="rounded-rectangle">
            <div className="login-container">
              <h1 className="display-5">Welcome, Sign In</h1>
              <button className="btn btn-primary active">
                Log In
              </button>
            </div>
          </div>
                       
        </div>
    );
  });

export default Home;