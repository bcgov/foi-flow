import React, {useEffect} from 'react';
import { useDispatch, useSelector } from "react-redux";
import UserService from "../../../services/UserService";
import { setUserAuth } from "../../../actions/bpmActions";

const Dashboard = React.memo((props) => { 
  const dispatch = useDispatch();
  useEffect(()=>{
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);


    return (      
        <div class="row">This is the Dashboard!</div>
    );
  });

export default Dashboard;