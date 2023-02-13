import React, {useEffect}from "react";
import { Redirect, Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import { Dashboard, MinistryDashboard } from "./Dashboard";
import FOIRequest  from "./FOIRequest";
import MinistryReview from "./FOIRequest/MinistryReview/MinistryReview";
import { isMinistryLogin } from '../../helper/FOI/helper';
import UnAuthorized from "./UnAuthorized";


const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated); 


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
  if (Object.entries(userDetail).length !== 0) {
    const userGroups = userDetail && userDetail.groups.map(group => group.slice(1));
    isMinistry = isMinistryLogin(userGroups);
  }

  return (
      <>
        {isAuth && Object.entries(userDetail).length !== 0 ? (
          isAuthorized ? (
            <>
              <FOIHeader /> 
              <Route exact path="/foi/dashboard">
                {isMinistry ? 
                <MinistryDashboard userDetail={userDetail} />
                : <Dashboard userDetail={userDetail} />
                }
              </Route>
              <Route path="/foi/reviewrequest/:requestId">
                <FOIRequest userDetail={userDetail} />
              </Route>
              <Route path="/foi/addrequest">
                <FOIRequest  userDetail={userDetail}/>
              </Route>
              <Route path="/foi/foirequests/:requestId/ministryrequest/:ministryId">
                <FOIRequest userDetail={userDetail} />
              </Route>
              <Route path="/foi/ministryreview/:requestId/ministryrequest/:ministryId">
                <MinistryReview userDetail={userDetail} />
              </Route>
              <Route exact path={["/foi", "/foi/dashboard/"]}>
                <Redirect to="/foi/dashboard"/>
              </Route>
              <FOIFooter />
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
