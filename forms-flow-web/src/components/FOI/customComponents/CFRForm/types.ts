export type CFRFormData = {
    cfrfeeid?: any;
    formStatus: string;
    amountDue: number;
    amountPaid: number;
    balanceRemaining: number;
    estimates: {
      locating: number;
      producing: number;
      ministryPreparing: number;
      iaoPreparing: number;
      electronicPages: number;
      hardcopyPages: number;
    };
    actual: {
      locating: number;
      producing: number;
      ministryPreparing: number;
      iaoPreparing: number;
      electronicPages: number;
      hardcopyPages: number;
    };
    suggestions: string;
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
