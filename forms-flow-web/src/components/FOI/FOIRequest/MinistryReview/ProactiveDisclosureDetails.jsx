import React from "react";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { ConditionalComponent } from "../../../../helper/FOI/helper";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";

const useStyles = makeStyles(() => ({
  rowMargin: {
    marginBottom: "1em",
  },
}));

const ProactiveDisclosureDetails = React.memo((requestDetails) => {
  const classes = useStyles();
  const _requestDetails = requestDetails.requestDetails;
  const requestType = _requestDetails.requestType
    ? _requestDetails.requestType.replace(/^./, (str) => str.toUpperCase())
    : "";

  return (
    <Card id="proactiveDisclosureDetailsMinistry" className="foi-details-card">
      <label className="foi-details-label">PROACTIVE DISCLOSURE DETAILS</label>
      <CardContent>
        <div className={clsx("row", "foi-details-row", classes.rowMargin)}>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Report Period:</b>
            </div>
            <div>
              <span>{_requestDetails.reportPeriod}</span>
            </div>
          </div>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Start Date:</b>
            </div>
            <div>
              <span>{_requestDetails.requestProcessStart}</span>
            </div>
          </div>
        </div>
        <div className="row foi-details-row">
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>CFR Due Date:</b>
            </div>
            <div>
              <span>{_requestDetails.cfrDueDate}</span>
            </div>
          </div>
          <div className="col-lg-6 foi-details-col">
            <div>
              <b>Publication Date:</b>
            </div>
            <div>
              <span>{_requestDetails.publicationDate}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

export default ProactiveDisclosureDetails;
