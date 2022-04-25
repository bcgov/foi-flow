import React, { useContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ActionContext } from "./ActionContext";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import AddExtensionModal from "./AddExtensionModal";
import DeleteExtensionModal from "./DeleteExtensionModal";
import { fetchExtensions } from "../../../../apiManager/services/FOI/foiExtensionServices";
import ExtensionsTable from "./ExtensionsTable";
import "./extensionscss.scss";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import { StateEnum } from "../../../../constants/FOI/statusEnum";

const useStyles = makeStyles((theme) => ({
  btndisabled: {
    color: "#808080",
  },
}));

const ExtensionDetailsBox = React.memo(() => {
  const classes = useStyles();

  const { setSaveModalOpen, setExtensionId, pendingExtensionExists, dispatch, requestState } =
    useContext(ActionContext);

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
          <div className="col-lg-8 foi-details-col">
            <label className="foi-details-label">EXTENSION DETAILS</label>
          </div>
          <div className="col-lg-4 foi-details-col">
            <button
              className={clsx("btn", "btn-link", "btn-description-history", {
                [classes.btndisabled]: pendingExtensionExists,
              })}
              onClick={(e) => {
                e.preventDefault();
                setSaveModalOpen(true);
                setExtensionId(null);
              }}
              disabled={pendingExtensionExists || requestState?.toLowerCase() ===  StateEnum.onhold.name.toLowerCase() || 
                requestState?.toLowerCase() === StateEnum.closed.name.toLowerCase()}
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
      <DeleteExtensionModal />
    </>
  );
});

export default ExtensionDetailsBox;
