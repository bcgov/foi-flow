
import { FOI_BASE_API_URL } from "./config";

const API = {
  FOI_GET_REQUESTS_API: `${FOI_BASE_API_URL}/api/dashboard`,
  FOI_GET_MINISTRY_REQUESTS_API: `${FOI_BASE_API_URL}/api/dashboard/ministry`,
  FOI_GET_CATEGORIES_API: `${FOI_BASE_API_URL}/api/foiflow/applicantcategories`,
  FOI_GET_PROGRAMAREAS_API: `${FOI_BASE_API_URL}/api/foiflow/programareas`,
  FOI_RAW_REQUEST_API: `${FOI_BASE_API_URL}/api/foirawrequest/<requestid>`,
  FOI_POST_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>`,
  FOI_GET_ASSIGNEDTO_ALLGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees`,
  FOI_GET_ASSIGNEDTO_INTAKEGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees/group/intaketeam`,
  FOI_GET_ASSIGNEDTO_REQUESTTYPELIST_API: `${FOI_BASE_API_URL}/api/foiassignees/<requesttype>`,
  FOI_GET_ASSIGNEDTOGROUPLIST_API: `${FOI_BASE_API_URL}/api/foiassignees/<requesttype>/<curentstate>`,
  FOI_GET_ASSIGNEDTO_MINISTRYGROUP_LIST_API: `${FOI_BASE_API_URL}/api/foiassignees/group/<govcode>ministryteam`,
  FOI_GET_DELIVERY_MODELIST: `${FOI_BASE_API_URL}/api/foiflow/deliverymodes`,
  FOI_GET_RECEIVED_MODELIST: `${FOI_BASE_API_URL}/api/foiflow/receivedmodes`,
  FOI_POST_REQUEST_POST: `${FOI_BASE_API_URL}/api/foirequests`,
  FOI_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>/ministryrequest/<ministryid>`,
  FOI_MINISTRYVIEW_REQUEST_API: `${FOI_BASE_API_URL}/api/foirequests/<requestid>/ministryrequest/<ministryid>/ministry`,
  FOI_RAW_REQUEST_DESCRIPTION: `${FOI_BASE_API_URL}/api/foiaudit/rawrequest/<requestid>/description`,
  FOI_MINISTRY_REQUEST_DESCRIPTION: `${FOI_BASE_API_URL}/api/foiaudit/ministryrequest/<ministryid>/description` 
};

export default API;
