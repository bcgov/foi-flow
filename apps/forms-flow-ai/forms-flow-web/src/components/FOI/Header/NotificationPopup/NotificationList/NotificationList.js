import React, {useState } from 'react';
import {useSelector, useDispatch } from "react-redux";
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import {addToFullnameList, getFullnameList } from '../../../../../helper/FOI/helper'
import {
  deleteFOINotifications
} from "../../../../../apiManager/services/FOI/foiNotificationServices";
import { useParams } from 'react-router-dom';
import {
  getBCgovCode
} from "../../../FOIRequest/utils";
import {
  fetchFOIRequestDetailsForNotification,
  fetchFOIRawRequestDetailsForNotification 
} from "../../../../../apiManager/services/FOI/foiRequestServices";

const NotificationList = (props) => {

  const dispatch = useDispatch();
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
      if (fullnameList && fullnameList !== null) {
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
        if (fullnameList && fullnameList !== null)
          return finduserbyuserid(userId)
      }
  }

  const dismissNotification = () => {
    let idNumber = notification.idnumber;
    idNumber+='';
    dispatch(deleteFOINotifications(idNumber.toLowerCase(), notification.notificationid,null));
  }

  const getStatusAndRedirect = () =>{
    if(notification.requesttype === 'rawrequest'){
      dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification))
    }
    else if(notification.requesttype === 'ministryrequest'){
      dispatch(fetchFOIRequestDetailsForNotification(notification.foirequestid,notification.requestid, notification));
    }
  }



  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <div className="redirect-url" onClick={getStatusAndRedirect}>{notification.idnumber}</div></h6>
        </Col>
        <Col className="close-btn-align" onClick={dismissNotification}>
          <i className="fa fa-times"></i>
        </Col>
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
