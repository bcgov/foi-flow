import React, {useEffect} from 'react';
import { useDispatch, useSelector } from "react-redux";
import UserService from "../../../services/UserService";
import { setUserAuth } from "../../../actions/bpmActions";
import DashboardImage from "../../../assets/FOI/images/DashboardImage.PNG"

const Dashboard = React.memo((props) => { 
  const dispatch = useDispatch();
  useEffect(()=>{
    console.log(JSON.stringify(props.store));
    if(props.store){
      UserService.initKeycloak(props.store, (err, res) => {
        dispatch(setUserAuth(res.authenticated));
      });
    }
  },[props.store, dispatch]);


    return (      
        <div className="dashboard">
          <img src={DashboardImage} alt="Dashboard" />
        </div>
    );
  });

export default Dashboard;