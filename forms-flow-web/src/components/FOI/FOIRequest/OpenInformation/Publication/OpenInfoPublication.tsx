import OpenInfoPublicationMain from "./OpenInfoPublicationMain";
import OpenInfoConfirmationModal from "../OpenInfoConfirmationModal";
import { formatDateInPst } from "../../../../../helper/FOI/helper";
import { OIPublicationStatuses } from "../../../../../helper/openinfo-helper";

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
  earliestPublicationDate
}: any) => {

  //Functions
  const publishConfirmation = () => {
    const todaysDate = formatDateInPst(new Date());
    saveData(todaysDate);
  }

  const save = () => {
    if (oiPublicationData.oipublicationstatus_id === OIPublicationStatuses.UnpublishRequest) {
      setConfirmationModal({
        show: true,
        title: "Unpublish Request",
        description: "Are you sure you want to unpublish this request?",
        message: "This request will be removed from Open Information and marked for Review.",
        confirmButtonTitle: "Unpublish Request"
      });
    } else {
      saveData()
    }
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
        earliestPublicationDate={earliestPublicationDate}
      />
      <button
        type="button"
        className="btn btn-bottom"
        disabled={!isDataEdited}
        onClick={save}
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
        confirm={(confirmModal.title === "Change Publication Date" && handleDateConfirmation)
           || (confirmModal.title === "Publish Now" && publishConfirmation)
           || (confirmModal.title === "Unpublish Request" && saveData)
          }
        setModal={setConfirmationModal}
      />
    </>
  );
};

export default OpenInfoPublication;
