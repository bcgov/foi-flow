export type PDTransactionObject = {
  oipublicationstatus_id: number;
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
  oipublicationstatusid: number;
  name: string;
  isactive: boolean;
};
export type PDExemption = {
  pdexemptionid: number;
  name: string;
  isactive: boolean;
};
