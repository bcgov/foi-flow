import { useState, useEffect } from "react";
import { saveFOIOpenInfoRequest, fetchFOIOpenInfoRequest } from "../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { useDispatch, useSelector } from "react-redux";
import IAOOpenInfoPublishing from "./Exemption/IAOOpenInfoPublishing";
import OpenInfoPublication from "./Publication/OpenInfoPublication";
import OpenInfoHeader from "./OpenInfoHeader";
import OpenInfoTab from "./OpenInfoTab";
import "./openinfo.scss";
import { OIPublicationStatus, OITransactionObject } from "./types";
import { OIStates, OIPublicationStatuses, OIExemptions } from "../../../../helper/openinfo-helper";
import { calculateDaysRemaining, addBusinessDays, addBusinessDaysToDate, calculateBusinessDaysBetween } from "../../../../helper/FOI/helper";

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
  const oiPublicationStatuses: OIPublicationStatus[] = useSelector(
    (state: any) => state.foiRequests.oiPublicationStatuses
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
    setOiPublicationData({...foiOITransactionData, oipublicationstatus_id: foiOITransactionData?.oipublicationstatus_id || OIPublicationStatuses.Publish});
    if (isOITeam) {
      if (foiOITransactionData.oipublicationstatus_id === findOIPublicationState('Do Not Publish')?.oipublicationstatusid) {
        setTabValue(1)
      } else {
        setTabValue(2)
      }
    }
  }, [foiOITransactionData]);

  //Functions
  const findOIPublicationState = (name: string) => {
    return oiPublicationStatuses.find((s: OIPublicationStatus) => s.name === name);
  }
  const handleOIDataChange = (
    value: number | string | boolean,
    oiDataKey: string
  ) => {
    if (!isDataEdited) {
      setIsDataEdited(true);
    }
    //Reset foi oi data if publication status goes back to publication.
    if (oiDataKey === "oipublicationstatus_id" && value === findOIPublicationState("Publish")?.oipublicationstatusid) {
      setOiPublicationData((prev: any) => ({
        ...prev,
        [oiDataKey]: value,
        copyrightsevered: null,
        publicationdate: null,
        oiexemptiondate: null,
        oiexemption_id: null
      }));
    } else if (oiDataKey === "publicationdate" && requestDetails.closedate 
      && typeof(value) === "string" && calculateBusinessDaysBetween(value, requestDetails.closedate) >=0 && calculateBusinessDaysBetween(value, requestDetails.closedate) <= 10) {
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
      oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish &&
      oiPublicationData?.oiexemption_id !== OIExemptions.OutsideScopeOfPublication
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
          description: "Are you sure you want to create an exemption request?",
          message: "This request will be assigned to the Open Information team queue.",
          confirmButtonTitle: "Save Changes"
        }));
      }
    } else {
      saveData();
    }
  };
  const saveData = (publicationdate?: any) => {
    const toastID = toast.loading("Saving FOI OpenInformation request...");
    publicationdate = publicationdate || (oiPublicationData.publicationdate ? 
      new Date(oiPublicationData.publicationdate).toISOString().split('T')[0] : 
      null)
    const formattedData = {
      ...oiPublicationData,
      publicationdate: publicationdate
    };
    if (formattedData.oiexemptionapproved === false && isOITeam) {
      formattedData.oipublicationstatus_id = findOIPublicationState("Publish")?.oipublicationstatusid || OIPublicationStatuses.Publish;
      formattedData.oiexemption_id = null;
    }
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
                "FOI Open Information request has been saved successfully.",
              position: "top-right",
              isLoading: false,
              autoClose: 3000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
            });
            const isValidExemptionRequest = !isOITeam && formattedData.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && formattedData.oiexemption_id !== OIExemptions.OutsideScopeOfPublication;
            const isValidExemptionDenial = isOITeam && formattedData.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && formattedData.oiexemption_id !== OIExemptions.OutsideScopeOfPublication && formattedData.oiexemptionapproved === false;
            const isValidExemptionApproved = isOITeam && formattedData.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish && formattedData.oiexemption_id !== OIExemptions.OutsideScopeOfPublication && formattedData.oiexemptionapproved === true;
            const manualPublicationStatusChange = requestDetails.oistatusid === OIStates.ExemptionRequest && formattedData.oipublicationstatus_id === OIPublicationStatuses.Publish;
            const isUnpublish = isOITeam && formattedData.oipublicationstatus_id === OIPublicationStatuses.UnpublishRequest;
            if (isValidExemptionRequest) {
              requestDetails.oistatusid = OIStates.ExemptionRequest;
            }
            if (isValidExemptionDenial || manualPublicationStatusChange) {
              requestDetails.oistatusid = null;
            }
            if (isValidExemptionApproved) {
              requestDetails.oistatusid = OIStates.DoNotPublish
            }
            if (isUnpublish) {
              requestDetails.oistatusid = OIStates.Unpublished
            }
            dispatch(fetchFOIOpenInfoRequest(foiministryrequestid));
          } else {
            toast.error(
              "Temporarily unable to save FOI Open Information request. Please try again in a few minutes.",
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
    const isDoNotPublish = oiPublicationData?.oipublicationstatus_id === OIPublicationStatuses.DoNotPublish;
    const hasExemption = oiPublicationData?.oiexemption_id;
    const isMissingRequiredFields =
      !oiPublicationData?.iaorationale || !oiPublicationData?.pagereference;
    const hasOutOfScopeExemption = oiPublicationData?.oiexemption_id === OIExemptions.OutsideScopeOfPublication;
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
    const isMissingRequiredInput = oiPublicationData?.copyrightsevered === null || oiPublicationData?.publicationdate === null || foiOpenInfoAdditionalFiles?.findIndex((f: any) => f.filename.includes("Response_Letter_" + requestNumber + ".pdf")) < 0;
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
            earliestPublicationDate={requestDetails ? addBusinessDaysToDate(requestDetails.closedate, 10) : null}
          />
        )}
      </div>
    </>
  );
};

export default OpenInfo;
