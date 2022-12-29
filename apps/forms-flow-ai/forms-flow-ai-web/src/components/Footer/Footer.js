import React from "react";
import "./footer.scss"

import { Navbar, Nav } from "react-bootstrap";
import { Container } from "@material-ui/core";


const Footer = React.memo(() => {
  return (
    <footer className="footerstyle">
      <div role="contentinfo" aria-label="footer" id="footer">
        <Navbar collapseOnSelect fixed="bottom" expand="sm" bg="#036" variant="dark" style={{ borderTop: "2px solid #fcba19" }} className="foi-footer-nav">
          <Container className="foiContainer">
            <Nav className="ml-auto">

              <div className="col-md-3" id="nav" role="navigation">
                <ul>
                  <li><a href="mailto:FOI.Requests@gov.bc.ca">Help</a></li>
                  <li><a href="https://www2.gov.bc.ca/gov/content/home/get-help-with-government-services">Contact</a></li>
                </ul>
              </div>
              <div className="col-md-3" id="nav" role="navigation">
                <ul>
                  <li><a href="http://www2.gov.bc.ca/gov/content/home/disclaimer">Disclaimer</a></li>
                  <li><a href="http://www2.gov.bc.ca/gov/content/home/privacy">Privacy</a></li>
                </ul>
              </div>
              <div className="col-md-3" id="nav" role="navigation">
                <ul>
                  <li><a href="http://www2.gov.bc.ca/gov/content/home/accessibility">Accessibility</a></li>
                  <li><a href="http://www2.gov.bc.ca/gov/content/home/copyright">Copyright</a></li>
                </ul>
              </div>
            </Nav>
          </Container>
        </Navbar>
        <Navbar collapseOnSelect fixed="bottom" expand="sm" bg="#036" variant="dark" style={{ borderTop: "2px solid #fcba19" }} className="foi-mobile-footer-nav">
          <Container className="foimobileContainer">
            <Nav className="ml-auto">

              <div className="row">
                <div className="col-4 foifootercolumn" id="nav" role="navigation">
                  <ul>
                    <li><a href="mailto:FOI.Requests@gov.bc.ca">Help</a></li>
                    <li><a href="https://www2.gov.bc.ca/gov/content/home/get-help-with-government-services">Contact</a></li>
                    <li><a href="http://www2.gov.bc.ca/gov/content/home/disclaimer">Disclaimer</a></li>
                  </ul>
                </div>
                <div className="col-4 foifootercolumn" id="nav" role="navigation">
                  <ul>
                    <li><a href="http://www2.gov.bc.ca/gov/content/home/privacy">Privacy</a></li>
                    <li><a href="http://www2.gov.bc.ca/gov/content/home/accessibility">Accessibility</a></li>
                    <li><a href="http://www2.gov.bc.ca/gov/content/home/copyright">Copyright</a></li>
                  </ul>
                </div>
              </div>

            </Nav>
          </Container>
        </Navbar>
      </div>
    </footer>
  );
});
export default Footer;
