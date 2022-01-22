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
import { StateEnum } from '../../../../../constants/FOI/statusEnum';

const NotificationList = ({notification}) => {

  const dispatch = useDispatch();
  let iaoassignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);
  let ministryAssignedToList = useSelector(state => state.foiRequests.foiMinistryAssignedToList);
  let requestDetails = useSelector(state => state.foiRequests.foiRequestDetail);
  const userDetail = useSelector(state=> state.user.userDetail);
  const [openModal, setModal] = useState(false);
  const [ministryCanvassedModal, setMinistryCanvassedModal] = useState(false);
  const [selectedMinistries,setSelectedMinistries]=useState([]);
  let isMinistry = false;
  let requestState = "";

  if (Object.entries(userDetail).length !== 0) {
    const userGroups = userDetail && userDetail.groups?.map(group => group.slice(1));
    isMinistry = isMinistryLogin(userGroups);
  }

  useEffect(() => {     
    console.log("Inside Useeffect!!");
    if(ministryCanvassedModal){
      console.log("Inside ministryCanvassedModal!!");
      if(notification.requesttype === 'rawrequest'){
        dispatch(fetchFOIRawRequestDetailsForNotification(notification, (err, res) => {
          if (!err && res) {
            getStatusAndRedirect(res);
          }
        }));
      }
      else if(notification.requesttype === 'ministryrequest'){
        dispatch(fetchFOIRequestDetailsForNotification(notification, isMinistry, (err,res) => {
        if (!err && res) {
          getStatusAndRedirect(res);
        }
        }));
      }
  }
  },[ministryCanvassedModal]);

  const [fullnameList, setFullnameList] = useState(getFullnameList);
  const {ministryId} = useParams();
  let bcgovcode = getBCgovCode(ministryId, requestDetails);

  const getStatusAndRedirect = (requestDetails) => {
    Object.entries(StateEnum).forEach(([key, value]) =>{
      if(key && value.id === requestDetails.requeststatusid){
        requestState = value.name;
      }
    })
    
    if(requestState === 'Archived' && requestDetails?.selectedMinistries?.length > 0){
      setSelectedMinistries(requestDetails.openedMinistries);
      setModal(true);
      setMinistryCanvassedModal(false);
    }
    else{
      setRedirectUrl(requestState);
      setMinistryCanvassedModal(false);
    }
  }

  const setRedirectUrl = (requestState) =>{
    let url = "";
    if(notification.requesttype === 'rawrequest'){
      url=`/foi/reviewrequest/${notification.requestid}/${requestState}`;
    }
    else if(notification.requesttype === 'ministryrequest'){
      if(isMinistry)
        url = `/foi/ministryreview/${notification.foirequestid}/ministryrequest/${notification.requestid}/${requestState}`;
      else
        url = `/foi/foirequests/${notification.foirequestid}/ministryrequest/${notification.requestid}/${requestState}`;
    }
    window.location.href=url;
  }

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


  return(
    <ListGroup.Item>
      <Row>
        <Col>
          <h6 className="notification-heading">
            <div className="redirect-url" onClick={() => setMinistryCanvassedModal(true)}>{notification.idnumber}</div></h6>
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
