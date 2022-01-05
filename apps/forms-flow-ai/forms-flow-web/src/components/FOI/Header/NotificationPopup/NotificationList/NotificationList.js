import React from 'react';
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import { formatDate } from '../../../../../helper/FOI/helper'
// import {
//   deleteFOINotification
// } from "../../../../../apiManager/services/FOI/foiNotificationServices";
import {useDispatch} from "react-redux";


const NotificationList = (props) => {
  let notification = props.notification;
  //const dispatch = useDispatch();

  const formatNoticationDate = (creationDate) =>{
    return formatDate(creationDate, 'yyyy MMM dd | hh:mm a');  
  }
  //TODO : To be continued for dismiss
  // const dismissNotification = () => {
  //   dispatch(deleteFOINotification(notification.idnumber, notification.notificationid, {}));
  // }

  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <a>{notification.idnumber}</a></h6>
        </Col>
        {/*TODO : To be continued for dismiss: <Col className="close-btn-align" onClick={dismissNotification}>
        <i className="fa fa-times"></i>
        </Col> */}
      </Row>
      <div>
      {notification.notification}
      </div>
      <Row className="notification-item-footer">
        <Col>{notification.createdby}</Col>
        <Col>{formatNoticationDate(notification.created_at)}</Col>
      </Row>
    </ListGroup.Item>
  );
}


export default NotificationList;
