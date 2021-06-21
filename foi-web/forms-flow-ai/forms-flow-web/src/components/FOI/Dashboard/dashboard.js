import React from 'react';
import {useSelector} from "react-redux";
// import DashboardImage from "../../../assets/FOI/images/DashboardImage.PNG"

const Dashboard = React.memo(() => {
  
  const user = useSelector((state) => state.user.userDetail);

     return (      
        <div className="dashboard">
          <span>Welcome {user.name || user.preferred_username || ""} !!!</span>
        </div>
    );
  });

export default Dashboard;