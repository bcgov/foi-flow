import React from "react";
import "./homemenu.scss";

const HomeMenu = React.memo(() => {
  return (
      <div className="justify-content-between foi-menu-bar">
          <div className="row foi-menu-bar-panel">
        <div className="col-4 foi-home-menu">
            <a href="/foi/Dashboard" alt="Home" className="foi-home-link">
                Home
            </a>
        </div>
        <div className="col-4">
            <button type="button" className="foi-search-button">
                <span className="fa fa-search foi-search-icon"></span>
            </button>
        </div>
        </div>
      </div>
  );
});
export default HomeMenu;
