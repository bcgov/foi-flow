import React, {useState,useEffect } from 'react';
import {useSelector, useDispatch } from "react-redux";
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import {addToFullnameList, getFullnameList, isMinistryLogin } from '../../../../../helper/FOI/helper'
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
import MinistriesCanvassed from '../../../customComponents/MinistriesCanvassed/MinistriesCanvassed';


const NotificationList = ({notification, setOpen}) => {

  const dispatch = useDispatch();
  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  let requestDetails = useSelector(state => state.foiRequests.foiRequestDetail);
  const userDetail = useSelector(state=> state.user.userDetail);
  let isMinistry = false;
  const [openModal, setModal] = useState(false);
  const [ministryCanvassedModal, setMinistryCanvassedModal] = useState(false);
  //let ministriesCanvassed = true;
  const [selectedMinistries,setSelectedMinistries]=useState([]);
  
  if (Object.entries(userDetail).length !== 0) {
    const userGroups = userDetail && userDetail.groups?.map(group => group.slice(1));
    isMinistry = isMinistryLogin(userGroups);
  }

    useEffect(() => {     
      if(openModal){
      dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification, (err, res) => {
        if (!err && res) {
          if(res && res.selectedMinistries?.length > 0){
            setSelectedMinistries(res.selectedMinistries);
            setModal(true);
            //setOpen(false);
          }
        }
      }));
    }
      // return () => { setModal(true) };
    },[ministryCanvassedModal]);

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
    let idNumber = notification.idnumber;
    idNumber+='';
    let requestIdStart = idNumber.substring(0, idNumber.indexOf("-"));
    if(requestIdStart === 'U' )
    //&& notification.notification.toLowerCase === "moved to open state")
    {
      setMinistryCanvassedModal(true);
      setModal(true);
    }
  //   //  ministriesCanvassed = true;
    // setModal2Visible(true)
    // setModal(true);
    // dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification, ministriesCanvassed));
    // setTimeout(() => {
    //   if(requestDetails && requestDetails.selectedMinistries?.length > 0){
    //     setSelectedMinistries(requestDetails.selectedMinistries);
    //     setModal2Visible(true);
    //     setModal(true);
    //   }
    // }
    // , 5000);
    // dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification, (err, res) => {
    //   if (!err && res) {
    //     if(requestDetails && requestDetails.selectedMinistries?.length > 0){
    //       setSelectedMinistries(requestDetails.selectedMinistries);
    //       setModal(true);
    //     }
    //   }
    // }));
  }

// const getStatusAndRedirect = () =>{

  //   let idNumber = notification.idnumber;
  //   idNumber+='';
  //   let requestIdStart = idNumber.substring(0, idNumber.indexOf("-"));
  //   ministriesCanvassed = true;
  //   dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification, 
  //     ministriesCanvassed, (err, res) => {
  //     if(requestDetails && requestDetails.selectedMinistries?.length > 0){
  //       setSelectedMinistries(requestDetails.selectedMinistries);
  //       setModal2Visible(true);
  //     }
  //   }));

  //   //  if(requestIdStart === 'U' && notification.notification.toLowerCase === "moved to open state")
  //   //  ministriesCanvassed = true;
  //   // else if(notification.requesttype === 'rawrequest'){
  //   //   dispatch(fetchFOIRawRequestDetailsForNotification(notification.requestid, notification, ministriesCanvassed))
  //   // }
  //   // else if(notification.requesttype === 'ministryrequest'){
  //   //   dispatch(fetchFOIRequestDetailsForNotification(notification.foirequestid,notification.requestid, notification, isMinistry, ministriesCanvassed));
  //   // }
  // }

  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <div className="redirect-url" onClick={() => getStatusAndRedirect()}>{notification.idnumber}</div></h6>
            {openModal && 
            <MinistriesCanvassed  openModal={openModal} selectedMinistries={selectedMinistries} setModal={setModal}/>
            }
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
