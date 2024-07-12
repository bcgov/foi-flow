import React, { useState } from "react";
import "../BottomButtonGroup/bottombuttongroup.scss";
import { makeStyles } from "@material-ui/core/styles";
import { useDispatch } from "react-redux";
import {
  postFOIS3DocumentPreSignedUrl,
  saveFilesinS3,
} from "../../../../apiManager/services/FOI/foiOSSServices";
import { saveMinistryRequestDetails } from "../../../../apiManager/services/FOI/foiRequestServices";
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";
import { ConfirmationModal } from "../../customComponents";
import { StateEnum } from "../../../../constants/FOI/statusEnum";
import { ConditionalComponent } from "../../../../helper/FOI/helper";
import { alertUser } from "./utils";
import clsx from "clsx";

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
  // btnsecondaryenabled: {
  //   border: '1px solid #38598A',
  //   backgroundColor: '#FFFFFF',
  //   color: '#38598A'
  // }
}));

const BottomButtonGroup = React.memo(
  ({
    isValidationError,
    saveMinistryRequestObject,
    unSavedRequest,
    recordsUploading,
    CFRUnsaved,
    handleSaveRequest,
    currentSelectedStatus,
    hasStatusRequestSaved,
    attachmentsArray,
    stateChanged,
    validLockRecordsState,
  }) => {
    /**
     * Bottom Button Group of Review request Page
     * Button enable/disable is handled here based on the validation
     */
    const { requestId, ministryId, requestState } = useParams();
    const classes = useStyles();
    const dispatch = useDispatch();

    const [opensaveModal, setsaveModal] = useState(false);

    const disableSave = isValidationError;

    //State to manage approval data for Ministry Sign Off
    const [ministryApprovalState, setMinistryApprovalState] = useState({
      approverName: "",
      approverTitle: "",
      approvedDate: ""
    });

    const handleApprovalInputs = (event) => {
      if(event.target.name === "name") {
        setMinistryApprovalState((prevState) => {
          return {...prevState, approverName: event.target.value}
        })
      }
      if(event.target.name === "title") {
        setMinistryApprovalState((prevState) => {
          return {...prevState, approverTitle: event.target.value}
        })
      }
      if(event.target.name === "datePicker") {
        setMinistryApprovalState((prevState) => {
          return {...prevState, approvedDate: event.target.value}
        })
      }
    }


    const returnToQueue = (e) => {
      if (
        (!unSavedRequest && !recordsUploading && !CFRUnsaved) ||
        window.confirm(
          "Are you sure you want to leave? Your changes will be lost."
        )
      ) {
        e.preventDefault();
        window.removeEventListener("beforeunload", alertUser);
        window.location.href = "/foi/dashboard";
      } else {
        window.history.pushState(null, null, window.location.pathname);
      }
    };

    const saveMinistryRequest = async () => {
      //Logic to reset user lock records status to null (and have FE useEffect in FOIRequest.js/MinistryView.js logic takeover) if request is in unlocked request states
      if (saveMinistryRequestObject.userlockedrecords !== null && !validLockRecordsState(currentSelectedStatus)) {
        saveMinistryRequestObject.userlockedrecords = null;
      }
      dispatch(
        saveMinistryRequestDetails(
          {
            ...saveMinistryRequestObject,
            divisions:
              saveMinistryRequestObject?.divisions?.filter(
                (division) =>
                  division.stageid !== -1 || division.divisionid !== -1
              ) || [],
          },
          requestId,
          ministryId,
          (err, res) => {
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
              const _state = currentSelectedStatus
                ? currentSelectedStatus
                : requestState;
              handleSaveRequest(_state, false, res.id);
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
              handleSaveRequest(currentSelectedStatus, true, "");
            }
          }
        )
      );
    };

    const handleOnHashChange = (e) => {
      returnToQueue(e);
    };

    React.useEffect(() => {
      if (stateChanged && currentSelectedStatus !== "" && !isValidationError) {
        saveRequestModal();
      }
    }, [currentSelectedStatus, stateChanged]);

    React.useEffect(() => {
      if (unSavedRequest || recordsUploading || CFRUnsaved) {
        window.history.pushState(null, null, window.location.pathname);
        window.addEventListener("popstate", handleOnHashChange);
        window.addEventListener("beforeunload", alertUser);
      }
      return () => {
        window.removeEventListener("popstate", handleOnHashChange);
        window.removeEventListener("beforeunload", alertUser);
      };
    }, [unSavedRequest, recordsUploading, CFRUnsaved]);

    const saveRequestModal = () => {
      if (currentSelectedStatus !== saveMinistryRequestObject?.currentState)
        setsaveModal(true);
    };

    const [successCount, setSuccessCount] = useState(0);
    const [fileCount, setFileCount] = useState(0);
    const [documents, setDocuments] = useState([]);
    
    const saveStatusId = () => {
      if (currentSelectedStatus) {
        switch (currentSelectedStatus.toLowerCase()) {
          case StateEnum.review.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel = StateEnum.review.label;
            break;
          case StateEnum.feeassessed.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel =
              StateEnum.feeassessed.label;
            break;
          case StateEnum.deduplication.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel =
              StateEnum.deduplication.label;
            break;
          case StateEnum.harms.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel = StateEnum.harms.label;
            break;
          case StateEnum.signoff.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel = StateEnum.signoff.label;
            break;
          case StateEnum.response.name.toLowerCase():
            saveMinistryRequestObject.ministrysignoffapproval = ministryApprovalState;
            saveMinistryRequestObject.requeststatuslabel = StateEnum.response.label;
            break;
          case StateEnum.callforrecords.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel =
              StateEnum.callforrecords.label;
            break;
          case StateEnum.recordsreadyforreview.name.toLowerCase():
            saveMinistryRequestObject.requeststatuslabel = StateEnum.recordsreadyforreview.label;
        }
      }
    };

    React.useEffect(() => {
      if (successCount === fileCount && successCount !== 0) {
        setsaveModal(false);
        saveStatusId();
        saveMinistryRequestObject.documents = documents;
        saveMinistryRequest();
        hasStatusRequestSaved(currentSelectedStatus);
      }
    }, [successCount]);

    const handleSaveModal = (value, fileInfoList, files) => {
      setsaveModal(false);
      setFileCount(files?.length);

      if (!value) {
        handleSaveRequest(requestState, true, "");
        return;
      }

      if (isValidationError) {
        return;
      }

      if (!files || files.length < 1) {
        saveStatusId();
        saveMinistryRequest();
        hasStatusRequestSaved(currentSelectedStatus);
        return;
      }

      postFOIS3DocumentPreSignedUrl(ministryId, fileInfoList, 'attachments', saveMinistryRequestObject.idNumber.split("-")[0], dispatch, (err, res) => {
        let _documents = [];
        if (!err) {
          res.map((header, index) => {
            const _file = files?.find((file) => file.filename === header.filename);
            const documentpath = {
              documentpath: header.filepathdb,
              filename: header.filename,
              category: header.filestatustransition,
            };
            _documents.push(documentpath);
            setDocuments(_documents);
            saveFilesinS3(header, _file, dispatch, (_err, _res) => {
              let count = 0;
              if (_res === 200) {
                count = index + 1;
              }
              setSuccessCount(count);
            });
          });
        }
      });
    };

    return (
      <div className={classes.root}>
        <ConditionalComponent condition={opensaveModal}>
          <ConfirmationModal
            attachmentsArray={attachmentsArray}
            openModal={opensaveModal}
            handleModal={handleSaveModal}
            handleApprovalInputs={handleApprovalInputs}
            ministryApprovalState={ministryApprovalState}
            state={currentSelectedStatus}
            saveRequestObject={saveMinistryRequestObject}
          />
        </ConditionalComponent>
        <div className="foi-bottom-button-group">
          <button
            type="button"
            className={clsx("btn", "btn-bottom", {
              [classes.btndisabled]: disableSave,
              [classes.btnenabled]: !disableSave,
            })}
            disabled={disableSave}
            onClick={saveMinistryRequest}
          >
            Save
          </button>
          {/* <button type="button" className={`btn btn-bottom ${classes.btnsecondaryenabled}`} onClick={returnToQueue} >Return to Queue</button>       */}
        </div>
      </div>
    );
  }
);

export default BottomButtonGroup;
