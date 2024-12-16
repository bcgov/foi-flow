import OpenInfoPublicationMain from "./OpenInfoPublicationMain";

const OpenInfoPublication = ({ oiPublicationData, isOIUser, ministryId, requestId, bcgovcode, requestNumber }: any) => {
  return (
    <>
      <OpenInfoPublicationMain
        oiPublicationData={oiPublicationData}
        isOIUser={isOIUser}
        ministryId={ministryId}
        requestId={requestId}
        bcgovcode={bcgovcode}
        requestNumber={requestNumber}
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
