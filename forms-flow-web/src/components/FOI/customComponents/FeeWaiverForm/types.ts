export type FeeWaiverFormData = {
    status: string,
    formdata: {    
        requesteddate: string,
        receiveddate: string,
        summary: string,
        recordsdescription: string,
        inability: boolean,
        publicinterest: boolean,
        inabilitydetails: {
            hasproof: boolean,
            description: string
        },
        publicinterestdetails: {
            debate: boolean,
            environment: boolean,
            disclosing: boolean,
            understanding: boolean,
            newpolicy: boolean,
            financing: boolean,
            other: string,
            analysis: string, //partial yes or no
            description: string

        },
        disseminate: boolean,
        abletodisseminate: boolean,
        narrow: boolean,
        exceed: boolean,
        timelines: boolean,
        previous: boolean,
        description: string,
        recommendation: {
            waive: string, //partial yes or no
            summary: string,
            amount: number
        }
        decision: {
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