import React, { useEffect, useContext } from "react";

import { useParams } from "react-router-dom";
import { ActionContext } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { fetchExtensions } from "../../../../../apiManager/services/FOI/foiExtensionServices";
import ExtensionsTable from "./ExtensionsTable";

const ExtensionDetailsBox = React.memo(() => {
  const { dispatch } = useContext(ActionContext);

  const { requestId } = useParams();

  useEffect(() => {
    if (requestId) {
      dispatch(fetchExtensions(requestId));
    }
  }, [requestId]);
  
  return (
    <>
      <Card className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col ">
            <label className="foi-details-label">EXTENSION DETAILS</label>
          </div>
        </div>
        <CardContent>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col"></div>
            <div className="col-lg-6 foi-details-col"></div>
          </div>
          <ExtensionsTable showActions={false}/>
        </CardContent>
      </Card>
    </>
  );
});

export default ExtensionDetailsBox;
