import {FeeWaiverFormData} from "./types";


export const isValidationError = (feeWaiverData : FeeWaiverFormData, newFiles : any) => {
    if(!(!!feeWaiverData?.formdata.requesteddate) || !(!!feeWaiverData?.formdata?.summary) || newFiles.length > 0 ||
        (!feeWaiverData?.formdata.inability && !feeWaiverData?.formdata.publicinterest) || 
            !(!!feeWaiverData?.formdata?.recordsdescription) || 
            (feeWaiverData?.formdata.inability && (typeof feeWaiverData?.formdata?.inabilitydetails.hasproof != "boolean"  || 
                        feeWaiverData?.formdata?.inabilitydetails.hasproof === true && !(!!feeWaiverData?.formdata?.inabilitydetails.description)))||
            (feeWaiverData?.formdata.publicinterest && (typeof feeWaiverData?.formdata?.publicinterestdetails.debate != "boolean" ||
            typeof feeWaiverData?.formdata.publicinterestdetails.environment != "boolean" || typeof feeWaiverData?.formdata.publicinterestdetails.disclosing != "boolean" ||
            typeof feeWaiverData?.formdata.publicinterestdetails.understanding != "boolean" || typeof feeWaiverData?.formdata.publicinterestdetails.newpolicy != "boolean" ||
            typeof feeWaiverData?.formdata.publicinterestdetails.financing != "boolean" || (!(!!feeWaiverData?.formdata.publicinterestdetails.analysis) || 
            feeWaiverData?.formdata.publicinterestdetails.analysis === 'partial' && !(!!feeWaiverData?.formdata.publicinterestdetails.description)))) ||
            typeof feeWaiverData?.formdata.narrow != "boolean" || typeof feeWaiverData?.formdata.exceed != "boolean" || typeof feeWaiverData?.formdata.timelines != "boolean" ||
            typeof feeWaiverData?.formdata.previous != "boolean" ||
            !(!!feeWaiverData?.formdata.recommendation.waive) || !(!!feeWaiverData?.formdata.recommendation.summary)
            )
        return true;
    return false;
}