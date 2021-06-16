import React from "react";
import Badge from '@material-ui/core/Badge';
import {useSelector} from "react-redux";
import "./foiheader.scss";
const FOIHeader = React.memo(() => {
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  //const isAuthenticated = true;
  //const today = new Date();
   {/* <header>
        <div className="offset-md-2 banner">
        <a href="https://gov.bc.ca" alt="British Columbia">
          <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
        </a>
        <h2>FOI</h2>        
    </div>
    </header> */}
  return (
    <nav className="navbar navbar-expand-lg navbar-light">
        <div className="offset-md-2 banner-left">
          <a href="https://gov.bc.ca" alt="British Columbia">
            <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
          </a>
          <h2>FOI</h2>
        </div>
        {isAuthenticated?
        <div className="ml-auto banner-right">       
        <ul className="navbar-nav ">
            <li className="nav-item username">
                <span className="navbar-text"> Username </span>
            </li>
            <li className="nav-item bell-icon">
            <Badge color="secondary" badgeContent=" " variant="dot">
                <i className="fa fa-bell-o"></i>
            </Badge>
              
            </li>
            <li className="nav-item">
              <button type="button" className="btn btn-primary signout-btn">Sign Out</button>
            </li>
        </ul>
        </div>
        :null}          
    </nav>
   
  );
});
export default FOIHeader;
