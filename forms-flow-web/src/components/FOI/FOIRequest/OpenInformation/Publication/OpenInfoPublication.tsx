import OpenInfoPublicationMain from "./OpenInfoPublicationMain";
import OpenInfoConfirmationModal from "../OpenInfoConfirmationModal";

const OpenInfoPublication = ({
  oiPublicationData,
  isOIUser,
  handleOIDataChange,
  disablePublish,
  confirmDateModal,
  handleDateConfirmation,
  setConfirmDateModal,
  isDataEdited,
  saveData,
  currentOIRequestState,
  ministryId, 
  requestId, 
  bcgovcode, 
  requestNumber
}: any) => {
  return (
    <>
      <OpenInfoPublicationMain
        oiPublicationData={oiPublicationData}
        isOIUser={isOIUser}
        handleOIDataChange={handleOIDataChange}
        currentOIRequestState={currentOIRequestState}
        ministryId={ministryId}
        requestId={requestId}
        bcgovcode={bcgovcode}
        requestNumber={requestNumber}
      />
      <button
        type="button"
        className="btn btn-bottom"
        disabled={!isDataEdited}
        onClick={saveData}
      >
        Save
      </button>
      <button
        type="button"
        disabled={disablePublish()}
        className="btn btn-bottom"
        // onClick={handleSave}
      >
        Publish Now
      </button>
      <OpenInfoConfirmationModal
        modal={confirmDateModal}
        confirm={handleDateConfirmation}
        setModal={setConfirmDateModal}
      />
    </>
  );
};

export default OpenInfoPublication;
