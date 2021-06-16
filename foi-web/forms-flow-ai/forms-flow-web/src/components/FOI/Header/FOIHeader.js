import React from "react";
import Badge from '@material-ui/core/Badge';
import {Navbar, Nav} from "react-bootstrap";
import {useSelector} from "react-redux";
import "./foiheader.scss";
import { Container } from "@material-ui/core";
const FOIHeader = React.memo(() => {
  //const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const isAuthenticated = true;
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
    <Navbar collapseOnSelect fixed="top" expand="sm" bg="#036" variant="dark">
      <Container>
      <Nav className="ml-auto">
    {/* <nav className="navbar navbar-expand-lg navbar-light"> */}
        {/* <div className="offset-md-2 banner-left"> */}
          <a href="https://gov.bc.ca" alt="British Columbia">
            <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
          </a>
          <h2>FOI</h2>
        {/* </div> */}
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        {isAuthenticated?
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="ml-auto">
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
        </Nav>
        </Navbar.Collapse>
       
        :null}
           
    {/* </nav> */}
    </Nav>
    </Container>
         </Navbar>   
   
  );
});
export default FOIHeader;
