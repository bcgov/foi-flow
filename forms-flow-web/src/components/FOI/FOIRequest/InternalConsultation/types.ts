// POST/PUT
export type ConsultTransactionObject = {
  fileNumber: string;
  consultAssignedTo?: string | null;
  consultTypeId: number;
  programAreaId: number;
  subjectCode?: string | null;
  dueDate: string; 
};

// GET
export type ConsultTransactionResponse = {
  id: number;
  fileNumber: string;
  consultAssignedTo: string;
  consultDueDate: string;
  consultTypeId: number;
  programAreaId: number;
  programAreaName: string;
  requestStatusId: number;
  requestStatusName: string;
  subjectCode: string;
  created_at: string;
};