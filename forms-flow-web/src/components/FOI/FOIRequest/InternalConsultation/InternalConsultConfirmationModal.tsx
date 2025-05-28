import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    IconButton,
  } from "@material-ui/core";
import { saveFOIRequestConsults, fetchFOIRequestConsults } from "../../../../apiManager/services/FOI/foiRequestConsultServices";
import CloseIcon from "@material-ui/icons/Close";
import { MinistriesList } from "../../customComponents";
import './InternalConsultConfirmationModal.scss';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { useDispatch } from "react-redux";
import { toast } from "react-toastify";
import { ConsultTypes } from "../../../../../src/helper/consult-helper";
import { ConsultTransactionObject } from "./types";
import { useEffect, useState } from "react";
  
  const InternalConsultConfirmationModal = ({
    requestId,
    ministryId,
    modal,
    confirm,
    setModal,
    masterProgramAreaList,
    handleUpdatedMasterProgramAreaList,
    requestDetails,
    requestConsults,
    setUnSavedRequest,
  }: any) => {

    const dispatch = useDispatch();
    const MinistriesListTyped = MinistriesList as React.FC<any>;

    const handleConfirmation = () => {
      setUnSavedRequest(false);
      const checkedItems = masterProgramAreaList.filter((programArea:any) => programArea.isChecked);
      if (modal.title === "Internal Consultation") {
        const subjectCode = modal.confirmationData?.subjectCode;
        const dueDate = modal.confirmationData?.dueDate;
        confirm({
            selectedMinistries: checkedItems,
            subjectCode: modal.confirmationData?.subjectCode,
            dueDate: modal.confirmationData?.dueDate,
          });
        
          const consultFormattedData: ConsultTransactionObject[] = (checkedItems || []).map((ministry:any) => ({
          fileNumber: requestDetails?.axisRequestId ? `${requestDetails.axisRequestId}-CON` : "",
          consultAssignedTo: requestDetails?.assignedTo ?? null,
          consultTypeId: ConsultTypes.Internal,
          programAreaId: ministry.programareaid,
          subjectCode: subjectCode ? subjectCode : null,
          dueDate: dueDate ?? null,
        }));
          
          dispatch(
                  saveFOIRequestConsults(
                    requestId,
                    ministryId,
                    consultFormattedData,
                    (err:any, res:any) => {            
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
                        console.log("res : ",res)
                        dispatch(fetchFOIRequestConsults(ministryId));
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
                      }
                    }
                  )
                );

      }


      setModal((prev : any) => ({
        ...prev,     
        show: false, 
        title: "", 
        message: "", 
        description: "",
        descriptionDetail:"",
        confirmButtonTitle: "",
        confirmationData: null,
      }));
    };
    const handleClose = () => {
      setModal((prev : any) => ({
        ...prev,     
        show: false, 
        title: "", 
        message: "", 
        description: "",
        descriptionDetail:"",
        confirmButtonTitle: "",
        confirmationData: null,
      }));
    };
  

    // const handleMinistriesChange = (updatedList: any[]) => {
    // setSelectedMinistriesState(updatedList);
    // handleUpdatedMasterProgramAreaList(updatedList); 
    // };

    return (
      <div className="consult-confirmation-dialog">
        <Dialog
          open={modal.show}
          onClose={() => {
            handleClose();
          }}
          aria-labelledby="consult-confirmation-dialog-title"
          aria-describedby="restricted-modal-text"
          maxWidth={"md"}
          fullWidth={true}
          PaperProps={{
            className: 'consult-confirmation-dialog'
          }}
        >
          <DialogTitle disableTypography id="consult-confirmation-dialog-title">
            <h2 className="consult-confirmation-header">{modal.title}</h2>
            <IconButton className="consult-title-col3" onClick={handleClose}>
              <i className="dialog-close-button">Close</i>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent id="consult-confirmation-dialog-content">
            <DialogContentText id="consult-modal-text" component={"span"}>
              <div className="modal-msg">
                <div className="confirmation-message">{modal.description}</div>
                <div className="confirmation-message-detail">{modal.descriptionDetail}</div>
                <div className="modal-msg-description">
                  <i>
                    <span>{modal.message}</span>
                  </i>
                </div>
              </div>

              {modal.show && modal.title === "Internal Consultation" && Object.entries(masterProgramAreaList).length !== 0 && (
             <div className="ministries-list-container">
              <MinistriesListTyped
                masterProgramAreaList={masterProgramAreaList}
                handleUpdatedMasterProgramAreaList={handleUpdatedMasterProgramAreaList}
                disableInput={false}
                isMultiSelectMode={true}
                showOnlySelected={true}  
                isInternalConsultValidationError={false}
              />
              </div>
            )}
            {modal.title === "Internal Consultation" && (
            <div className="help-box">
            <div className="help-content">
                <div className="consult-help-inline">
                <InfoOutlinedIcon className="consult-help-icon" />
                <span className="consult-help-title">Help:</span>
                <span className="consult-help-description">
                    This will create an internal consultation for each recipient selected.
                </span>
                </div>
                <ul>
                <li>You can track them in your FOI Request queue, under your original request.</li>
                <li>
                    You will need to create a consultation package in the “Redaction App” and attach it to the internal consultation(s) created.
                </li>
                </ul>
            </div>
            </div>
            )}
            </DialogContentText>
          </DialogContent>
          <DialogActions className="custom-dialog-actions">
            <button
              className={`btn-bottom btn-save btn`}
              onClick={handleConfirmation}
              disabled={false}
            >
              {modal.confirmButtonTitle}
            </button>
            <button className="btn-bottom btn-cancel" onClick={handleClose}>
              Cancel
            </button>
          </DialogActions>
        </Dialog>
      </div>
    );
  };
  
  export default InternalConsultConfirmationModal;