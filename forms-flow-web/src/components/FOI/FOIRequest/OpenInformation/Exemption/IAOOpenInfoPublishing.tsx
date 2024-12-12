import IAOOpenInfoMain from "./IAOOpenInfoMain";
import IAOOpenInfoSaveModal from "./IAOOpenInfoSaveModal";
import "../openinfo.scss";

const IAOOpenInfoPublishing = ({
  handleOIDataChange,
  oiPublicationData,
  handleSave,
  disableSave,
  isOIUser,
  showSaveModal,
  saveData,
  setShowSaveModal
}: any) => {

  return (
    <>
      <IAOOpenInfoMain
        handleOIDataChange={handleOIDataChange}
        oiPublicationData={oiPublicationData}
        isOIUser={isOIUser}
      />
      <button
        type="button"
        className="btn btn-bottom"
        onClick={handleSave}
        disabled={disableSave(oiPublicationData)}
      >
        Save
      </button>
      <IAOOpenInfoSaveModal
        showModal={showSaveModal}
        saveData={saveData}
        setShowModal={setShowSaveModal}
      />
    </>
  );
};

export default IAOOpenInfoPublishing;
