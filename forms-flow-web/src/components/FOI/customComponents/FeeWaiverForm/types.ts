export type FeeWaiverFormData = {
    "status": string,
    "formdata": {    
        "requesteddate": string,
        "receiveddate": string,
        "summary": string,
        "recordsdescription": string,
        "type": string, // public or inability
        "inability": {
            "hasproof": boolean,
            "description": string
        },
        "public": {
            "debate": boolean,
            "environment": boolean,
            "disclosing": boolean,
            "understanding": boolean,
            "newpolicy": boolean,
            "financing": boolean,
            "other": string,
            "analysis": string, //partial yes or no
            "description": string

        },
        "disseminate": boolean,
        "abletodisseminate": boolean,
        "narrow": boolean,
        "exceed": boolean,
        "timelines": boolean,
        "previous": boolean,
        "recommendation": {
            "waive": string, //partial yes or no
            "summary": string,
            "amount": number
        }
    }
}

export type params = {
    requestNumber: string;
    requestState: string;
    ministryId: number;
    requestId: number;
    userDetail: {
      groups: string[];
    };
    setCFRUnsaved: Function;
}