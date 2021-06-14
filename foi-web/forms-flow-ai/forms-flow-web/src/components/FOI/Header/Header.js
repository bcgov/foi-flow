import React from "react";
import "./header.scss";
const Header = React.memo(() => {
  //const today = new Date();
  return (
      <header>
        <div className="offset-md-1 banner">
        <a href="https://gov.bc.ca" alt="British Columbia">
          <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
        </a>
        <h2>FOI</h2>        
    </div>
    <div className="other">   
      &nbsp;
    </div>
    </header>
  );
});
export default Header;
