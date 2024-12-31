import { useState, useEffect } from "react";
import { saveFOIOpenInfoRequest } from "../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { useDispatch, useSelector } from "react-redux";
import IAOOpenInfoPublishing from "./Exemption/IAOOpenInfoPublishing";
import OpenInfoPublication from "./Publication/OpenInfoPublication";
import OpenInfoHeader from "./OpenInfoHeader";
import OpenInfoTab from "./OpenInfoTab";
import "./openinfo.scss";
import { isReadyForPublishing } from "../utils";

type OITransactionObject = {
  oipublicationstatus_id: number;
  oiexemption_id: number | null;
  oiexemptionapproved: boolean | null;
  pagereference: string;
  iaorationale: string;
  oifeedback: string;
  copyrightsevered: boolean;
  publicationdate: string;
  oiexemptiondate: string;
};

const OpenInfo = ({
  requestNumber,
  requestDetails,
  foiministryrequestid,
  foirequestid,
  bcgovcode,
  toast,
  currentOIRequestState,
  isOITeam,
}: any) => {
  const dispatch = useDispatch();

  //App State
  const assignedToList = useSelector(
    (state: any) => state.foiRequests.foiFullAssignedToList
  );
  let foiOpenInfoAdditionalFiles = useSelector(
    (state: any) => state.foiRequests.foiOpenInfoAdditionalFiles
  );
  let foiOITransactionData = useSelector(
    (state: any) => state.foiRequests.foiOpenInfoRequest
  );

  //Local State
  const [oiPublicationData, setOiPublicationData] =
    useState<OITransactionObject>(foiOITransactionData);
  const [confirmationModal, setConfirmationModal] = useState({
    show: false, 
    title: "", 
    message: "", 
    description: "",
    confirmButtonTitle: "",
    confirmationData: null,
  });
  const [tabValue, setTabValue] = useState(isOITeam ? 2 : 1);
  const [isDataEdited, setIsDataEdited] = useState(false);

  useEffect(() => {
    setOiPublicationData(foiOITransactionData);
  }, [foiOITransactionData]);

  //Functions
  const handleOIDataChange = (
    value: number | string | boolean,
    oiDataKey: string
  ) => {
    if (!isDataEdited) {
      setIsDataEdited(true);
    }
    //Reset foi oi data if publication status goes back to publication.
    if (oiDataKey === "oipublicationstatus_id" && value === 2) {
      setOiPublicationData((prev: any) => ({
        ...prev,
        [oiDataKey]: 2,
        copyrightsevered: null,
        publicationdate: null,
        oiexemptiondate: null,
      }));
    } else if (oiDataKey === "publicationdate" && requestDetails.closedate 
      && typeof(value) === "string" && calculateDaysBetweenDates(value, requestDetails.closedate) >= 1 && calculateDaysBetweenDates(value, requestDetails.closedate) <= 10) {
      setConfirmationModal((prev : any) => ({
        ...prev, 
        show: true,
        title: "Change Publication Date",
        description: "The date you have chosen falls within 10 business days of the closed date. Are you sure you want to continue?",
        message: "",
        confirmButtonTitle: "Continue",
        confirmationData: value,
      }));
    } else {
      setOiPublicationData((prev: any) => ({
        ...prev,
        [oiDataKey]: value,
      }));
    }
  };
  const handleExemptionSave = () => {
    if (
      oiPublicationData?.oipublicationstatus_id === 1 &&
      oiPublicationData?.oiexemption_id !== 5
    ) {
      if (isOITeam && oiPublicationData?.oiexemptionapproved != null) {
        setConfirmationModal((prev: any) => ({
          ...prev,
          show: true,
          title: oiPublicationData.oiexemptionapproved ? "Exemption Approved" : "Exemption Denied",
          description: oiPublicationData.oiexemptionapproved 
            ? "Are you sure you want to approve this exemption?"
            : "Are you sure you want to deny this exemption? ",
          message: oiPublicationData.oiexemptionapproved ? "The request will not be eligible for publication and will be removed from the OI Queue." : "The request will still be eligible for publication and will remain in the OI Queue.",
          confirmButtonTitle: "Save Change"
        }));
      } else {
        setConfirmationModal((prev: any) => ({
          ...prev,
          show: true,
          title: "Exemption Request",
          description: "Are you sure you want to change the state to Exemption Request?",
          message: "This will assign the request to the Open Information Queue.",
          confirmButtonTitle: "Save Changes"
        }));
      }
    } else {
      saveData();
    }
  };
  const saveData = () => {
    const toastID = toast.loading("Saving FOI OpenInformation request...");
    const formattedData = {
      ...oiPublicationData,
      publicationdate: oiPublicationData.publicationdate ? 
        new Date(oiPublicationData.publicationdate).toISOString().split('T')[0] : 
        null
    };
    dispatch(
      saveFOIOpenInfoRequest(
        foiministryrequestid,
        foirequestid,
        formattedData,
        isOITeam,
        requestDetails,
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
            const isValidExemptionRequest = !isOITeam && formattedData.oipublicationstatus_id === 1 && formattedData.oiexemption_id !== 5;
            const isValidExemptionDenial = isOITeam && formattedData.oipublicationstatus_id === 1 && formattedData.oiexemption_id !== 5 && formattedData.oiexemptionapproved === false;
            const manualPublicationStatusChange = requestDetails.oistatusid === 8 && formattedData.oipublicationstatus_id === 2;
            if (isValidExemptionRequest) {
              requestDetails.oistatusid = 8;
            }
            if (isValidExemptionDenial || manualPublicationStatusChange) {
              requestDetails.oistatusid = null;
            }
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
      !oiPublicationData?.iaorationale || !oiPublicationData?.pagereference;
    const hasOutOfScopeExemption = oiPublicationData?.oiexemption_id === 5;
    if (isDoNotPublish && hasOutOfScopeExemption) {
      return false;
    }
    if (isDoNotPublish && !hasExemption) {
      return true;
    }
    if (isDoNotPublish && hasExemption) {
      return isMissingRequiredFields;
    }
    if (isDataEdited) {
      return false;
    }
    return true;
  };
  const disablePublish = (oiPublicationData: OITransactionObject) : boolean => {    
    const isMissingRequiredInput = !isReadyForPublishing(oiPublicationData, foiOpenInfoAdditionalFiles, requestNumber);
    const isOIReadyToPublish = currentOIRequestState === "Ready to Publish";
    if (!isOIReadyToPublish) {
      return true;
    }
    if (isMissingRequiredInput) {
      return true;
    }
    return false;
  }
  const handleTabSelect = (value: number): void => {
    setTabValue(value);
  };
  const handleDateConfirmation = (value : Date) => {
    setOiPublicationData((prev: any) => ({
      ...prev,
      publicationdate: value,
    }));
  }
  const calculateDaysBetweenDates = (date1: string, date2: string) => {
    return Math.round((new Date(date1).getTime() - new Date(date2).getTime()) / (1000 * 3600 *24));
  }
  const handlePublishNow = () => {
    setConfirmationModal((prev : any) => ({
      ...prev, 
      show: true,
      title: "Publish Now",
      description: "Are you sure you want to Publish this request now?",
      message: "",
      confirmButtonTitle: "Publish Now",
    }));
  }

  console.log("req", requestDetails)
  console.log("oi info", oiPublicationData)
  console.log("isOIUser", isOITeam)

  return (
    <>
      <div className="oi-section">
        <OpenInfoHeader
          requestDetails={requestDetails}
          requestNumber={requestNumber}
          isOIUser={isOITeam}
          assignedToList={assignedToList}
          foiministryrequestid={foiministryrequestid}
          foirequestid={foirequestid}
          toast={toast}
        />
        <OpenInfoTab tabValue={tabValue} handleTabSelect={handleTabSelect} isOIUser={isOITeam} />
        {tabValue === 1 ? (
          <IAOOpenInfoPublishing
            handleOIDataChange={handleOIDataChange}
            oiPublicationData={oiPublicationData}
            handleExemptionSave={handleExemptionSave}
            disableSave={disableSave}
            isOIUser={isOITeam}
            saveModal={confirmationModal}
            saveData={saveData}
            setSaveModal={setConfirmationModal}
          />
        ) : (
          <OpenInfoPublication
            oiPublicationData={oiPublicationData}
            handleOIDataChange={handleOIDataChange}
            disablePublish={disablePublish}
            confirmModal={confirmationModal}
            handleDateConfirmation={handleDateConfirmation}
            setConfirmationModal={setConfirmationModal}
            isDataEdited={isDataEdited}
            saveData={saveData}
            currentOIRequestState={currentOIRequestState}
            ministryId={foiministryrequestid}
            requestId={foirequestid} 
            bcgovcode={bcgovcode}
            requestNumber={requestNumber}
            handlePublishNow={handlePublishNow}
          />
        )}
      </div>
    </>
  );
};

export default OpenInfo;
