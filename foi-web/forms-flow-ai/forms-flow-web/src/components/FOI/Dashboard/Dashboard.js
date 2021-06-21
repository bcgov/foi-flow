import React from 'react';
import {useSelector} from "react-redux";
import "./dashboard.scss";
const Dashboard = React.memo(() => {
  
  const user = useSelector((state) => state.user.userDetail);

     return (      
        <div className="foidashboard">
          <span>Welcome {user.name || user.preferred_username || ""} !!!</span>
        </div>
    );
  });

export default Dashboard;