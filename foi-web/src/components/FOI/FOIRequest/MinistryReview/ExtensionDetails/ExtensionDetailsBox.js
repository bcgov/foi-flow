import React, { useEffect, useContext } from "react";

import { useParams } from "react-router-dom";
import { ActionContext } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { fetchExtensions } from "../../../../../apiManager/services/FOI/foiExtensionServices";
import ExtensionsTable from "./ExtensionsTable";

const ExtensionDetailsBox = React.memo(() => {
  const { dispatch } = useContext(ActionContext);

  const { ministryId } = useParams();

  useEffect(() => {
    if (ministryId) {
      fetchExtensions({
        ministryId,
        dispatch,
      });
    }
  }, [ministryId]);
  
  return (
    <>
      <Card className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col ">
            <label className="foi-details-label">EXTENSION DETAILS</label>
          </div>
        </div>
        <CardContent>
          <ExtensionsTable showActions={false}/>
        </CardContent>
      </Card>
    </>
  );
});

export default ExtensionDetailsBox;
