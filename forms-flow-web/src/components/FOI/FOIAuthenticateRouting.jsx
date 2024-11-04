import React, {useEffect, useState}from "react";
import { Redirect, Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import { Dashboard, MinistryDashboard, OIDashboard } from "./Dashboard";
import FOIRequest  from "./FOIRequest";
import MinistryReview from "./FOIRequest/MinistryReview/MinistryReview";
import { isMinistryLogin } from '../../helper/FOI/helper';
//import { isMinistryLogin, isOITeam } from '../../helper/FOI/helper';
import UnAuthorized from "./UnAuthorized";
import Admin from "./Admin";
import Divisions from "./Admin/Divisions";
import ApplicantProfileModal from "./FOIRequest/ApplicantProfileModal";


const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated); 

  
  const [applicantProfileModalOpen, setApplicantProfileModalOpen] = useState(false);
  const handleApplicantModalClose = () => {
    setApplicantProfileModalOpen(false);
  }
  const openApplicantProfileModal = () => {
    setApplicantProfileModalOpen(true);
  }

  useEffect(()=>{
    console.log('authenticate')
    if(props.store){
      UserService.initKeycloak(props.store, (_err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);
  const userDetail = useSelector(state=> state.user.userDetail);
  const isAuthorized = useSelector(state=> state.user.isAuthorized);

  let isMinistry = false;
  //let isOITeam = false;
  if (Object.entries(userDetail).length !== 0) {
    const userGroups = userDetail && userDetail.groups.map(group => group.slice(1));
    isMinistry = isMinistryLogin(userGroups);
    //isOITeam = isOITeamLogin(userGroups);
  }
  console.log("isMinistry : ",isMinistry)
  //console.log("isOITeam : ",isOITeam)
  return (
      <>
        {isAuth && Object.entries(userDetail).length !== 0 ? (
          isAuthorized ? (
            <>
              <FOIHeader /> 
              <Route exact path="/foi/dashboard">
                  {/* {isOITeam ? (
                  <OIDashboard userDetail={userDetail} />
                  ) : isMinistry ? (
                  <MinistryDashboard userDetail={userDetail} />
                  ) : (
                  <Dashboard userDetail={userDetail} />
                  )} */}
                  {isMinistry ? (
                  <MinistryDashboard userDetail={userDetail} />
                  ) : (
                  <Dashboard userDetail={userDetail} />
                  )}
              </Route>
              <Route path="/foi/reviewrequest/:requestId">
                <FOIRequest userDetail={userDetail} openApplicantProfileModal={openApplicantProfileModal} />
              </Route>
              <Route path="/foi/addrequest">
                <FOIRequest  userDetail={userDetail} openApplicantProfileModal={openApplicantProfileModal}/>
              </Route>
              <Route path="/foi/foirequests/:requestId/ministryrequest/:ministryId">
                <FOIRequest userDetail={userDetail} openApplicantProfileModal={openApplicantProfileModal}/>
              </Route>
              <Route path="/foi/ministryreview/:requestId/ministryrequest/:ministryId">
                <MinistryReview userDetail={userDetail} />
              </Route>
              <Route path="/foi/admin/divisions">
                <Divisions userDetail={userDetail} />
              </Route>
              <Route path="/foi/admin">
                <Admin userDetail={userDetail} />
              </Route>
              <Route exact path={["/foi", "/foi/dashboard/"]}>
                <Redirect to="/foi/dashboard"/>
              </Route>
              <FOIFooter />
              <ApplicantProfileModal
                modalOpen={applicantProfileModalOpen}
                handleModalClose={handleApplicantModalClose}
              />
            </>
          ) : (
            <Route path="/foi">
              <FOIHeader  unauthorized={true}/> 
              <UnAuthorized />
              <FOIFooter />
            </Route>
          )
        ) : (
          <Loading />
        )} 
      </>
    );
})

export default FOIAuthenticateRouting;
