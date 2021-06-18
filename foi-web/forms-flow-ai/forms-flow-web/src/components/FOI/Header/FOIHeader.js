import React  from "react";
import Badge from '@material-ui/core/Badge';
import {Navbar, Nav} from "react-bootstrap";
import {useDispatch, useSelector} from "react-redux";
import "./foiheader.scss";
import { Container } from "@material-ui/core";
import UserService from "../../../services/UserService";
import logo from "../../../assets/FOI/images/logo-banner.png";
import {push} from "connected-react-router";

const FOIHeader = React.memo(() => {
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  //const isAuthenticated = true;
  const user = useSelector((state) => state.user.userDetail);
  const dispatch = useDispatch();
  
  const signout = () => {
    dispatch(push(`/`));
      UserService.userLogout(); 
}

  return (
    <Navbar collapseOnSelect fixed="top" expand="sm" bg="#036" variant="dark" style={{borderBottom: "2px solid #fcba19"}}>
      <Container className="foiContainer">
      <Nav className="ml-auto">  
       <div className="col-md-6">
         <div className="col-md-3 foiheaderLogosection">
         <a href="https://gov.bc.ca" alt="British Columbia">
            <img src={logo} alt="Go to the Government of British Columbia website" />
          </a>
         </div>
         <div className="col-md-3 foiheaderAppNamesection">
         <h2>FOI</h2>
         </div>
          
          
          </div>
          <div className="col-md-6">
        {isAuthenticated?
          <Navbar.Toggle aria-controls="responsive-navbar-nav" className="foiNavBarToggle" />
        :null}
        {isAuthenticated?
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="ml-auto">
              <div className="ml-auto banner-right foihamburgermenu">       
                <ul className="navbar-nav foihamburgermenulist">
                    <li className="nav-item username foinavitem">
                        <span className="navbar-text">  {user.name || user.preferred_username || ""} </span>
                    </li>
                    <li className="nav-item bell-icon foinavitem">
                    <Badge color="secondary" badgeContent=" " variant="dot">
                        <i className="fa fa-bell-o"></i>
                    </Badge>
                      
                    </li>
                    <li className="nav-item foinavitem">
                      <button type="button" className="btn btn-primary signout-btn" onClick={signout}>Sign Out</button>
                    </li>
                </ul>
              </div>
          </Nav>
          </Navbar.Collapse>       
        :null}
        </div>
    </Nav>
    </Container>
         </Navbar>   
   
  );
});
export default FOIHeader;
