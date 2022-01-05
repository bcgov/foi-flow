import React, {useState } from 'react';
import {useSelector } from "react-redux";
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import {addToFullnameList, getFullnameList } from '../../../../../helper/FOI/helper'
// import {
//   deleteFOINotification
// } from "../../../../../apiManager/services/FOI/foiNotificationServices";
// import {useDispatch} from "react-redux";
import { useParams } from 'react-router-dom';
import {
  getBCgovCode
} from "../../../FOIRequest/utils";

const NotificationList = (props) => {
  let notification = props.notification;
  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  let requestDetails = useSelector(state => state.foiRequests.foiRequestDetail);
  
  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const {ministryId} = useParams();
  let bcgovcode = getBCgovCode(ministryId, requestDetails);


  const finduserbyuserid = (userId) => {
    let user = fullnameList.find(u => u.username === userId);
    return user && user.fullname ? user.fullname : userId;

  }
  const getfullName = (userId) => {
      if (fullnameList) {
        return finduserbyuserid(userId)
      } else {
        if (iaoassignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, "iao");
          setFullnameList(getFullnameList());
        }

        if (ministryAssignedToList.length > 0) {
          addToFullnameList(iaoassignedToList, bcgovcode);
          setFullnameList(getFullnameList());
        }

        return finduserbyuserid(userId)
      }
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
        <Col>{getfullName(notification.createdby)}</Col>
        <Col>{notification.created_at}</Col>
      </Row>
    </ListGroup.Item>
  );
}


export default NotificationList;
