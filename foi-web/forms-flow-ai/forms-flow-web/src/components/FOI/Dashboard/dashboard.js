import React from 'react';
import DashboardImage from "../../../assets/FOI/images/DashboardImage.PNG"

const Dashboard = React.memo(() => { 
     return (      
        <div className="dashboard">
          <img src={DashboardImage} alt="Dashboard" />
        </div>
    );
  });

export default Dashboard;