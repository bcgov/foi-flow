import React from "react";
import "./FOIFooter.scss"




const FOIFooter = React.memo(() => {  
  return (
    <div className="footerstyle">
    <div className="row ">
        <div className="col-md-3 offset-md-2">

          <ul>
            <li><a href="#">Help</a></li>
            <li><a href="#">Contact</a></li>
          </ul>

        </div>
        <div className="col-md-3">
        <ul>
            <li><a href="#">Disclaimer</a></li>
            <li><a href="#">Privacy</a></li>
            <li><a href="#">Accessibility</a></li>
            <li><a href="#">Copyright</a></li>
        </ul>

        </div>
    </div>
    </div>
  );
});
export default FOIFooter;
