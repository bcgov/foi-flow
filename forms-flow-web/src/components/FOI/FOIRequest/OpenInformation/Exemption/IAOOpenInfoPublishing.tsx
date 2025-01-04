import IAOOpenInfoMain from "./IAOOpenInfoMain";
import OpenInfoConfirmationModal from "../OpenInfoConfirmationModal";
import "../openinfo.scss";

const IAOOpenInfoPublishing = ({
  handleOIDataChange,
  oiPublicationData,
  handleExemptionSave,
  disableSave,
  isOIUser,
  saveModal,
  saveData,
  setSaveModal
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
        onClick={handleExemptionSave}
        disabled={disableSave(oiPublicationData)}
      >
        Save
      </button>
      <OpenInfoConfirmationModal
        modal={saveModal}
        confirm={() => saveData()}
        setModal={setSaveModal}
      />
    </>
  );
};

export default IAOOpenInfoPublishing;
