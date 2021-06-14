import React, { memo } from 'react';
import Button from '@material-ui/core/Button';
import "./home.scss";
const Home = memo((props) => { 
    return (      
        <div className="home-page">
          <div className="rounded-rectangle">
            <div className="login-container">
              <h1>Welcome, Sign In</h1>
              <button>
                Log In
              </button>
            </div>
          </div>
                       
        </div>
    );
  });

export default Home;