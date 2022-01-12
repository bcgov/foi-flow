import React, { useEffect, useContext } from "react";

import { useParams } from "react-router-dom";
import { ActionContext } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import AddExtensionModal from "./AddExtensionModal"
import {
  fetchExtensions,
} from "../../../../apiManager/services/FOI/foiExtensionServices";
import ExtensionsTable from "./ExtensionsTable";

const ExtensionDetailsBox = React.memo(() => {
  const { setModalOpen, dispatch} = useContext(ActionContext);

  const { ministryId } = useParams();

  useEffect(() => {
    if (ministryId) {
      dispatch(fetchExtensions(ministryId));
    }
  }, [ministryId]);
  
  return (
    <>
      <Card className="foi-details-card">
        <div className="row foi-details-row">
          <div className="col-lg-8 foi-details-col ">
            <label className="foi-details-label">EXTENSION DETAILS</label>
          </div>
          <div className="col-lg-4 foi-details-col ">
            <a
              href="#"
              className="foi-floatright foi-link"
              onClick={(e) => {
                e.preventDefault();
                setModalOpen(true);
              }}
            >
              New Extension
            </a>
          </div>
        </div>
        <CardContent>
          <div className="row foi-details-row">
            <div className="col-lg-6 foi-details-col"></div>
            <div className="col-lg-6 foi-details-col"></div>
          </div>
          <ExtensionsTable/>
        </CardContent>
      </Card>
      <AddExtensionModal/>
    </>
  );
});

export default ExtensionDetailsBox;
