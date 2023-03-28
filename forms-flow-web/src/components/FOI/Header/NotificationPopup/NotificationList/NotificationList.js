import React, {useState} from 'react';
import {useSelector, useDispatch } from "react-redux";
import { Col, Row, ListGroup } from 'react-bootstrap';
import './notificationlist.scss';
import {addToFullnameList, getFullnameList} from '../../../../../helper/FOI/helper'
import {
  deleteFOINotifications
} from "../../../../../apiManager/services/FOI/foiNotificationServices";
import {
  fetchOpenedMinistriesForNotification
} from "../../../../../apiManager/services/FOI/foiRequestServices";
import MinistriesCanvassed from '../../../customComponents/MinistriesCanvassed/MinistriesCanvassed';

const NotificationList = ({notification, isMinistry, ministryCode}) => {

  const dispatch = useDispatch();
  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  const [openModal, setModal] = useState(false);
  const [selectedMinistries,setSelectedMinistries]=useState([]);
  const [fullnameList, setFullnameList] = useState(getFullnameList);


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
        addToFullnameList(iaoassignedToList, ministryCode);
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

  const handleClick = (notificationVal) => {

    if(checkCommentType(notificationVal.notificationtype)){
      setCommentUrl();
    }
    else if(notificationVal.requesttype === 'rawrequest' && 
     notification.notification.toLowerCase() === "moved to open state"){
        dispatch(fetchOpenedMinistriesForNotification(notificationVal, (err, res) => {
            getStatusAndRedirect(err, res);
        }));
    }
    else if (checkPDFStitchType(notificationVal.notificationtype)) {
      setRecordsUrl();
    }
    else{
      setRedirectUrl();
    }
  }

  const checkCommentType = (type) => {
    return !!(type === 'New User Comments' || type === 'Reply User Comments' ||
      type === 'Tagged User Comments');
  }

  const checkPDFStitchType = (type) => {
    return !!(type === 'PDFStitch');
  }

  const commentTitle = (type) => {
    if(type === "New User Comments")
      return "New Comment:";
    else if(type === "Tagged User Comments")
      return "You've been tagged in a comment:";
    else
      return "New Reply to Your comment:";
  }

  const commentText = (message) => {
    if(message.length > 90)
      return `"`+message.substring(0, 90)+`..."`;
    else
      return `"`+message+`"`;
   }

  const getStatusAndRedirect = (err, res) => {
    if (!err && res) {
      if(res?.openedMinistries?.length > 0){
        setSelectedMinistries(res.openedMinistries);
        setModal(true);
      }
      else{
        setRedirectUrl();
      }
    }
  }

  const setRedirectUrl = () =>{
    let url = "";
    if(notification.requesttype === 'rawrequest'){
      url=`/foi/reviewrequest/${notification.requestid}`;
    }
    else if(notification.requesttype === 'ministryrequest'){
      if(isMinistry)
        url = `/foi/ministryreview/${notification.foirequestid}/ministryrequest/${notification.requestid}`;
      else
        url = `/foi/foirequests/${notification.foirequestid}/ministryrequest/${notification.requestid}`;
    }
    window.location.href=url;
  }

  const setCommentUrl = () =>{
    let url = "";
    if(notification.requesttype === 'rawrequest'){
      url=`/foi/reviewrequest/${notification.requestid}/comments`;
    }
    else if(notification.requesttype === 'ministryrequest'){
      if(isMinistry)
        url = `/foi/ministryreview/${notification.foirequestid}/ministryrequest/${notification.requestid}/comments`;
      else
        url = `/foi/foirequests/${notification.foirequestid}/ministryrequest/${notification.requestid}/comments`;
    }
    window.location.href=url;
  }

  const setRecordsUrl = () =>{
    let url = "";    
    if(isMinistry)
      url = `/foi/ministryreview/${notification.foirequestid}/ministryrequest/${notification.requestid}/records`;
    else
      url = `/foi/foirequests/${notification.foirequestid}/ministryrequest/${notification.requestid}/records`;
    window.location.href=url;
  }


  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <div className="redirect-url" onClick={() => handleClick(notification)}>{notification.axisnumber}</div></h6>
            {openModal && 
            <MinistriesCanvassed  openModal={openModal} selectedMinistries={selectedMinistries} setModal={setModal}/>
            }
        </Col>
        <Col className="close-btn-align" onClick={dismissNotification}>
          <i className="fa fa-times"></i>
        </Col>
      </Row>
      { checkCommentType(notification.notificationtype) ?
      <>
        <div style={{fontSize:"16px"}}>{commentTitle(notification.notificationtype)}</div> 
        <div style={{fontStyle: "italic"}} >
          {commentText(notification.notification)}
        </div>
      </> 
        :
        <div>
          {notification.notification}
        </div>
      }        
      
      <Row className="notification-item-footer">
        <Col>{getfullName(notification.createdby)}</Col>
        <Col>{notification.created_at}</Col>
      </Row>
    </ListGroup.Item>
  );
}


export default NotificationList;
