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
import "./extensionscss.scss"
import { extensionStatusId } from "../../../../constants/FOI/enum"
import clsx from "clsx"
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  btndisabled: {
    color: "#808080",
  },
}));

const ExtensionDetailsBox = React.memo(() => {
  const classes = useStyles();

  const { setModalOpen, dispatch, extensions, setExtensionId} = useContext(ActionContext);

  const pendingExtensionExists = extensions.some(
    (ex) => ex.extensionstatusid === extensionStatusId.pending
  );
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
            <button
              className={clsx("btn", "btn-link", "btn-description-history", {
                [classes.btndisabled]: pendingExtensionExists,
              })}
              onClick={(e) => {
                e.preventDefault();
                setModalOpen(true);
                setExtensionId(null)
              }}
              disabled={pendingExtensionExists}
            >
              New Extension
            </button>
          </div>
        </div>
        <CardContent>
          <ExtensionsTable />
        </CardContent>
      </Card>
      <AddExtensionModal />
    </>
  );
});

export default ExtensionDetailsBox;
