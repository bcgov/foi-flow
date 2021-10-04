import React, {useEffect}from "react";
import { Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import { Dashboard, MinistryDashboard } from "./Dashboard";
import FOIRequest  from "./FOIRequest";
import { isMinistryLogin } from '../../helper/FOI/helper';

//import TabbedContainer from "./TabbedContainer/TabbedContainer";
const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated); 

  useEffect(()=>{
    console.log('authenticate')
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);
  const userDetail = useSelector(state=> state.user.userDetail); 
  let isMinistry = false;
  if (Object.entries(userDetail).length !== 0) {
    const userGroups = userDetail && userDetail.groups.map(group => group.slice(1));
    isMinistry = isMinistryLogin(userGroups);
}
  return (
      <>
        {isAuth ? (
          <>
          <FOIHeader /> 
          
            <Route exact path="/foi/dashboard">
              {isMinistry ? 
              <MinistryDashboard />
              : <Dashboard />
              }
              
            </Route>
            <Route path="/foi/reviewrequest/:requestId/:requestState">
              <FOIRequest  />
            </Route>
            <Route path="/foi/addrequest">
              <FOIRequest  />
            </Route>
            <Route path="/foi/foirequests/:requestId/ministryrequest/:ministryId/:requestState">
              <FOIRequest  />
            </Route>
           
            <FOIFooter />
            </>
         ) : (
          <Loading />
        )} 
      </>
    );
})

export default FOIAuthenticateRouting;
