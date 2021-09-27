import React, {useEffect}from "react";
import { Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import Dashboard from "./Dashboard";
import FOIRequest  from "./FOIRequest";
import { fetchFOIFullAssignedToList } from "../../apiManager/services/FOI/foiRequestServices";

//import TabbedContainer from "./TabbedContainer/TabbedContainer";
const FOIAuthenticateRouting = React.memo((props) => {
  const dispatch = useDispatch();
  const isAuth = useSelector((state) => state.user.isAuthenticated);
  const fullAssignedToList = useSelector((state) => state.foiRequests.foiFullAssignedToList);

  useEffect(()=>{
    console.log('authenticate')
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
    dispatch(fetchFOIFullAssignedToList());
  },[props.store, dispatch]);


  return (
      <>
        {isAuth ? (
          <>
          <FOIHeader /> 
          
            <Route exact path="/foi/dashboard">
              <Dashboard fullAssignedToList = {fullAssignedToList}/>
            </Route>
            <Route path="/foi/reviewrequest/:requestId">
              <FOIRequest  />
            </Route>
            <Route path="/foi/addrequest">
              <FOIRequest  />
            </Route>
            <Route path="/foi/foirequests/:requestId/ministryrequest/:ministryId">
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
