export type CFRFormData = {
    requestNumber: string;
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
