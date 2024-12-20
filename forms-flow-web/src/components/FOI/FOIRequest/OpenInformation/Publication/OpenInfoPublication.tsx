import OpenInfoPublicationMain from "./OpenInfoPublicationMain";
import OpenInfoConfirmationModal from "../OpenInfoConfirmationModal";
import { formatDateInPst } from "../../../../../helper/FOI/helper";

const OpenInfoPublication = ({
  oiPublicationData,
  handleOIDataChange,
  disablePublish,
  confirmModal,
  handleDateConfirmation,
  setConfirmationModal,
  isDataEdited,
  saveData,
  currentOIRequestState,
  ministryId, 
  requestId, 
  bcgovcode, 
  requestNumber,
  handlePublishNow,
}: any) => {

  //Functions
  const publishConfirmation = () => {
    const todaysDate = formatDateInPst(new Date());
    handleOIDataChange(todaysDate, "publicationdate");
  }

  return (
    <>
      <OpenInfoPublicationMain
        oiPublicationData={oiPublicationData}
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
        onClick={handlePublishNow}
      >
        Publish Now
      </button>
      <OpenInfoConfirmationModal
        modal={confirmModal}
        confirm={(confirmModal.title === "Change Publication Date" && handleDateConfirmation) || (confirmModal.title === "Publish Now" && publishConfirmation)}
        setModal={setConfirmationModal}
      />
    </>
  );
};

export default OpenInfoPublication;
