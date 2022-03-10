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
import { fetchFOINotifications } from "../../../apiManager/services/FOI/foiNotificationServices";
import { isMinistryLogin, getMinistryCode } from "../../../helper/FOI/helper";
import io from "socket.io-client";
import {
  SOCKETIO_CONNECT_URL,
  SOCKETIO_RECONNECTION_DELAY,
  SOCKETIO_RECONNECTION_DELAY_MAX,
} from "../../../constants/constants";
import { fetchFOIFullAssignedToList } from "../../../apiManager/services/FOI/foiMasterDataServices";

const FOIHeader = React.memo(({ unauthorized = false }) => {
  const dispatch = useDispatch();
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);
  const user = useSelector((state) => state.user.userDetail);
  let isMinistry = false;
  let ministryCode = "";
  const [screenPosition, setScreenPosition] = useState(0);
  const [open, setOpen] = useState(false);
  const closeModal = () => setOpen(false);
  const openModal = (coordinates) => {
    const screenX = coordinates.pageX;
    setScreenPosition(screenX);
    setOpen(!open);
  };
  const [messageData, setMessageData] = useState([]);
  let foiNotifications = useSelector(
    (state) => state.notifications.foiNotifications
  );
  const [socket, setSocket] = useState(null);

  const userGroups = user?.groups?.map((group) => group.slice(1));
  isMinistry = isMinistryLogin(userGroups);
  ministryCode = getMinistryCode(userGroups);

  useEffect(() => {
    if (!unauthorized && isAuthenticated) {
      dispatch(fetchFOIFullAssignedToList());
      dispatch(fetchFOINotifications());
      const options = {
        reconnectionDelay: SOCKETIO_RECONNECTION_DELAY
          ? SOCKETIO_RECONNECTION_DELAY
          : 20000,
        reconnectionDelayMax: SOCKETIO_RECONNECTION_DELAY_MAX
          ? SOCKETIO_RECONNECTION_DELAY_MAX
          : 30000,
        path: "/api/v1/socket.io",
        transports: ["websocket"],
        auth: { "x-jwt-token": UserService.getToken() },
      };
      setSocket(io.connect(SOCKETIO_CONNECT_URL, options));

      setInterval(() => {
        dispatch(fetchFOINotifications());
      }, 900000);
    }
  }, []);

useEffect(() => {     
  if(!unauthorized && isAuthenticated){
    dispatch(fetchFOIFullAssignedToList());
    dispatch(fetchFOINotifications());  
    console.log("Token for Socket:", UserService.getToken());
    const options = {
      reconnectionDelay:SOCKETIO_RECONNECTION_DELAY?SOCKETIO_RECONNECTION_DELAY:20000,
      reconnectionDelayMax:SOCKETIO_RECONNECTION_DELAY_MAX?SOCKETIO_RECONNECTION_DELAY_MAX :30000,
      path:'/api/v1/socket.io',
      transports: ['websocket'],
      auth: { "x-jwt-token": UserService.getToken() }
    };
    setSocket(io.connect(SOCKETIO_CONNECT_URL, options));
    //console.log("Socket Val after connect:", socket);
    setInterval(() => {
      dispatch(fetchFOINotifications());
    }, 900000);
  }
},[]);

console.log("Socket Value:", socket);

useEffect(() => {     
    socket?.on(user.preferred_username, data => {
     if(data.action === 'delete'){
      setMessageData((oldMessageData) => oldMessageData.filter((msg) => msg.notificationid !== data.notificationid))
     }
     else{
      setMessageData(oldMessageData => [data, ...oldMessageData])
     }
    });
  }, [socket]);

  useEffect(() => {
    if (foiNotifications) {
      setMessageData(foiNotifications);
    }
  }, [foiNotifications]);

  const signout = () => {
    socket?.disconnect();
    console.log("Socket Val after disconnect:", socket);
    localStorage.removeItem('authToken');
    dispatch(push(`/`));
    UserService.userLogout();
  };

  const triggerPopup = () => {
    return (
      <>
        <Badge badgeContent={messageData?.length} color="secondary">
          <i
            style={{ color: open ? "#003366" : "white", cursor: "pointer" }}
            className="fa fa-bell-o foi-bell"
          ></i>
        </Badge>
      </>
    );
  };

  return (
    <div>
      <div className="row ">
        <Navbar
          collapseOnSelect
          fixed="top"
          expand="sm"
          bg="#036"
          variant="dark"
          style={{ borderBottom: "2px solid #fcba19" }}
        >
          <Container className="foiContainer" style={{ maxHeight: "45px" }}>
            <Nav className="ml-auto">
              <div className="col-md-12 col-sm-12">
                <div className="col-md-3 col-sm-4 foiheaderLogosection">
                  <a href="/foi/dashboard" alt="British Columbia">
                    <img
                      src={logo}
                      alt="Go to the Government of British Columbia website"
                    />
                  </a>
                </div>
                <div className="col-md-3 col-sm-4 foiheaderAppNamesection">
                  <h2>FOI</h2>
                </div>
                <div className="col-md-6 col-sm-4 foiheaderUserStatusSection">
                  {isAuthenticated && (
                    <>
                      <Navbar.Toggle
                        aria-controls="responsive-navbar-nav"
                        className="foiNavBarToggle"
                      />
                      <Navbar.Collapse id="responsive-navbar-nav">
                        <Nav className="ml-auto">
                          <div className="ml-auto banner-right foihamburgermenu">
                            <ul className="navbar-nav foihamburgermenulist">
                              <li className="nav-item username foinavitem">
                                <span className="navbar-text">
                                  {" "}
                                  {user.name ||
                                    user.preferred_username ||
                                    ""}{" "}
                                </span>
                              </li>
                              <li className="bell-icon foinavitem">
                                <div
                                  onClick={(e) => openModal(e)}
                                  className={`drawer-div ${
                                    open && "notification-popup-drawer"
                                  }`}
                                >
                                  <Popup
                                    className="notification-popup"
                                    role="tooltip"
                                    open={open}
                                    onClose={closeModal}
                                    trigger={triggerPopup}
                                    nested
                                    closeOnDocumentClick
                                    contentStyle={{
                                      left: `${screenPosition - 300}px`,
                                    }}
                                    position={"bottom right"}
                                  >
                                    <NotificationPopup
                                      notifications={messageData}
                                      isMinistry={isMinistry}
                                      ministryCode={ministryCode}
                                    ></NotificationPopup>
                                  </Popup>
                                </div>
                              </li>
                              <li className="nav-item foinavitem">
                                <button
                                  type="button"
                                  className="btn btn-primary signout-btn"
                                  onClick={signout}
                                >
                                  Sign Out
                                </button>
                              </li>
                            </ul>
                          </div>
                        </Nav>
                      </Navbar.Collapse>
                    </>
                  )}
                </div>
              </div>
            </Nav>
          </Container>
        </Navbar>
      </div>
    </div>
  );
});
export default FOIHeader;
