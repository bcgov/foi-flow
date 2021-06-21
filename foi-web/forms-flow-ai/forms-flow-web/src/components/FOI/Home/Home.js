import React,  {useEffect} from 'react';
import {useDispatch, useSelector} from "react-redux";
import {push} from "connected-react-router";
import UserService from "../../../services/UserService";
import { setUserAuth } from "../../../actions/bpmActions";
import "./home.scss";
const Home = React.memo((props) => {
  let isAuth = false;

  const authToken = localStorage.getItem("authToken"); 
  
  if(authToken !== null && authToken !== '' && authToken !== undefined) {
    isAuth = true;
  }

  const dispatch = useDispatch();

  useEffect(()=>{
    if(props.store && isAuth){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);


  const user = useSelector((state) => state.user.userDetail);
  const login = () => {
    dispatch(push(`/Dashboard`));
}
    return (      
        <div className="home-page">         
          <div className="card rounded-rectangle foiroundedrectangle">     
            <div className="card-body login-container">
            {isAuth?<h1 className="card-title">Welcome {user.name || user.preferred_username || ""}</h1> : <div> <h1 className="card-title">Welcome, Sign In</h1> <button type="button" className="btn btn-primary login-btn foiLogin" onClick={login}>Log In</button> </div>}
              
            </div>
          </div>     
        </div>
    );
  });

export default Home;