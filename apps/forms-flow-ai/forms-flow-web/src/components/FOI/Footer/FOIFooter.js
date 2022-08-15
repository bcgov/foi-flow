import React from "react";
import "./FOIFooter.scss"

import {Navbar, Nav} from "react-bootstrap";
import { Container } from "@material-ui/core";


const FOIFooter = React.memo(() => {  
  return (
  <div className="footerstyle">
    <div className="row ">

      <Navbar collapseOnSelect  expand="sm" bg="#036" variant="dark" style={{borderTop: "2px solid #fcba19"}} className="foi-footer-nav">
        <Container className="foiContainer">
          <Nav className="ml-auto">
            
            <div className="col-md-3">
              <ul>
                <li><a href="#">Help</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
            </div>            
            <div className="col-md-3">
              <ul>
                  <li><a href="#">Disclaimer</a></li>
                  <li><a href="#">Privacy</a></li>
              </ul>
            </div>
			<div className="col-md-3">
              <ul>
                  <li><a href="#">Accessibility</a></li>
                  <li><a href="#">Copyright</a></li>
              </ul>
            </div>
          </Nav>
        </Container>
      </Navbar>

    </div>      
  </div>
  );
});
export default FOIFooter;
