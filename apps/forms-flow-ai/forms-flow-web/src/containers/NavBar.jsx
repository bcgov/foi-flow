import React from "react";
import {Navbar, Dropdown, Container, Nav, NavDropdown} from "react-bootstrap";
import {Link, useLocation} from "react-router-dom";
import {useDispatch, useSelector} from "react-redux";
import UserService from "../services/UserService";
import {getUserRoleName, getUserRolePermission, getUserInsightsPermission} from "../helper/user";

import "./styles.scss";
import {CLIENT, STAFF_REVIEWER, APPLICATION_NAME, STAFF_DESIGNER} from "../constants/constants";
import ServiceFlowFilterListDropDown from "../components/ServiceFlow/filter/ServiceTaskFilterListDropDown";
import {push} from "connected-react-router";

const NavBar = React.memo(() => {
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const location = useLocation();
  const { pathname } = location;
  const user = useSelector((state) => state.user.userDetail);
  const userRoles = useSelector((state) => state.user.roles);
  const showApplications= useSelector((state) => state.user.showApplications);
  const dispatch = useDispatch();
  const logoPath = "/logo.svg";
  const appName = APPLICATION_NAME;

  const logout = () => {
      dispatch(push(`/`));
      UserService.userLogout();
  }

  const goToTask = () => {
    dispatch(push(`/task`));
  }

  return (
    <header>
      <Navbar collapseOnSelect expand="lg" className="topheading-border-bottom" fixed="top">
        <Container fluid className="service-bc-navbar-background">
          {/*<Nav className="d-lg-none">
            <div className="mt-1" onClick={menuToggle}>
              <i className="fa fa-bars fa-lg"/>
            </div>
          </Nav>*/}
          <Navbar.Brand className="d-flex" >
            <Link to="/">
              <img
                className="img-fluid"
                src={logoPath}
                width="100px"
                min-width="87px"
                max-width="100px"
                max-height="55px"
                alt="Logo"
              />
            </Link>
            <div className="custom-app-name pl-2">{appName}</div>
          </Navbar.Brand>
         {/*
           <Navbar.Brand className="d-flex">
            <Link to="/">
                  <img
                    className="img-xs rounded-circle"
                    src="/assets/Images/user.svg"
                    alt="profile"
                  />
            </Link>
          </Navbar.Brand>*/}
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          {isAuthenticated?
            <Navbar.Collapse id="responsive-navbar-nav" className="navbar-nav">
            <Nav id="main-menu-nav" className="mr-auto">
              <Nav.Link eventKey="1" as={Link} to='/form'  className={`main-nav nav-item ${
                pathname.match(/^\/form/) ? "" : "inactive-tab"
              }`}>  
                <i
                  className={`fa fa-wpforms fa-lg
                      ${pathname.match(/^\/form/) ? "active-tab-text" : ""}
                  `}
                >
                </i>
                <span 
                  className={`tab-text-padding 
                              ${pathname.match(/^\/form/) ? "active-tab-text" : ""}`
                            }
                >
                  Forms
                </span>
              </Nav.Link>
              {(getUserRolePermission(userRoles, STAFF_DESIGNER)) ?
                (<Nav.Link eventKey="10" as={Link} to='/admin'  className={`main-nav nav-item ${
                  pathname.match(/^\/admin/) ? "" : "inactive-tab"
                }`}>
                  <i
                    className={`fa fa-list-alt fa-fw fa-lg
                        ${pathname.match(/^\/admin/) ? "active-tab-text" : ""}`
                    }
                  >
                  </i> 
                  <span 
                    className={`tab-text-padding 
                                ${pathname.match(/^\/admin/) ? "active-tab-text" : ""}`
                              }
                  >
                    Admin
                  </span>
                </Nav.Link>)
                :null
              }

              {showApplications?(getUserRolePermission(userRoles, STAFF_REVIEWER) ||  getUserRolePermission(userRoles, CLIENT)) ?
                <Nav.Link eventKey="2" as={Link} to='/application'  className={`main-nav nav-item ${
                  pathname.match(/^\/application/) ? "" : "inactive-tab"
                }`}> 
                  <img
                    className={`applications-icon-header
                                ${pathname.match(/^\/application/) ? "active-tab" : ""}
                                `}
                    src="/webfonts/fa-regular_list-alt.svg"
                    alt="Header Applications Icon"
                  /> 
                  <span
                    className={`tab-text-padding 
                    ${pathname.match(/^\/application/) ? "active-tab-text" : ""}`
                  }
                  >
                    Applications
                  </span>
                </Nav.Link>
                :
                null:
                null}

{/*              {getUserRolePermission(userRoles, STAFF_REVIEWER) ?
                <Nav.Link as={Link} to='/task'  className={`main-nav nav-item ${
                  pathname.match(/^\/task/) ? "active-tab" : ""
                }`}><i className="fa fa-list"/> Tasks</Nav.Link>
                :
                null}*/}

              {getUserRolePermission(userRoles, STAFF_REVIEWER) ?
                <NavDropdown
                  title={
                      <span className="white-text">
                        <img
                          className={`task-dropdown-icon
                                      ${pathname.match(/^\/task/) ? "active-tab-dropdown" : "inactive-tab"}`
                                    }
                          src="/webfonts/fa-solid_list.svg"
                          alt="Task Icon"
                        /> 
                        <span
                          className={`tab-text-padding 
                                    ${pathname.match(/^\/task/) ? "active-tab-text" : ""}
                          `}
                        >
                            Tasks
                        </span>
                      </span>
                  }
                  id="task-dropdown"
                  className={`main-nav nav-item taskDropdown
                            ${pathname.match(/^\/task/) ? "" : "inactive-tab"}`
                  }
                  onClick={goToTask}
                >
                  <ServiceFlowFilterListDropDown/>
              </NavDropdown>:null}

              {getUserRolePermission(userRoles, STAFF_REVIEWER) ?
                <NavDropdown 
                  title={
                  <span className="white-text">
                    <i 
                      class={`fa fa-tachometer fa-2 dashboard-icon-dropdown
                      ${pathname.match(/^\/metrics/) || pathname.match(/^\/insights/) ? "active-tab-text" : ""}
                      `}
                      aria-hidden="true"
                    >     
                    </i>
                    <span
                      className={`tab-text-padding 
                      ${pathname.match(/^\/metrics/) || pathname.match(/^\/insights/) ? "active-tab-text" : ""}
                          `}
                    >
                      Dashboards
                    </span>
                  </span>
                  }
                  id="dashboard-dropdown"
                  className={`main-nav nav-item 
                              ${pathname.match(/^\/metrics/) || pathname.match(/^\/insights/) ? "" : "inactive-tab-dropdown"}`
                  }
                >
                  <NavDropdown.Item
                    eventKey="3"
                    as={Link}
                    to='/metrics'
                    className={`main-nav nav-item 
                    ${pathname.match(/^\/metrics/) ? "dropdown-option-selected" : ""}`
                    }
                  >
                    <i
                      class={`fa fa-pie-chart dashboard-dropdown-options black-text
                      ${pathname.match(/^\/metrics/) ? "dropdown-option-selected" : ""}
                      `}
                      aria-hidden="true"
                    >
                    </i>
                    <span className={`${pathname.match(/^\/metrics/) ? "dropdown-option-selected" : "black-text"}`}>
                      Metrics
                    </span>
                  </NavDropdown.Item>
                  {
                    getUserInsightsPermission() &&
                    <NavDropdown.Item
                      eventKey="4"
                      as={Link} to='/insights'
                      className={`main-nav nav-item 
                      ${pathname.match(/^\/insights/) ? "dropdown-option-selected" : ""}
                      `}
                    >
                      <i
                        class={`fa fa-lightbulb-o dashboard-dropdown-options
                        ${pathname.match(/^\/insights/) ? "dropdown-option-selected" : "black-text"}
                        `}
                        aria-hidden="true"
                      ></i>
                      <span className={`${pathname.match(/^\/insights/) ? "dropdown-option-selected" : "black-text"}`}>
                        Insights
                      </span>
                    </NavDropdown.Item>
                  }
              </NavDropdown>:null}
            </Nav>
            <Nav className="ml-auto">
              <Dropdown alignRight>
                <Dropdown.Toggle id="dropdown-basic" as="div">
                  <span className="mr-1">
                      <img
                        className="img-xs rounded-circle"
                        src="/assets/Images/user.svg"
                        alt="profile"
                      />
                    </span>
                      <span id="username" className="d-none d-lg-inline-block">
                      {user?.name || user?.preferred_username || ""}
                  </span>
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item disabled eventKey="5"> {user?.name || user?.preferred_username || ""}<br/>
                    <i className="fa fa-users fa-fw"/>
                    <b>{getUserRoleName(userRoles)}</b></Dropdown.Item>
                  <Dropdown.Divider/>
                  <Dropdown.Item eventKey="6" as={Link} onClick ={logout}><i className="fa fa-sign-out fa-fw"/> Logout</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              </Nav>
          </Navbar.Collapse>:<Link to="/" className="btn btn-primary">Login</Link>}
        </Container>
      </Navbar>
    </header>
  );
})

export default NavBar;
