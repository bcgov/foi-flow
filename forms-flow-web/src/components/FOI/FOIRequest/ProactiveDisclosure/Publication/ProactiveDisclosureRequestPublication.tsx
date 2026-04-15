import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import ProactiveDisclosureRequestPublicationMain from "./ProactiveDisclosureRequestPublicationMain";
import OpenInfoConfirmationModal from "../../OpenInformation/OpenInfoConfirmationModal";
import OpenInfoHeader from "../../OpenInformation/OpenInfoHeader";
import { saveFOIProactiveDisclosureRequest, fetchFOIProactiveDisclosureRequest, publishFOIProactiveDisclosureRequest, unpublishFOIProactiveDisclosureRequest } from "../../../../../apiManager/services/FOI/foiProactiveDisclosureServices";
import { PDPublicationStatus, PDTransactionObject } from "./types";
import { OIStates, OIPublicationStatuses } from "../../../../../helper/openinfo-helper";
import { formatDateInPst } from "../../../../../helper/FOI/helper";
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
    let foiPDTransactionData = useSelector(
        (state: any) => state.foiRequests.foiOpenInfoRequest
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
        if (foiPDTransactionData) setPdPublicationData(foiPDTransactionData);
    }, [foiPDTransactionData]);

    //Functions
    const handlePDDataChange = (
        value: number | string | boolean,
        pdDataKey: string
    ) => {
        if (!isDataEdited) {
            setIsDataEdited(true);
        }
         if (pdDataKey === "publicationdate") {
            setConfirmationModal((prev: any) => ({
                ...prev,
                show: true,
                title: "Change Publication Date",
                description: `This proactive disclosure will be scheduled for publication on ${value}. Are you sure you want to proceed?`,
                message: "",
                confirmButtonTitle: "Confirm",
                confirmationData: value,
            }));
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
            oipublicationstatus_id: OIPublicationStatuses.Publish,
            publicationdate: publicationdate
        };
        dispatch(
            publishFOIProactiveDisclosureRequest(
                foiministryrequestid,
                foirequestid,
                formattedData,
                (err: any, _res: any) => {
                    if (!err) {
                        const toastMsg = _res.status === 202 ? "FOI Proactive Disclosure request has successfully been sent for publishing." : "No data found to publish for this FOI Proactive Disclosure request.";
                        toast.update(toastID, {
                            type: "success",
                            render:
                                 toastMsg,
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
                        toast.update(toastID, {
                            type: "error",
                            render:
                                 "Temporarily unable to publish FOI Proactive Disclosure request. Please try again in a few minutes.",
                            position: "top-right",
                            isLoading: false,
                            autoClose: 3000,
                            hideProgressBar: true,
                            closeOnClick: true,
                            pauseOnHover: true,
                            draggable: true,
                            progress: undefined,
                        });
                    }
                }
            )
        );
    }

    const unpublish = (): any => {
        const toastID = toast.loading("Unpublishing FOI Proactive Disclosure request...");
        const formattedData = {
            ...pdPublicationData,
            oipublicationstatus_id: OIPublicationStatuses.UnpublishRequest,
        };
        dispatch(
            unpublishFOIProactiveDisclosureRequest(
                foiministryrequestid,
                foirequestid,
                formattedData,
                (err: any, _res: any) => {
                    if (!err) {
                        const toastMsg = _res.status === 202 ? "FOI Proactive Disclosure request has successfully been sent for unpublishing." : "No data found to unpublish for this FOI Proactive Disclosure request.";
                        toast.update(toastID, {
                            type: "success",
                            render:
                                 toastMsg,
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
                        toast.update(toastID, {
                            type: "error",
                            render:
                                 "Temporarily unable to unpublish FOI Proactive Disclosure request. Please try again in a few minutes.",
                            position: "top-right",
                            isLoading: false,
                            autoClose: 3000,
                            hideProgressBar: true,
                            closeOnClick: true,
                            pauseOnHover: true,
                            draggable: true,
                            progress: undefined,
                        });
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

    const disableUnpublish = (): boolean => {
        const isPDPublished = currentPDRequestState === "Published";
        if (!isPDPublished) {
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
            description: "Are you sure you want to Publish this request now?",
            message: "Your Proactive Disclosure request will be sent to our Publication Service for publishing. Any previously scheduled publication date will be overridden. You will receive a notification shortly once your request has been published, and the request state will be moved to 'Published'.",
            confirmButtonTitle: "Publish Now",
        }));
    }
    const handleUnpublish = () => {
        setConfirmationModal((prev: any) => ({
            ...prev,
            show: true,
            title: "Unpublish Request",
            description: "Are you sure you want to Unpublish this request?",
            message: "Your Proactive Disclosure request will be sent to our Publication Service for unpublishing. You will receive a notification shortly once your request has been unpublished and the request state will be moved to 'Unpublished'.",
            confirmButtonTitle: "Unpublish",
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
                foiministryrequestid={foiministryrequestid}
                foirequestid={foirequestid}
                toast={toast}
                handleOIDataChange={handlePDDataChange}
            />
            <ProactiveDisclosureRequestPublicationMain
                pdPublicationData={pdPublicationData}
                handlePDDataChange={handlePDDataChange}
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
                onClick={() => saveData()}
            >
                Save
            </button>
            {currentPDRequestState === "Published" ?
            <button
                type="button"
                disabled={disableUnpublish()}
                className="btn btn-bottom"
                onClick={handleUnpublish}
            >
                Unpublish
            </button>
            : <button
                type="button"
                disabled={disablePublish()}
                className="btn btn-bottom"
                onClick={handlePublishNow}
            >
                Publish Now
            </button> 
            }
            <OpenInfoConfirmationModal
                modal={confirmationModal}
                confirm={(confirmationModal.title === "Change Publication Date" && handleDateConfirmation)
                    || (confirmationModal.title === "Publish Files Now" && publishConfirmation) ||
                    (confirmationModal.title === "Unpublish Request" && unpublish)
                }
                setModal={setConfirmationModal}
            />
        </div>
    );
};

export default ProactiveDisclosureRequestPublication;
