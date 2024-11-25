export type CFRFormData = {
    cfrfeeid?: any;
    formStatus: string;
    estimatedTotalDue: number;
    actualTotalDue: number;
    estimatePaymentMethod: string;
    balancePaymentMethod: string;
    amountPaid: number;
    balanceRemaining: number;
    feewaiverAmount: number;
    refundAmount: number;
    estimates: feeData;
    actual: feeData;
    suggestions: string;
    reason: string;
}

export type ApplicationFeeFormData = {
  applicationfeeid?: any;
  applicationFeeStatus: string;
  amountPaid: number;
  paymentSource: string;
  paymentDate: any;
  orderId: string;
  transactionNumber: string;
  receipts: any[];
  refundAmount: number;
  refundDate: any;
  reasonForRefund: string;
  paymentId: number | null;
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
  requestDetails: any;
  ministryId: number;
  requestId: number;
  userDetail: {
    groups: string[];
  };
  setCFRUnsaved: Function;
  handleStateChange: Function;
}

export type modalParams = {
  modalOpen: boolean;
  handleClose: () => void;
  formHistory: Array<any>;
  isMinistry: boolean;
}

export enum FeesSubtabValues {
  APPLICATIONFEE = "APPLICATIONFEE",
  CFRFORM = "CFRFORM"
} 