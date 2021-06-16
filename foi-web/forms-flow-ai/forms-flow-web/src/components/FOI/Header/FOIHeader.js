import React from "react";
import Badge from '@material-ui/core/Badge';
import {Navbar, Nav} from "react-bootstrap";
import {useSelector} from "react-redux";
import "./foiheader.scss";
import { Container } from "@material-ui/core";
const FOIHeader = React.memo(() => {
  //const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const isAuthenticated = true;  
  return (
    <Navbar collapseOnSelect fixed="top" expand="sm" bg="#036" variant="dark">
      <Container>
      <Nav className="ml-auto">   
          <a href="https://gov.bc.ca" alt="British Columbia">
            <img src="FOI/assets/Images/logo-banner.png" alt="Go to the Government of British Columbia website" />
          </a>
          <h2>FOI</h2>
        {isAuthenticated?
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        :null}
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
    </Nav>
    </Container>
         </Navbar>   
   
  );
});
export default FOIHeader;
