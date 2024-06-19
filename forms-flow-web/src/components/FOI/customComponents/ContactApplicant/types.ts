export interface Template {
  value: string;
  label: string;
  templateid: number;
  text: string;
  disabled: boolean;
}

export type params = {  
  requestNumber: string;
  ministryId: number;
  ministryCode: string;
  requestId: number;
  applicantCorrespondence: Array<any>;
  applicantCorrespondenceTemplates: Array<any>;
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
  handleDraftSave: () => void;
  attachments: Array<any>
  templateInfo: any;
  enableSend: boolean;
}
