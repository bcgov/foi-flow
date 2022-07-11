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
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

const useStyles = makeStyles((_theme) => ({
  btndisabled: {
    color: "#808080",
  },
  heading: {
    color: '#FFF',
    fontSize: '16px !important',
    fontWeight: 'bold !important'
  },
  accordionSummary: {
    flexDirection: 'row-reverse'
  }
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
     <div className='request-accordian' >
      <Accordion defaultExpanded={true}>
      <AccordionSummary className={classes.accordionSummary} expandIcon={<ExpandMoreIcon />} id="extensionDetails-header">
      <Typography className={classes.heading}>EXTENSION DETAILS</Typography>
      </AccordionSummary>
      <AccordionDetails>
          <div>
            <button
              className={clsx("btn", "new-extension-link", "btn-description-history", {
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
          <ExtensionsTable />
        </AccordionDetails>
    </Accordion>
  </div>
      <AddExtensionModal />
      <DeleteExtensionModal />
    </>
  );
});

export default ExtensionDetailsBox;
