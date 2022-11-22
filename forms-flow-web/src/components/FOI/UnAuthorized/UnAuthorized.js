import React from 'react';
import "../Home/home.scss";

const UnAuthorized = React.memo(() => {
  return (      
      <div className="home-page">
        <div className="card rounded-rectangle foiroundedrectangle">
          <div className="card-body login-container">
            <div> <h1 className="card-title">Unauthorized Access </h1> <h3> Please sign in with a valid account</h3> </div>
          </div>
        </div>
      </div>
  );
});

export default UnAuthorized;