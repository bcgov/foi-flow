import React, { useEffect, useState } from "react";
import "./bottombuttongroup.scss";
import { makeStyles } from "@material-ui/core/styles";
import { useDispatch } from "react-redux";
import {
  saveRequestDetails,
  openRequestDetails
} from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";
import { ConfirmationModal } from "../../customComponents";
import {
  addBusinessDays,
  formatDate,
  calculateDaysRemaining,
  ConditionalComponent
} from "../../../../helper/FOI/helper";
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { dueDateCalculation, getRequestState, returnToQueue } from "./utils";
import { handleBeforeUnload } from "../utils";
import { setFOILoader } from '../../../../actions/FOI/foiRequestActions'
import clsx from "clsx";
import AxisSyncModal from "../AxisDetails/AxisSyncModal";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    marginTop: "30px",
    marginBottom: "50px",
  },
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
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
  btnsecondaryenabled: {
    border: "1px solid #38598A",
    backgroundColor: "#FFFFFF",
    color: "#38598A",
  },
}));

const BottomButtonGroup = React.memo(
  ({
    isValidationError,
    urlIndexCreateRequest,
    saveRequestObject,
    unSavedRequest,
    handleSaveRequest,
    handleOpenRequest,
    currentSelectedStatus,
    hasStatusRequestSaved,
    disableInput,
    stateChanged,
    setIsAddRequest,
    requestState,
    axisSyncedData,
    axisMessage
  }) => {
    /**
     * Bottom Button Group of Review request Page
     * Button enable/disable is handled here based on the validation
     */
    const { requestId, ministryId } = useParams();

    const classes = useStyles();
    const dispatch = useDispatch();

    const [openModal, setOpenModal] = useState(false);
    const [opensaveModal, setsaveModal] = useState(false);

    const [closingDate, setClosingDate] = useState(formatDate(new Date()));
    const [closingReasonId, setClosingReasonId] = useState();

    const [axisSyncModalOpen, setAxisSyncModalOpen] = useState(false);

    const handleClosingDateChange = (cDate) => {
      setClosingDate(cDate);
    };

    const handleClosingReasonChange = (cReasonId) => {
      setClosingReasonId(cReasonId);
    };

    useEffect(() => {
      if (stateChanged) {
        requestState = saveRequestObject.currentState;
      }
    }, [stateChanged]);

    const saveRequest = async () => {
      if (urlIndexCreateRequest > -1) {
        saveRequestObject.requeststatusid = StateEnum.intakeinprogress.id;
        setIsAddRequest(false);
      }      
      dispatch(setFOILoader(true))
      dispatch(
        saveRequestDetails(
          saveRequestObject,
          urlIndexCreateRequest,
          requestId,
          ministryId,
          (err, res) => {            
            dispatch(setFOILoader(false))
            if (!err) {
              toast.success("The request has been saved successfully.", {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              });
              const _state = getRequestState({
                currentSelectedStatus,
                requestState,
                urlIndexCreateRequest,
                saveRequestObject,
              });
              handleSaveRequest(_state, false, res.id);
              hasStatusRequestSaved(currentSelectedStatus);
            } else {
              toast.error(
                "Temporarily unable to save your request. Please try again in a few minutes.",
                {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: true,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                  progress: undefined,
                }
              );
              handleSaveRequest(requestState, true, "");
            }
          }
        )
      );
    };

    const handleOnHashChange = (e) => {
      returnToQueue(e, unSavedRequest);
    };

    React.useEffect(() => {
      if (isValidationError || !stateChanged) {
        return;
      }

      if (
        currentSelectedStatus &&
        currentSelectedStatus !== StateEnum.open.name &&
        saveRequestObject.requeststatusid &&
        saveRequestObject.currentState
      ) {
        saveRequestModal();
      } else {
        saveRequestObject.requeststatusid = StateEnum.open.id;
        if (currentSelectedStatus === StateEnum.open.name && ministryId) {
          saveRequestModal();
        } else {
          openRequest();
        }
      }
    }, [currentSelectedStatus, stateChanged]);

    React.useEffect(() => {
      if (unSavedRequest) {
        window.history.pushState(null, null, window.location.pathname);
        window.addEventListener("popstate", handleOnHashChange);
        window.addEventListener("beforeunload", handleBeforeUnload);
        return () => {
          window.removeEventListener("popstate", handleOnHashChange);
          window.removeEventListener("beforeunload", handleBeforeUnload);
        };
      }
    }, [unSavedRequest]);

    const openRequest = () => {
      saveRequestObject.id = saveRequestObject.id
        ? saveRequestObject.id
        : requestId;
      saveRequestObject.requeststatusid = 1;
      setOpenModal(true);
    };

    const saveRequestModal = () => {
      if (currentSelectedStatus !== saveRequestObject?.currentState)
        setsaveModal(true);
    };

    const handleModal = (value) => {
      setOpenModal(false);
      if (!value) {
        handleOpenRequest("", "", true);
        return;
      }
      dispatch(
        openRequestDetails(saveRequestObject, (err, res) => {
          if (!err) {
            toast.success("The request has been opened successfully.", {
              position: "top-right",
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
            const parentRequestId = res.id;
            res.ministryRequests.sort(function (a, b) {
              return a.filenumber - b.filenumber;
            });
            const firstMinistry = res.ministryRequests[0];
            handleOpenRequest(parentRequestId, firstMinistry.id, false);
            hasStatusRequestSaved(StateEnum.open.name);
          } else {
            toast.error(
              "Temporarily unable to open your request. Please try again in a few minutes.",
              {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              }
            );
            handleOpenRequest("", "", true);
          }
        })
      );
    };

    const handleSaveModal = (value, fileInfoList) => {
      setsaveModal(false);
      if (!value) {
        handleSaveRequest(requestState, true, "");
        return;
      }

      if (isValidationError) {
        return;
      }

      switch (currentSelectedStatus) {
        case StateEnum.closed.name:
          saveRequestObject.requeststatusid = StateEnum.closed.id;
          saveRequestObject.closedate = closingDate;
          saveRequestObject.closereasonid = closingReasonId;
          saveRequest();
          break;

        case StateEnum.callforrecords.name:
          saveRequestObject.requeststatusid = StateEnum.callforrecords.id;
          if (
            !("cfrDueDate" in saveRequestObject) ||
            saveRequestObject.cfrDueDate === ""
          ) {
            const calculatedCFRDueDate = dueDateCalculation(new Date(), 10);
            saveRequestObject.cfrDueDate = calculatedCFRDueDate;
          }
          if (
            ![StateEnum.closed.name, StateEnum.onhold.name].includes(
              currentSelectedStatus
            ) &&
            saveRequestObject.onholdTransitionDate
          ) {
            const today = new Date();

            // make it start of today
            today.setHours(0, 0, 0, 0);

            const onHoldDays = calculateDaysRemaining(
              today,
              saveRequestObject.onholdTransitionDate
            );
            const calculatedCFRDueDate = addBusinessDays(
              saveRequestObject.cfrDueDate,
              onHoldDays
            );
            const calculatedRequestDueDate = addBusinessDays(
              saveRequestObject.dueDate,
              onHoldDays
            );
            saveRequestObject.cfrDueDate = calculatedCFRDueDate;
            saveRequestObject.dueDate = calculatedRequestDueDate;
          }
          saveRequest();
          break;

        case StateEnum.redirect.name:
        case StateEnum.open.name:
        case StateEnum.intakeinprogress.name:
        case StateEnum.review.name:
        case StateEnum.onhold.name:
        case StateEnum.signoff.name:
        case StateEnum.feeassessed.name:
        case StateEnum.consult.name:
        case StateEnum.deduplication.name:
        case StateEnum.harms.name:
        case StateEnum.response.name:
          const status = Object.values(StateEnum).find(
            (statusValue) => statusValue.name === currentSelectedStatus
          );

          saveRequestObject.requeststatusid = status.id;
          saveRequest();
          break;

        default:
          return;
      }
    };

    return (
      <div className={classes.root}>
        <ConditionalComponent condition={openModal}>
          <ConfirmationModal
            requestId={requestId}
            openModal={openModal}
            handleModal={handleModal}
            state={StateEnum.open.name}
            saveRequestObject={saveRequestObject}
          />
        </ConditionalComponent>

        <ConditionalComponent condition={opensaveModal}>
          <ConfirmationModal
            requestId={requestId}
            openModal={opensaveModal}
            handleModal={handleSaveModal}
            state={currentSelectedStatus}
            saveRequestObject={saveRequestObject}
            handleClosingDateChange={handleClosingDateChange}
            handleClosingReasonChange={handleClosingReasonChange}
          />
        </ConditionalComponent>

        <div className="foi-bottom-button-group">
          {urlIndexCreateRequest < 0 &&
            (requestState?.toLowerCase() !== StateEnum.intakeinprogress.name.toLowerCase() &&
            requestState?.toLowerCase() !== StateEnum.unopened.name.toLowerCase()) &&
              <button
                type="button"
                className="btn btn-bottom"
                disabled={Object.entries(axisSyncedData)?.length === 0 || axisMessage !== "WARNING"}
                onClick={() => {
                  setAxisSyncModalOpen(true);
                }}
              >
                Sync with AXIS
              </button>
            }
          <button
            type="button"
            className={clsx("btn", "btn-bottom", {
              [classes.btndisabled]: isValidationError,
              [classes.btnenabled]: !isValidationError,
            })}
            disabled={isValidationError || disableInput}
            onClick={saveRequest}
          >
            Save
          </button>
          <button
            type="button"
            className={`btn btn-bottom ${classes.btnsecondaryenabled}`}
            onClick={(e) => returnToQueue(e, unSavedRequest)}
          >
            Return to Queue
          </button>
        </div>
        {axisSyncModalOpen && (
          <AxisSyncModal
            axisSyncModalOpen={axisSyncModalOpen}
            setAxisSyncModalOpen={setAxisSyncModalOpen}
            saveRequest={saveRequest}
            saveRequestObject={saveRequestObject}
            urlIndexCreateRequest={urlIndexCreateRequest}
            handleSaveRequest={handleSaveRequest}
            currentSelectedStatus={currentSelectedStatus}
            hasStatusRequestSaved={hasStatusRequestSaved}
            requestState={requestState}
            requestId={requestId}
            ministryId={ministryId}
            axisSyncedData={axisSyncedData}
          />
        )}
      </div>
    );
  }
);

export default BottomButtonGroup;
