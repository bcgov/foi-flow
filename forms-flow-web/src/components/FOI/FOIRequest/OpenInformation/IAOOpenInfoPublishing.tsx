import { useSelector } from "react-redux";
import Grid from "@material-ui/core/Grid";

type OIExemption = {
    "oiexemptionid": number,
    "name": string,
    "isactive": boolean
}
type OIPublicationStatus = {
    "oipublicationstatusid": number,
    "name": string,
    "isactive": boolean
}

const IAOOpenInfoPublishing = ({ requestNumber, } : any) => {
    const oiExemptions: OIExemption[] = useSelector((state : any) => state.foiRequests.oiExemptions);
    const oiPublicationStatuses: OIPublicationStatus[] = useSelector((state : any) => state.foiRequests.oiPublicationStatuses);

    console.log("exemptions", oiExemptions)
    console.log("publicationstats", oiPublicationStatuses)
    
    return (
        <Grid
            container
            direction="row"
            alignItems="flex-start"
            spacing={1}
        >
            <Grid item xs={6}>
                <h1 className="foi-review-request-text foi-ministry-requestheadertext">
                    {requestNumber ? `Request #${requestNumber}` : ""}
                </h1>
            </Grid>
        </Grid>
    );
}

export default IAOOpenInfoPublishing;