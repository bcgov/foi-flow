import React, { useState, useContext } from "react";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import { makeStyles } from "@material-ui/core/styles";
import { ActionContext } from "./ActionContext";
import Grid from "@material-ui/core/Grid";
import "./extensionscss.scss";
import CircularProgress from "@material-ui/core/CircularProgress";
import clsx from "clsx";
import {
  deleteExtensionRequest,
  fetchExtensions,
} from "../../../../apiManager/services/FOI/foiExtensionServices";
import { fetchFOIRequestAttachmentsList } from "../../../../apiManager/services/FOI/foiAttachmentServices";
import { fetchFOIRequestNotesList } from "../../../../apiManager/services/FOI/foiRequestNoteServices";
import { useParams } from "react-router-dom";
import { errorToast } from "./utils";
import { setRequestDueDate } from "../../../../actions/FOI/foiRequestActions";
import { formatDate } from "../../../../helper/FOI/helper";

const useStyles = makeStyles((theme) => ({
  btndisabled: {
    border: "none",
    backgroundColor: "#eceaea",
    color: "#FFFFFF",
  },
  btnenabled: {
    border: "none",
    backgroundColor: "#38598A",
    color: "#FFFFFF",
  },
  gridContainer: {
    padding: "2em",
  },
  DialogContent: {
    margin: "auto",
  },
  DialogLable: {
    fontWeight: theme.typography.fontWeightBold,
  },
  fullWidth: {
    width: "100%",
    padding: 0,
  },
}));

const DeleteExtensionModal = () => {
  const classes = useStyles();
  const { requestId, ministryId } = useParams();

  const {
    deleteModalOpen,
    setDeleteModalOpen,
    extensionId,
    setExtensionId,
    dispatch,
  } = useContext(ActionContext);

  const [loading, setLoading] = useState(false);

  const handleDelete = () => {
    setLoading(true);
    deleteExtensionRequest({
      extensionId,
      ministryId,
      requestId,
      callback: (data) => {
        fetchExtensions({
          ministryId: ministryId,
          errorCallback: () => {
            errorToast("Error occurred while refreshing extensions.");
          },
          dispatch,
        });
        dispatch(fetchFOIRequestNotesList(requestId, ministryId));
        dispatch(fetchFOIRequestAttachmentsList(requestId, ministryId));
        setLoading(false);
        setDeleteModalOpen(false);
        if (data.newduedate) {
          dispatch(
            setRequestDueDate(
              formatDate(new Date(data.newduedate), "yyyy-MM-dd")
            )
          );
        }
      },
      errorCallback: (errorMessage) => {
        setLoading(false);
        errorToast(errorMessage);
      },
      dispatch,
    });
  };

  return (
    <>
      <Dialog
        id="delete-extension-dialog"
        open={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        aria-labelledby="extension-dialog-title"
        maxWidth={"md"}
        fullWidth={true}
        TransitionProps={{
          onExited: () => {
            setLoading(false);
            setExtensionId(null);
          },
        }}
      >
        <DialogTitle disableTypography id="extension-dialog-title">
          <Grid
            container
            direction="row-reverse"
            justifyContent="flex-start"
            alignItems="flex-start"
          >
            <IconButton
              className="title-col3"
              onClick={() => setDeleteModalOpen(false)}
            >
              <CloseIcon />
            </IconButton>
          </Grid>
        </DialogTitle>

        <DialogContent
          className="dialog-content"
          style={{
            overflowX: "hidden",
          }}
        >
          <DialogContentText variant="h4">
            Are you sure you want to delete this extension?
          </DialogContentText>
        </DialogContent>

        <DialogActions className="dialog-content-nomargin">
          <Grid
            container
            direction="row"
            justifyContent="flex-start"
            alignItems="flex-start"
            className={classes.gridContainer}
            spacing={2}
          >
            <Grid item xs={6}>
              <button
                style={{ width: "100%" }}
                className={clsx("btn-save", {
                  [classes.btnenabled]: !loading,
                  [classes.btndisabled]: loading,
                })}
                onClick={handleDelete}
                disabled={loading}
              >
                {loading ? <CircularProgress size="2em" /> : "Continue"}
              </button>
            </Grid>
            <Grid item xs={6}>
              <button
                className="btn-cancel"
                style={{ width: "100%" }}
                disabled={loading}
                onClick={() => setDeleteModalOpen(false)}
              >
                Cancel
              </button>
            </Grid>
          </Grid>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DeleteExtensionModal;
