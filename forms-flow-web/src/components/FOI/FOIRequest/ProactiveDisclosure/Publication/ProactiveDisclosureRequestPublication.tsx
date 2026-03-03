import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import ProactiveDisclosureRequestPublicationMain from "./ProactiveDisclosureRequestPublicationMain";
import OpenInfoConfirmationModal from "../../OpenInformation/OpenInfoConfirmationModal";
import OpenInfoHeader from "../../OpenInformation/OpenInfoHeader";
import { saveFOIOpenInfoRequest, fetchFOIOpenInfoRequest } from "../../../../../apiManager/services/FOI/foiOpenInfoRequestServices";
import { OIPublicationStatus, OITransactionObject } from "./types";
import { OIStates, OIPublicationStatuses } from "../../../../../helper/openinfo-helper";
import { calculateBusinessDaysBetween, addBusinessDays, formatDateInPst } from "../../../../../helper/FOI/helper";
import "../../OpenInformation/openinfo.scss";

const ProactiveDisclosureRequestPublication = ({
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
    const [confirmationModal, setConfirmationModal] = useState<{
        show: boolean;
        title: string;
        message: string;
        description: string;
        confirmButtonTitle: string;
        confirmationData: any;
    }>({
        show: false,
        title: "",
        message: "",
        description: "",
        confirmButtonTitle: "",
        confirmationData: null,
    });
    const [isDataEdited, setIsDataEdited] = useState(false);

    useEffect(() => {
        setOiPublicationData({ ...foiOITransactionData, oipublicationstatus_id: foiOITransactionData?.oipublicationstatus_id || OIPublicationStatuses.Publish });
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
                receiveddate: null,
                oiexemption_id: null
            }));
        } else if (oiDataKey === "publicationdate" && requestDetails.closedate
            && typeof (value) === "string") {
            const daysBetween = calculateBusinessDaysBetween(requestDetails.closedate, value);
            if (daysBetween >= 0 && daysBetween < 10) {
                setConfirmationModal((prev: any) => ({
                    ...prev,
                    show: true,
                    title: "Change Publication Date",
                    description: "The date you have chosen falls within 10 business days of the closed date. Are you sure you want to continue?",
                    message: "",
                    confirmButtonTitle: "Continue",
                    confirmationData: value,
                }));
            }
            else {
                setOiPublicationData((prev: any) => ({
                    ...prev,
                    [oiDataKey]: value,
                }));
            }
        } else {
            setOiPublicationData((prev: any) => ({
                ...prev,
                [oiDataKey]: value,
            }));
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
                        const manualPublicationStatusChange = requestDetails.oistatusid === OIStates.ExemptionRequest && oiPublicationData.oipublicationstatus_id === OIPublicationStatuses.Publish;
                        const isUnpublish = isOITeam && oiPublicationData.oipublicationstatus_id === OIPublicationStatuses.UnpublishRequest;

                        if (manualPublicationStatusChange) {
                            requestDetails.oistatusid = null;
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

    const disablePublish = (): boolean => {
        const responseLetterRegex = /Response[_\-\s]*Letter/i;
        const isMissingRequiredInput = oiPublicationData?.copyrightsevered === null || oiPublicationData?.publicationdate === null || !foiOpenInfoAdditionalFiles?.some((f: any) => responseLetterRegex.test(f.filename));
        const isOIReadyToPublish = currentOIRequestState === "Ready to Publish";
        if (!isOIReadyToPublish) {
            return true;
        }
        if (isMissingRequiredInput) {
            return true;
        }
        return false;
    }

    const handleDateConfirmation = (value: Date) => {
        setOiPublicationData((prev: any) => ({
            ...prev,
            publicationdate: value,
        }));
    }
    const handlePublishNow = () => {
        setConfirmationModal((prev: any) => ({
            ...prev,
            show: true,
            title: "Publish Now",
            description: "Are you sure you want to Publish this request now?",
            message: "",
            confirmButtonTitle: "Publish Now",
        }));
    }

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
                message: "This request will be removed from the Open Information website, the request state will be changed to 'Unpublished', and the request will be available in the Open Information queue for further review and action.",
                confirmButtonTitle: "Unpublish Request",
                confirmationData: null,
            });
        } else {
            saveData()
        }
    }

    return (
        <div className="oi-section">
            <OpenInfoHeader
                requestDetails={requestDetails}
                requestNumber={requestNumber}
                isOIUser={isOITeam}
                assignedToList={assignedToList}
                foiministryrequestid={foiministryrequestid}
                foirequestid={foirequestid}
                toast={toast}
                handleOIDataChange={handleOIDataChange}
            />
            <ProactiveDisclosureRequestPublicationMain
                oiPublicationData={oiPublicationData}
                handleOIDataChange={handleOIDataChange}
                currentOIRequestState={currentOIRequestState}
                ministryId={foiministryrequestid}
                requestId={foirequestid}
                bcgovcode={bcgovcode}
                requestNumber={requestNumber}
                earliestPublicationDate={requestDetails?.publicationDate}
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
                modal={confirmationModal}
                confirm={(confirmationModal.title === "Change Publication Date" && handleDateConfirmation)
                    || (confirmationModal.title === "Publish Now" && publishConfirmation)
                    || (confirmationModal.title === "Unpublish Request" && saveData)
                }
                setModal={setConfirmationModal}
            />
        </div>
    );
};

export default ProactiveDisclosureRequestPublication;
