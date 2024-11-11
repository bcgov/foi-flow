import { useState, useEffect } from "react";
import "./iaoopeninfo.scss";
import IAOOpenInfoHeader from "./IAOOpenInfoHeader";
import IAOOpenInfoMain from "./IAOOpenInfoMain";
import IAOOpenInfoSaveModal from "./IAOOpenInfoSaveModal";
import { saveFOIOpenInfoRequest } from "../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { useDispatch, useSelector } from "react-redux";

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
  const assignedToList = useSelector(
    (state : any) => state.foiRequests.foiFullAssignedToList
  );
  const isOIUser: boolean = userGroups.includes("OI Team");
  const dispatch = useDispatch();

  //Local State
  const [oiPublicationData, setOiPublicationData] =
    useState<OITransactionObject>(foiOITransactionData);
  const [showSaveModal, setShowSaveModal] = useState(false);

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
        isOIUser={isOIUser}
        assignedToList={assignedToList}
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