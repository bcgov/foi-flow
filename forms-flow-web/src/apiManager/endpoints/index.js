
import { FOI_BASE_API_URL, AXIS_API_URL } from "./config";

const API = {
  FOI_GET_REQUESTS_API: `${FOI_BASE_API_URL}/api/dashboard`,
  FOI_GET_MINISTRY_REQUESTS_API: `${FOI_BASE_API_URL}/api/dashboard/ministry`,
  FOI_GET_REQUESTS_PAGE_API: `${FOI_BASE_API_URL}/api/dashboardpagination`,
  FOI_GET_MINISTRY_REQUESTS_PAGE_API: `${FOI_BASE_API_URL}/api/dashboardpagination/ministry`,
  FOI_GET_CATEGORIES_API: `${FOI_BASE_API_URL}/api/foiflow/applicantcategories`,
  FOI_GET_PROGRAMAREAS_API: `${FOI_BASE_API_URL}/api/foiflow/programareas`,
  FOI_GET_PROGRAMAREAS_FORUSER_API: `${FOI_BASE_API_URL}/api/foiflow/programareasforuser`,
  FOI_RAW_REQUEST_API: `${FOI_BASE_API_URL}/api/foirawrequest/<requestid>`,
  FOI_POST_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>`,
  FOI_GET_ASSIGNEDTO_ALLGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees`,
  FOI_GET_ASSIGNEDTO_INTAKEGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees/group/intaketeam`,
  FOI_GET_ASSIGNEDTO_REQUESTTYPELIST_API: `${FOI_BASE_API_URL}/api/foiassignees/<requesttype>`,
  FOI_GET_ASSIGNEDTOGROUPLIST_API: `${FOI_BASE_API_URL}/api/foiassignees/<requesttype>/<curentstate>`,
  FOI_GET_ASSIGNEDTOGROUPLIST_WITHGOVCODE_API: `${FOI_BASE_API_URL}/api/foiassignees/<requesttype>/<curentstate>/<bcgovcode>`,
  FOI_GET_PROCESSINGTEAMLIST_API: `${FOI_BASE_API_URL}/api/foiassignees/processingteams/<requesttype>`,
  FOI_GET_ASSIGNEDTO_MINISTRYGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees/group/<govcode>ministryteam`,
  FOI_GET_DELIVERY_MODELIST: `${FOI_BASE_API_URL}/api/foiflow/deliverymodes`,
  FOI_GET_RECEIVED_MODELIST: `${FOI_BASE_API_URL}/api/foiflow/receivedmodes`,
  FOI_POST_REQUEST_POST: `${FOI_BASE_API_URL}/api/foirequests`,
  FOI_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>/ministryrequest/<ministryid>`,
  FOI_MINISTRYVIEW_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>/ministryrequest/<ministryid>/ministry`,
  FOI_RAW_REQUEST_DESCRIPTION: `${FOI_BASE_API_URL}/api/foiaudit/rawrequest/<requestid>/description`,
  FOI_MINISTRY_REQUEST_DESCRIPTION: `${FOI_BASE_API_URL}/api/foiaudit/ministryrequest/<ministryid>/description`,
  FOI_MINISTRY_DIVISIONALSTAGES: `${FOI_BASE_API_URL}/api/foiflow/divisions/<bcgovcode>`,
  FOI_POST_RAW_REQUEST_WATCHERS: `${FOI_BASE_API_URL}/api/foiwatcher/rawrequest`,
  FOI_GET_RAW_REQUEST_WATCHERS: `${FOI_BASE_API_URL}/api/foiwatcher/rawrequest/<requestid>`,
  FOI_POST_MINISTRY_REQUEST_WATCHERS: `${FOI_BASE_API_URL}/api/foiwatcher/ministryrequest`,
  FOI_GET_MINISTRY_REQUEST_WATCHERS: `${FOI_BASE_API_URL}/api/foiwatcher/ministryrequest/<ministryid>`,
  FOI_GET_CLOSING_REASONS: `${FOI_BASE_API_URL}/api/foiflow/closereasons`,
  FOI_POST_OSS_HEADER: `${FOI_BASE_API_URL}/api/foiflow/oss/authheader`,

  FOI_POST_COMMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foicomment/rawrequest`,
  FOI_GET_COMMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foicomment/rawrequest/<requestid>`,
  FOI_PUT_COMMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foicomment/rawrequest/<requestid>`,
  FOI_DELETE_COMMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foicomment/rawrequest/<commentid>/disable`,

  FOI_POST_COMMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foicomment/ministryrequest`,
  FOI_GET_COMMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foicomment/ministryrequest/<ministryrequestid>`,
  FOI_PUT_COMMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foicomment/ministryrequest/<ministryrequestid>`,
  FOI_DELETE_COMMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foicomment/ministryrequest/<commentid>/disable`,

  FOI_ATTACHMENTS_RAWREQUEST: `${FOI_BASE_API_URL}/api/foidocument/rawrequest/<requestid>`,
  FOI_ATTACHMENTS_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foidocument/ministryrequest/<ministryrequestid>`,

  FOI_RENAME_ATTACHMENTS_RAWREQUEST: `${FOI_BASE_API_URL}/api/foidocument/rawrequest/<requestid>/documentid/<documentid>/rename`,
  FOI_RENAME_ATTACHMENTS_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foidocument/ministryrequest/<ministryrequestid>/documentid/<documentid>/rename`,
  FOI_REPLACE_ATTACHMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foidocument/rawrequest/<requestid>/documentid/<documentid>/replace`,
  FOI_REPLACE_ATTACHMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foidocument/ministryrequest/<ministryrequestid>/documentid/<documentid>/replace`,
  FOI_DELETE_ATTACHMENT_RAWREQUEST: `${FOI_BASE_API_URL}/api/foidocument/rawrequest/<requestid>/documentid/<documentid>/delete`,
  FOI_DELETE_ATTACHMENT_MINISTRYREQUEST: `${FOI_BASE_API_URL}/api/foidocument/ministryrequest/<ministryrequestid>/documentid/<documentid>/delete`,

  FOI_GET_NOTIFICATIONS: `${FOI_BASE_API_URL}/api/foinotifications`,
  FOI_DELETE_NOTIFICATION: `${FOI_BASE_API_URL}/api/foinotifications/<idNumber>/<notificationId>`,
  FOI_DELETE_ALL_NOTIFICATIONS: `${FOI_BASE_API_URL}/api/foinotifications/<type>`,

  FOI_GET_EXTENSION_REASONS: `${FOI_BASE_API_URL}/api/foiflow/extensionreasons`,
  FOI_POST_AXIS_EXTENSIONS: `${FOI_BASE_API_URL}/api/foiextension/axisrequest/<ministryrequestid>`,
  FOI_POST_EXTENSION: `${FOI_BASE_API_URL}/api/foiextension/foirequest/<requestid>/ministryrequest/<ministryrequestid>`,
  FOI_POST_UPDATE_EXTENSION: `${FOI_BASE_API_URL}/api/foiextension/foirequest/<requestid>/ministryrequest/<ministryrequestid>/extension/<extensionid>/edit`,
  FOI_POST_DELETE_EXTENSION: `${FOI_BASE_API_URL}/api/foiextension/foirequest/<requestid>/ministryrequest/<ministryrequestid>/extension/<extensionid>/delete`,

  FOI_GET_EXTENSIONS: `${FOI_BASE_API_URL}/api/foiextension/ministryrequest/<ministryrequestid>`,
  FOI_GET_EXTENSION: `${FOI_BASE_API_URL}/api/foiextension/<extensionId>`,

  FOI_GET_CFR_FORM: `${FOI_BASE_API_URL}/api/foicfrfee/ministryrequest/<ministryrequestid>`,
  FOI_POST_CFR_FORM: `${FOI_BASE_API_URL}/api/foicfrfee/foirequest/<requestid>/ministryrequest/<ministryrequestid>`,
  FOI_POST_CFR_FORM_IAO: `${FOI_BASE_API_URL}/api/foicfrfee/foirequest/<requestid>/ministryrequest/<ministryrequestid>/sanction`,

  FOI_POST_EMAIL_CORRESPONDENCE: `${FOI_BASE_API_URL}/api/foiflow/applicantcorrespondence/<requestid>/<ministryrequestid>`,
  FOI_GET_EMAIL_CORRESPONDENCE: `${FOI_BASE_API_URL}/api/foiflow/applicantcorrespondence/<requestid>/<ministryrequestid>`,
  FOI_GET_EMAIL_CORRESPONDENCE_TEMPLATES: `${FOI_BASE_API_URL}/api/foiflow/applicantcorrespondence/templates`,

  FOI_GET_OPENED_MINISTRIES: `${FOI_BASE_API_URL}/api/foirawrequest/<requestid>/fields?names=ministries`,

  FOI_GET_ADVANCED_SEARCH: `${FOI_BASE_API_URL}/api/advancedsearch`,

  FOI_CHECK_AXIS_REQUEST_ID: `${FOI_BASE_API_URL}/api/foirawrequest/axisrequestid/<axisrequestid>`,
  
  FOI_GET_AXIS_REQUEST_DATA: `${AXIS_API_URL}/api/RequestSearch/<axisrequestid>`,

  FOI_REQUEST_ASSIGNEE_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>/ministryrequest/<ministryid>/<usertype>/assignee`,
  FOI_RAWREQUEST_ASSIGNEE_API:  `${FOI_BASE_API_URL}/api/foirawrequest/<requestid>/assignee`,

  FOI_GET_S3DOCUMENT_PRESIGNEDURL:`${FOI_BASE_API_URL}/api/foiflow/oss/presigned`,

  FOI_GET_SUBJECT_CODELIST: `${FOI_BASE_API_URL}/api/foiflow/subjectcodes`,
  FOI_POST_RAWREQUEST_RESTRICTION: `${FOI_BASE_API_URL}/api/foirawrequest/restricted/<requestid>`,
  FOI_POST_MINISTRYREQUEST_RESTRICTION: `${FOI_BASE_API_URL}/api/foirequests/restricted/<ministryrequestid>/<type>`,

  FOI_GET_RESTRICTED_RAWREQUEST_TAG_LIST: `${FOI_BASE_API_URL}/api/foicomment/rawrequest/<requestid>/restricted`,
  FOI_GET_RESTRICTED_MINISTRYREQUEST_TAG_LIST: `${FOI_BASE_API_URL}/api/foicomment/ministryrequest/<ministryrequestid>/restricted`


};
export default API;
