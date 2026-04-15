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
  earliestPublicationDate,
  handleUnpublish,
  disableUnpublish,
  publishNow,
  unpublish,
}: any) => {

  //Functions
  const publishConfirmation = () => {
    const todaysDate = formatDateInPst(new Date());
    publishNow(todaysDate);
  }
  // const save = () => {
  //   if (oiPublicationData.oipublicationstatus_id === OIPublicationStatuses.UnpublishRequest) {
  //     setConfirmationModal({
  //       show: true,
  //       title: "Unpublish Request",
  //       description: "Are you sure you want to Unpublish this request?",
  //       message: "Your request will be sent to our Publication Service for unpublishing. You will receive a notification shortly once your request has been unpublished and the request state will be moved to 'Unpublished'.",
  //       confirmButtonTitle: "Unpublish"
  //     });
  //   } else {
  //     saveData()
  //   }
  // }

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
        onClick={() => saveData()}
      >
        Save
      </button>
      {currentOIRequestState === "Published" ?
       <button
        type="button"
        disabled={disableUnpublish()}
        className="btn btn-bottom"
        onClick={handleUnpublish}
      >
        Unpublish
      </button>
      : <button
        type="button"
        disabled={disablePublish()}
        className="btn btn-bottom"
        onClick={handlePublishNow}
      >
        Publish Now
      </button>
      }
      <OpenInfoConfirmationModal
        modal={confirmModal}
        confirm={(confirmModal.title === "Change Publication Date" && handleDateConfirmation)
           || (confirmModal.title === "Publish Now" && publishConfirmation)
           || (confirmModal.title === "Unpublish Request" && unpublish)
          }
        setModal={setConfirmationModal}
      />
    </>
  );
};

export default OpenInfoPublication;
