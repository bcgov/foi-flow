import Tooltip from "@mui/material/Tooltip";

export const BottomButtonGroup = ({ 
  save, 
  validateFields, 
  requestState, 
  StateEnum, 
  formData, 
  isNewCFRForm, 
  isMinistry, 
  setCreateModalOpen, 
  disableNewCfrFormBtn,
  handleGenerateInvoice,
  cfrStatus,
  isProcessingFeeSubTab,
}: any) => {
  const generateInvoiceDisabled: boolean = cfrStatus !== "approved";
  return (
    <div className="foi-bottom-button-group cfrform">
      <button
        type="button"
        className="col-lg-4 btn btn-bottom btn-save"
        id="btncfrsave"
        onClick={save}
        color="primary"
        disabled={!validateFields() || requestState === StateEnum.peerreview.name || (formData?.reason === 'init' && isNewCFRForm)}
      >
        Save
      </button>
      {isMinistry &&
      <button
        type="button"
        className="col-lg-4 btn btn-bottom btn-cancel"
        onClick={() => {
          setCreateModalOpen(true)
        }}
        disabled={disableNewCfrFormBtn()}
      >
        + Create New Processing Fee Form
      </button>}
      {isProcessingFeeSubTab && !isMinistry && 
      <Tooltip
        title={
          generateInvoiceDisabled && 
          <div style={{ fontSize: "10px" }}>
            Invoice generation disabled. Please change the 'Processing Fee Status' field to 'Approved'
          </div>
        }
        enterDelay={1000}
        leaveDelay={200}
        >
        <button
          type="button"
          className="col-lg-4 btn btn-bottom btn-save"
          id="btncfrinvoice"
          onClick={() => {handleGenerateInvoice()}}
          color="primary"
          disabled={generateInvoiceDisabled}
        >
          Generate Invoice
        </button>
      </Tooltip>
      }
    </div>
  )
}