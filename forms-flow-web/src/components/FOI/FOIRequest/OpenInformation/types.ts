export type OITransactionObject = {
  oipublicationstatus_id: number;
  oiexemption_id: number | null;
  oiexemptionapproved: boolean | null;
  pagereference: string;
  iaorationale: string;
  oifeedback: string;
  copyrightsevered: boolean;
  publicationdate: string;
  oiexemptiondate: string;
};

export type OIPublicationStatus = {
  oipublicationstatusid: number;
  name: string;
  isactive: boolean;
};
export type OIExemption = {
  oiexemptionid: number;
  name: string;
  isactive: boolean;
};
