export type PDTransactionObject = {
  pdpublicationstatus_id: number;
  pdexemption_id: number | null;
  pdexemptionapproved: boolean | null;
  pagereference: string;
  iaorationale: string;
  oifeedback: string;
  copyrightsevered: boolean;
  publicationdate: string;
  receiveddate: string;
};

export type PDPublicationStatus = {
  pdpublicationstatusid: number;
  name: string;
  isactive: boolean;
};
export type PDExemption = {
  pdexemptionid: number;
  name: string;
  isactive: boolean;
};
