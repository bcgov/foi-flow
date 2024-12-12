import OpenInfoPublicationMain from "./OpenInfoPublicationMain";

const OpenInfoPublication = ({ oiPublicationData, isOIUser }: any) => {
  return (
    <>
      <OpenInfoPublicationMain
        oiPublicationData={oiPublicationData}
        isOIUser={isOIUser}
      />
      <button
        type="button"
        className="btn btn-bottom"
        // onClick={handleSave}
        // disabled={disableSave(oiPublicationData)}
      >
        Save
      </button>
      <button
        type="button"
        className="btn btn-bottom"
        // onClick={handleSave}
        // disabled={disableSave(oiPublicationData)}
      >
        Publish
      </button>
    </>
  );
};

export default OpenInfoPublication;
