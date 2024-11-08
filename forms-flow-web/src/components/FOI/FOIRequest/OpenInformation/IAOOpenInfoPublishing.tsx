import { useState, useEffect } from "react";
import "./iaoopeninfo.scss";
import IAOOpenInfoHeader from "./IAOOpenInfoHeader";
import IAOOpenInfoMain from "./IAOOpenInfoMain";
import IAOOpenInfoSaveModal from "./IAOOpenInfoSaveModal";
import { saveFOIOpenInfoRequest } from "../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { useDispatch, useSelector } from "react-redux";
import user from "../../../../modules/userDetailReducer";

type OITransactionObject = {
  oipublicationstatus_id: number;
  oiexemption_id: number | null;
  oiexemptionapproved: boolean | null;
  pagereference: string;
  iaorationale: string;
  oifeedback: string;
};

const IAOOpenInfoPublishing = ({
  requestNumber,
  requestDetails,
  userDetail,
  foiOITransactionData,
  foiministryrequestid,
  foirequestid,
  toast,
}: any) => {
  const userGroups: string[] = userDetail.groups.map((group: any) =>
    group.slice(1)
  );
  const isOIUser: boolean = userGroups.includes("OI Team");
  const dispatch = useDispatch();

  //Local State
  const [oiPublicationData, setOiPublicationData] =
    useState<OITransactionObject>(foiOITransactionData);
  const [showSaveModal, setShowSaveModal] = useState(false);

  console.log("BANG", oiPublicationData);
  console.log(userDetail, "userdetail");
  console.log("userGroups", userGroups);

  //Functions
  const handleOIDataChange = (
    value: number | string | boolean,
    oiDataKey: string
  ) => {
    if (oiDataKey === "oipublicationstatus_id" && value === 2) {
      setOiPublicationData((prev: any) => ({
        ...prev,
        [oiDataKey]: 2,
        iaorationale: "",
        oiexemption_id: null,
        pagereference: "",
      }));
    } else {
      setOiPublicationData((prev: any) => ({
        ...prev,
        [oiDataKey]: value,
      }));
    }
  };
  const handleSave = () => {
    if (
      oiPublicationData?.oipublicationstatus_id === 1 &&
      oiPublicationData?.oiexemption_id !== 5
    ) {
      setShowSaveModal(true);
    } else {
      saveData();
    }
  };
  const saveData = () => {
    const toastID = toast.loading("Saving FOI OpenInformation request...");
    dispatch(
      saveFOIOpenInfoRequest(
        foiministryrequestid,
        foirequestid,
        oiPublicationData,
        (err: any, _res: any) => {
          if (!err) {
            toast.update(toastID, {
              type: "success",
              render:
                "FOI OpenInformation request has been saved successfully.",
              position: "top-right",
              isLoading: false,
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
          } else {
            toast.error(
              "Temporarily unable to save FOI OpenInformation request. Please try again in a few minutes.",
              {
                position: "top-right",
                autoClose: 3000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
              }
            );
          }
        }
      )
    );
  };
  const disableSave = (oiPublicationData: OITransactionObject): boolean => {
    const isDoNotPublish = oiPublicationData?.oipublicationstatus_id === 1;
    const hasExemption = oiPublicationData?.oiexemption_id !== null;
    const isMissingRequiredFields =
      !oiPublicationData?.iaorationale && !oiPublicationData?.pagereference;
    const hasOutOfScopeExemption = oiPublicationData?.oiexemption_id === 5;
    if (isDoNotPublish && hasOutOfScopeExemption) {
      return false;
    }
    if (isDoNotPublish && hasExemption) {
      return isMissingRequiredFields;
    }
    return true;
  };

  return (
    <div className="oi-section">
      <IAOOpenInfoHeader
        requestDetails={requestDetails}
        requestNumber={requestNumber}
      />
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
        // AH NOTE -> THIS WILL BE BUGGY IF CHANGED BACK TO PUBLISH.
        // IF status changed back to any other besides do not publish -> wipe data? ASK MATT ON EDITING DATA AFTER AND WIPING DATA IF STATUS CHANGED
        // Save button disabled = if on original load no foiopeninforequest exists (and using default obj) OR exmeption reason is null && publicationSTatusid is not 2
      >
        Save
      </button>
      <IAOOpenInfoSaveModal
        showModal={showSaveModal}
        saveData={saveData}
        setShowModal={setShowSaveModal}
      />
    </div>
  );
};

export default IAOOpenInfoPublishing;

/* To do 
1. create get, post api route for foioirequest data X
2. trigger get route in FE to gather all the data X
3. trigger update route x
4. if publish selected again -> WIPE ALL OI FORM DATA + CREATE MODAL X
5. finalzie FE ux for iao side of things (confirm all questions incl. top bars, save button , toast for save?)
6. trigger post route in FE to post foioi txn data (done when save button clicked and when request is closed, and when request state is changed - eseentially any time a reuest is changed triger a new foi opn txn change)
*/
