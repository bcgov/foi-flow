import React, { useEffect,useState } from "react";
import Badge from '@material-ui/core/Badge';
import {Navbar, Nav} from "react-bootstrap";
import {useDispatch, useSelector} from "react-redux";
import "./foiheader.scss";
import { Container } from "@material-ui/core";
import UserService from "../../../services/UserService";
import logo from "../../../assets/FOI/images/logo-banner.png";
import {push} from "connected-react-router";
import Popup from 'reactjs-popup';
import NotificationPopup from "./NotificationPopup/NotificationPopup";
import {
  fetchFOINotifications
} from "../../../apiManager/services/FOI/foiNotificationServices";

const FOIHeader = React.memo(() => { 

  const dispatch = useDispatch();
  const signout = () => {
    localStorage.removeItem('authToken');
    dispatch(push(`/`));
    UserService.userLogout();
}
const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
const user = useSelector((state) => state.user.userDetail);
const [screenPosition, setScreenPosition] = useState(0);
const [open, setOpen] = useState(false);
const closeModal = () => setOpen(false);
const openModal = (coordinates) => {
  const screenX = coordinates.pageX;
  setScreenPosition(screenX);
  console.log(screenX);
  setOpen(!open);
}

let foiNotifications = useSelector(state=> state.notifications.foiNotifications);

useEffect(() => {     
  if(isAuthenticated)
    dispatch(fetchFOINotifications());
  const fetchNotifications = () =>{
    dispatch(fetchFOINotifications());
  }
  setInterval(() => {
    fetchNotifications();
  }, 900000);
},[dispatch]);



const triggerPopup = () => {
  return(
    <> 
    <Badge badgeContent={foiNotifications?.length} color="secondary">
      <i style={{color: open? "#003366" : "white",cursor: "pointer"}} className="fa fa-bell-o foi-bell"></i>
    </Badge>
   </>
  )
}

  return (
    <div>
    <div className="row ">
    <Navbar collapseOnSelect fixed="top" expand="sm" bg="#036" variant="dark" style={{borderBottom: "2px solid #fcba19"}}>
      <Container className="foiContainer" style={{maxHeight: "45px"}}>
        <Nav className="ml-auto">  
        <div className="col-md-12 col-sm-12">
          <div className="col-md-3 col-sm-4 foiheaderLogosection">
          <a href="/foi/dashboard" alt="British Columbia">
              <img src={logo} alt="Go to the Government of British Columbia website" />
            </a>
          </div>
          <div className="col-md-3 col-sm-4 foiheaderAppNamesection">
          <h2>FOI</h2>
          </div>
            <div className="col-md-6 col-sm-4 foiheaderUserStatusSection">
          {isAuthenticated?
            <Navbar.Toggle aria-controls="responsive-navbar-nav" className="foiNavBarToggle" />
          :null}
          { isAuthenticated?
            <Navbar.Collapse id="responsive-navbar-nav">
              <Nav className="ml-auto">
                <div className="ml-auto banner-right foihamburgermenu">       
                  <ul className="navbar-nav foihamburgermenulist">
                      <li className="nav-item username foinavitem">
                          <span className="navbar-text">  {user.name || user.preferred_username || ""} </span>
                      </li>
                      <li className="bell-icon foinavitem" >
                      <div onClick={(e) => openModal(e)} className={`drawer-div ${open && 'notification-popup-drawer'}`}>
                        <Popup className="notification-popup" 
                        role='tooltip'
                        open={open} 
                        onClose={closeModal}
                        trigger={
                          triggerPopup
                        }
                        nested
                        closeOnDocumentClick 
                        contentStyle={{left: `${(screenPosition - 300)}px`}}
                        position={'bottom right'}
                        >
                        <NotificationPopup notifications={foiNotifications} ></NotificationPopup>
                        </Popup>
                      </div>
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
          </div>
      </Nav>      
    </Container>    
         </Navbar>   
      {/* {isAuthenticated ?  <HomeMenu /> : null} */}
         </div>
         </div>
  );
});
export default FOIHeader;
