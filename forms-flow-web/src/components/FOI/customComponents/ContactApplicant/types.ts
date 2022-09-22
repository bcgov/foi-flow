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

export type modalParams = {
  modalOpen: boolean;
  handleClose: () => void;
  formHistory: Array<any>
}

export type previewParams = {
  modalOpen: boolean;
  handleClose: () => void;
  handleSave: (emailContent: string) => void;
  innerhtml: string;
  attachments: Array<any>;
  templateInfo: any;
}
