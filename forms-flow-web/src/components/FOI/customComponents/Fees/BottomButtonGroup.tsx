export const BottomButtonGroup = ({ 
  save, 
  validateFields, 
  requestState, 
  StateEnum, 
  formData, 
  isNewCFRForm, 
  isMinistry, 
  setCreateModalOpen, 
  disableNewCfrFormBtn 
}: any) => {
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
    </div>
  )
}