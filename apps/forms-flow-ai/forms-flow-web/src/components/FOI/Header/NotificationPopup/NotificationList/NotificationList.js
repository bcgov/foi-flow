import React from 'react';
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import { formatDate } from '../../../../../helper/FOI/helper'
import {
  deleteFOINotification
} from "../../../../../apiManager/services/FOI/foiRequestServices";
import {useDispatch} from "react-redux";


const NotificationList = (props) => {
  let notification = props.notification;
  const dispatch = useDispatch();

  const formatNoticationDate = (creationDate) =>{
    return formatDate(creationDate, 'yyyy MMM dd | hh:mm a');  
  }
  const dismissNotification = () => {
    dispatch(deleteFOINotification(notification.idnumber, notification.notificationid, {}));
  }

  const redirectUrl = () => {
    let url = "";
    if(notification.type === 'rawRequest')
       url =window.location.href+"/foi/reviewrequest/"+notification.rawRequestId/notification.requestState;
    else if(notification.type === 'ministryRequest'){
       url = window.location.href+'/foi/foirequests/'+notification.requestId+'/ministryrequest/'+notification.ministryRequestId/notification.requestState;
    }
     return url;
  }

  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <a className="redirect-link" href={redirectUrl()}>{notification.idnumber}</a></h6>
        </Col>
        <Col className="close-btn-align" onClick={dismissNotification}>
        <i className="fa fa-times"></i>
        </Col>
      </Row>
      {/* <div style={{fontSize:"16px"}}>New Comment:
      </div> */}
      <div>
      {notification.notification}
      </div>
      <Row className="notification-item-footer">
        <Col>{notification.createdby}</Col>
        <Col>{formatNoticationDate(notification.created_at)}</Col>
        {/* <Col>2021 Dec 06 | HH:MM AM/PM</Col> */}
      </Row>
    </ListGroup.Item>
  );
}


export default NotificationList;
