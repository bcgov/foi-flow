import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import ProactiveDisclosureRequestPublicationMain from "./ProactiveDisclosureRequestPublicationMain";
import OpenInfoConfirmationModal from "../../OpenInformation/OpenInfoConfirmationModal";
import OpenInfoHeader from "../../OpenInformation/OpenInfoHeader";
import { saveFOIProactiveDisclosureRequest, fetchFOIProactiveDisclosureRequest, publishFOIProactiveDisclosureRequest } from "../../../../../apiManager/services/FOI/foiProactiveDisclosureServices";
import { PDPublicationStatus, PDTransactionObject } from "./types";
import { OIStates, OIPublicationStatuses } from "../../../../../helper/openinfo-helper";
import { calculateBusinessDaysBetween, formatDateInPst } from "../../../../../helper/FOI/helper";
import "../../OpenInformation/openinfo.scss";

const ProactiveDisclosureRequestPublication = ({
    requestNumber,
    requestDetails,
    foiministryrequestid,
    foirequestid,
    bcgovcode,
    toast,
    currentPDRequestState,
    isOITeam,
}: any) => {
    const dispatch = useDispatch();

    //App State
    const assignedToList = useSelector(
        (state: any) => state.foiRequests.foiFullAssignedToList
    );
    let foiPDTransactionData = useSelector(
        (state: any) => state.foiRequests.foiOpenInfoRequest
    );
    const pdPublicationStatuses: PDPublicationStatus[] = useSelector(
        (state: any) => state.foiRequests.oiPublicationStatuses
    );

    //Local State
    const [pdPublicationData, setPdPublicationData] =
        useState<PDTransactionObject>(foiPDTransactionData);
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
        setPdPublicationData({
            ...foiPDTransactionData,
            oipublicationstatus_id: foiPDTransactionData?.oipublicationstatus_id || OIPublicationStatuses.Publish
        });
    }, [foiPDTransactionData]);

    //Functions
    const findPDPublicationState = (name: string) => {
        return pdPublicationStatuses.find((s: PDPublicationStatus) => s.name === name);
    }
    const handlePDDataChange = (
        value: number | string | boolean,
        pdDataKey: string
    ) => {
        if (!isDataEdited) {
            setIsDataEdited(true);
        }
        //Reset foi pd data if publication status goes back to publication.
         if (pdDataKey === "publicationdate" && requestDetails.closedate
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
                setPdPublicationData((prev: any) => ({
                    ...prev,
                    [pdDataKey]: value,
                }));
            }
        } else {
            setPdPublicationData((prev: any) => ({
                ...prev,
                [pdDataKey]: value,
            }));
        }
    };

    const saveData = (publicationdate?: any) => {
        const toastID = toast.loading("Saving FOI Proactive Disclosure request...");
        publicationdate = publicationdate || (pdPublicationData.publicationdate ?
            new Date(pdPublicationData.publicationdate).toISOString().split('T')[0] :
            null)
        const formattedData = {
            ...pdPublicationData,
            publicationdate: publicationdate
        };
        dispatch(
            saveFOIProactiveDisclosureRequest(
                foiministryrequestid,
                foirequestid,
                formattedData,
                (err: any, _res: any) => {
                    if (!err) {
                        toast.update(toastID, {
                            type: "success",
                            render:
                                "FOI Proactive Disclosure request has been saved successfully.",
                            position: "top-right",
                            isLoading: false,
                            autoClose: 3000,
                            hideProgressBar: true,
                            closeOnClick: true,
                            pauseOnHover: true,
                            draggable: true,
                            progress: undefined,
                        });
                        dispatch(fetchFOIProactiveDisclosureRequest(foiministryrequestid));
                        setIsDataEdited(false);
                    } else {
                        toast.error(
                            "Temporarily unable to save FOI Proactive Disclosure request. Please try again in a few minutes.",
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

    const publishNow = (publicationdate : any): any => {
        const toastID = toast.loading("Publishing FOI Proactive Disclosure request...");
        publicationdate = publicationdate || (pdPublicationData.publicationdate ?
            new Date(pdPublicationData.publicationdate).toISOString().split('T')[0] :
            null)
        const formattedData = {
            ...pdPublicationData,
            publicationdate: publicationdate
        };
        dispatch(
            publishFOIProactiveDisclosureRequest(
                foiministryrequestid,
                foirequestid,
                formattedData,
                (err: any, _res: any) => {
                    if (!err) {
                        toast.update(toastID, {
                            type: "success",
                            render:
                                "FOI Proactive Disclosure request has been successfully published.",
                            position: "top-right",
                            isLoading: false,
                            autoClose: 3000,
                            hideProgressBar: true,
                            closeOnClick: true,
                            pauseOnHover: true,
                            draggable: true,
                            progress: undefined,
                        });
                        requestDetails.oistatusid = OIStates.Published;
                        dispatch(fetchFOIProactiveDisclosureRequest(foiministryrequestid));
                        setIsDataEdited(false);
                    } else {
                        toast.error(
                            "Temporarily unable to publish FOI Proactive Disclosure request. Please try again in a few minutes.",
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
    }

    const disablePublish = (): boolean => {
        const isMissingRequiredInput = pdPublicationData?.publicationdate === null;
        const isPDReadyToPublish = currentPDRequestState === "Ready to Publish";
        if (!isPDReadyToPublish) {
            return true;
        }
        if (isMissingRequiredInput) {
            return true;
        }
        return false;
    }

    const handleDateConfirmation = (value: Date) => {
        setPdPublicationData((prev: any) => ({
            ...prev,
            publicationdate: value,
        }));
    }
    const handlePublishNow = () => {
        setConfirmationModal((prev: any) => ({
            ...prev,
            show: true,
            title: "Publish Files Now",
            description: "Your publication files will be published immediately. Any previously scheduled publication date is overridden.",
            message: "",
            confirmButtonTitle: "Publish Now",
        }));
    }

    const publishConfirmation = () => {
        const todaysDate = formatDateInPst(new Date());
        publishNow(todaysDate);
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
                handleOIDataChange={handlePDDataChange}
            />
            <ProactiveDisclosureRequestPublicationMain
                pdPublicationData={pdPublicationData}
                handlePDDataChange={handlePDDataChange}
                currentPDRequestState={currentPDRequestState}
                ministryId={foiministryrequestid}
                requestId={foirequestid}
                bcgovcode={bcgovcode}
                requestNumber={requestNumber}
                earliestPublicationDate={requestDetails?.earliestEligiblePublicationDate}
            />
            <button
                type="button"
                className="btn btn-bottom"
                disabled={!isDataEdited}
                onClick={saveData}
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
                    || (confirmationModal.title === "Publish Files Now" && publishConfirmation)
                }
                setModal={setConfirmationModal}
            />
        </div>
    );
};

export default ProactiveDisclosureRequestPublication;
