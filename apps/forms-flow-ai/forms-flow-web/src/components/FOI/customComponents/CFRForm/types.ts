export type CFRFormData = {
    formStatus: string;
    amountDue: number;
    amountPaid: number;
    estimates: {
      locating: number;
      producing: number;
      preparing: number;
      electronicPages: number;
      hardcopyPages: number;
    };
    actual: {
      locating: number;
      producing: number;
      preparing: number;
      electronicPages: number;
      hardcopyPages: number;
    };
    suggestions: string;
}

export type params = {
  requestNumber: string;
  ministryId: number;
  requestId: number;
  userDetail: {
    groups: string[];
  };
}
