export type CFRFormData = {
    cfrfeeid?: any;
    formStatus: string;
    estimatedTotalDue: number;
    actualTotalDue: number;
    amountPaid: number;
    balanceRemaining: number;
    feewaiverAmount: number;
    refundAmount: number;
    estimates: feeData;
    actual: feeData;
    suggestions: string;
}

export type feeData = {
  locating: number;
  producing: number;
  ministryPreparing: number;
  iaoPreparing: number;
  electronicPages: number;
  hardcopyPages: number;
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

export type modalParams = {
  modalOpen: boolean;
  handleClose: () => void;
  formHistory: Array<any>
}
