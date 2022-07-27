import React, {useEffect}from "react";
import { Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import "semantic-ui-css/semantic.min.css";

import UserService from "../../services/UserService";
import { setUserAuth } from "../../actions/bpmActions";
import Loading from "../../containers/Loading";
import FOIHeader from "./Header";
import FOIFooter from "./Footer";
import UnAuthorized from "./UnAuthorized";
import AttachmentViewer from "./customComponents/AttachmentViewer"


const FOIDocumentViewRouting = React.memo((props) => {
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

  const queryParams = new URLSearchParams(window.location.search);
  const _filepath = queryParams.get('filepath');

  const renderViewer =()=>{

    if(isAuthorized)
    {
      return (
        <>                          
              <Route path="/foidocument">
                <AttachmentViewer filepath={_filepath} />
              </Route>
             
            </>
      );
    }

    return ( <Route path="/foidocument">
    <FOIHeader  unauthorized={true}/> 
    <UnAuthorized />
    <FOIFooter />
  </Route>);
    
  }

  return (
      <>
        {isAuth && Object.entries(userDetail).length !== 0 ? (
          renderViewer()
        ) : (
          <Loading />
        )} 
      </>
    );
})

export default FOIDocumentViewRouting;
