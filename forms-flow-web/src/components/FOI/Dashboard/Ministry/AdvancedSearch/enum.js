const SearchFilter = Object.freeze({
  REQUEST_DESCRIPTION: "requestdescription",
  RAW_REQUEST_NUM: "rawrequest_num",
  ID_NUM: "idnumber",
  AXIS_REQUEST_NUM: "axisrequest_number",
  APPLICANT_NAME: "applicantname",
  ASSIGNEE_NAME: "ministryassigneename",
  SUBJECT_CODE: "subjectcode",
  OIPC_NUMBER: "oipc_number"
});

const DateRangeTypes = Object.freeze([
  {name: "receivedDate", value: "Received Date"},
  {name: "duedate", value: "Legislated Due Date"},
  {name: "closedate", value: "Closed Date"},
]);

const MappedMinistries = Object.freeze({
  'ECC': ['ECC', 'EDU'],
  'ECS': ['ECS', 'EMLI'],
  'PSE': ['PSE', 'AEST'],
  'HSG': ['HSG', 'MUNI'],
  'CAS': ['BRD', 'CAS'],
  'JED': ['JED', 'JERI'],
  'HTH': ['MMHA', 'HTH'],
})

export {
  SearchFilter,
  DateRangeTypes,
  MappedMinistries
};