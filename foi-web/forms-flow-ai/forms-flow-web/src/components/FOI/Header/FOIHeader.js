import React from "react";
import "./foiheader.scss";
const FOIHeader = React.memo(() => {
  //const today = new Date();
  return (
      <header>
        <div className="offset-md-2 banner">
        <a href="https://gov.bc.ca" alt="British Columbia">
          <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
        </a>
        <h2>FOI</h2>        
    </div>
    </header>
  );
});
export default FOIHeader;
