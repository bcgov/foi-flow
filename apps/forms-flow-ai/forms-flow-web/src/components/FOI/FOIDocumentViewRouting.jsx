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
  useEffect(()=>{  
    let _store =  props.store;
    if(_store){
      UserService.initKeycloak(_store, (_err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);

  const _userDetail = useSelector(state=> state.user.userDetail);
  const _isAuthorized = useSelector(state=> state.user.isAuthorized);
  const _isAuth = useSelector((state) => state.user.isAuthenticated); 
  const _queryParams = new URLSearchParams(window.location.search);
  const _filepath = _queryParams.get('filepath');

  const renderViewer =()=>{

    if(_isAuthorized)
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
        {_isAuth && Object.entries(_userDetail).length !== 0 ? (
          renderViewer()
        ) : (
          <Loading />
        )} 
      </>
    );
})

export default FOIDocumentViewRouting;
