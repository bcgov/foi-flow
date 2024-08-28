import { useSelector } from "react-redux";

const IAOOpenInfoPublishing = ({ data } : any) => {
    const oiExemptions: string[] = useSelector((state : any) => state.foiRequests.oiExemptions);
    const oiPublicationStatuses: string[] = useSelector((state : any) => state.foiRequests.oiPublicationStatuses);

    console.log("exemptions", oiExemptions)
    console.log("publicationstats", oiPublicationStatuses)

    return (
    <>
        <div>
            <h1>Open Information TOP HALF</h1>
        </div>
        <div>
            <h1>Open Information Feedback+Rationale</h1>
        </div>
    </>
    );
}

export default IAOOpenInfoPublishing;