import 'reactjs-popup/dist/index.css';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import _ from "lodash";
import { Typography } from '@material-ui/core';
import './exportrequestdetails.scss';


const ExportCFRForms = ({
  foiRequestCFRFormHistory,
  foiRequestCFRForm
}) => {

  let cfrForms = foiRequestCFRFormHistory?.filter(cfr=>cfr?.cfrfeeid===foiRequestCFRForm?.cfrfeeid).length>0 ? []:[foiRequestCFRForm]
  foiRequestCFRFormHistory.map((cfrHistory) => {
    if (cfrHistory['cfrfeestatus.description'] === 'Approved') {
      cfrForms.push(cfrHistory);
    }
  })

  return (
    <div id="CfrFormExport">
      {cfrForms.map((entry, index) => {
        return <div className='request-accordian'
          key={entry.cfrfeeid}>
          <Accordion defaultExpanded={true} className='history-entry-accordion' >
            <AccordionSummary style={{ pageBreakInside: 'avoid' }} >
              <Typography className="history-entry-title">
                {entry.version_created_at ? 'Version ' + (cfrForms.length - index) + " - " : "Draft - "} {entry['cfrformreason.description'] ? entry['cfrformreason.description'] : 'Original'}
              </Typography>
              <Typography className="history-entry-username">
                {entry.version_created_at ? entry.version_createdby + " - " + entry.version_created_at : ""}
              </Typography>
            </AccordionSummary>

            <AccordionDetails
              sx={{
                '& .MuiTextField-root': { my: 1, mx: 0 },
              }}
            >
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <div className="historyLabel">
                    OVERALL FEE ESTIMATE
                  </div>
                </div>
              </div>
              <div className="row foi-details-row">
                {/* <div className="col-lg-6 foi-details-col"> */}
                <div className="col-lg-6 foi-details-col">
                  <span className="formLabel">Estimate Payment Method</span>
                </div>
                <div className="col-lg-6 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatepaymentmethod || 'NA'}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-6 foi-details-col">
                  <span className="formLabel">Balance Payment Method</span>
                </div>
                <div className="col-lg-6 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.balancepaymentmethod || 'NA'}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Amount Paid</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.amountpaid).toFixed(2)}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Balance Remaining</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.balanceremaining).toFixed(2)}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Estimated Total</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.estimatedtotaldue).toFixed(2)}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Actual Total</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.actualtotaldue).toFixed(2)}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Fee Waiver Amount</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.feewaiveramount).toFixed(2)}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Refund Amount</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{"$" + parseFloat(entry.feedata.refundamount).toFixed(2)}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <hr />
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <div className="historyLabel">LOCATING/RETRIEVING</div>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Estimated Hours</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatedlocatinghrs + " hr(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Actual Hours</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.actuallocatinghrs + " hr(s)"}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <hr />
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <div className="historyLabel">
                    PRODUCING
                  </div>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Estimated Hours</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatedproducinghrs + " hr(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Actual Hours</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.actualproducinghrs + " hr(s)"}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <hr />
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <div className="historyLabel">
                    PREPARING
                  </div>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Estimated Hours IAO</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatediaopreparinghrs + " hr(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Estimated Hours Ministry</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatedministrypreparinghrs + " hr(s)"}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Actual Hours IAO</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.actualiaopreparinghrs + " hr(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Actual Hours Ministry</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.actualministrypreparinghrs + " hr(s)"}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <hr />
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-12 foi-details-col">
                  <div className="historyLabel">
                    VOLUME
                  </div>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Electronic Estimated Files</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatediaopreparinghrs + " file(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Electronic Actual Files</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatedelectronicpages + " file(s)"}</span>
                </div>
              </div>
              <div className="row foi-details-row">
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Hardcopy Estimated Pages</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatediaopreparinghrs + " pg(s)"}</span>
                </div>
                <div className="col-lg-4 foi-details-col">
                  <span className="formLabel">Hardcopy Actual Pages</span>
                </div>
                <div className="col-lg-2 foi-details-col">
                  <span className="cfrAttributeValue">{entry.feedata.estimatedelectronicpages + " pg(s)"}</span>
                </div>
              </div>
            </AccordionDetails>
          </Accordion>
        </div>
      })}
    </div>
  );
};
export default ExportCFRForms;
