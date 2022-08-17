export type FeeWaiverFormData = {
    status: string,
    formdata: {    
        requesteddate: string,
        receiveddate: string,
        summary: string,
        recordsdescription: string,
        inability: boolean,
        publicinterest: boolean,
        inabilitydetails?: {
            hasproof: any,
            description: string
        },
        publicinterestdetails?: {
            debate: any,
            environment: any,
            disclosing: any,
            understanding: any,
            newpolicy: any,
            financing: any,
            other: string,
            analysis: string, //partial yes or no
            description: string

        },
        disseminate: any,
        abletodisseminate: any,
        narrow: any,
        exceed: any,
        timelines: any,
        previous: any,
        description: string,
        recommendation: {
            waive: string, //partial yes or no
            summary: string,
            amount: number
        },
        decision?: {
            amount: number
        }
    }
}

export type params = {
    requestDescription: string;
    fromDate: string;
    toDate: string;
    requestNumber: string;
    requestState: string;
    ministryId: number;
    requestId: number;
    userDetail: {
      groups: string[];
    };
    setCFRUnsaved: Function;
}