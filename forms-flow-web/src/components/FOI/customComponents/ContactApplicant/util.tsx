
import { formatDateInPst } from "../../../../helper/FOI/helper";
import { any } from "prop-types";

export const renderTemplate = (template: string, content: string, params: Array<any>) => {
  let newTemplate = template.replace("{{content}}", content);
  return applyVariables(newTemplate, params);
}

export const applyVariables = (content: string, params: Array<any>) => {
  let newContent = content;
  params.forEach((item) => {
    newContent = newContent.replaceAll(item.name, item.value);
  });

  return newContent;
}

export const getExtensiondetails = (requestExtensions:any, type: string) => {
    if (requestExtensions && requestExtensions.length >0) {
      let recentExtension = requestExtensions[0];
      if (recentExtension["extensiontype"] === "Public Body"  && recentExtension["extensionstatus"] == "Approved") {
        return [recentExtension["extendedduedays"], recentExtension["extendedduedate"], recentExtension["extensionreson"]]
      } else if (recentExtension["extensiontype"] === "OIPC"  && recentExtension["extensionstatus"] == "Approved") {
        return [recentExtension["approvednoofdays"], recentExtension["extendedduedate"], recentExtension["extensionreson"], recentExtension["created_at"], recentExtension["extensionreasonid"], recentExtension["decisiondate"]
      ]
      }
    }    
    return ["","","","","",""]
}

export const getExtensionType = (requestExtensions: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let pbExtension =  getExtensiondetails(requestExtensions, "Public Body");
  return pbExtension[0] ? "PB" : oipcExtension[0] ? "OIPC" : "NA";
}

export const getTemplateVariables = (requestDetails: any, requestExtensions:any, templateInfo: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let pbExtension =  getExtensiondetails(requestExtensions, "Public Body");

  // Find the record that matches the criteria for already taken a time extension under section 10(1), excluding the most recent record
  const filteredOutLatestExtensions = findLatestMatchingTimeExtension(requestExtensions, reasonsToCheck);

  return [
    {name: "{{axisRequestId}}", value: requestDetails.axisRequestId},
    {name: "{{title}}", value: templateInfo?.label || ""},
    {name: "{{firstName}}", value: requestDetails.firstName},
    {name: "{{lastName}}", value: requestDetails.lastName},
    {name: "{{assignedToFirstName}}", value: requestDetails.assignedToFirstName || ""},
    {name: "{{assignedToLastName}}", value: requestDetails.assignedToLastName || ""},
    {name: "{{assignedGroup}}", value: requestDetails.assignedGroup},
    {name: "{{assignedGroupEmail}}", value: requestDetails.assignedGroupEmail},
    {name: "{{ffaurl}}", value: requestDetails.ffaurl},
    {name: "{{description}}", value: requestDetails.description},
    {name: "{{selectedMinistry}}", value: requestDetails?.selectedMinistries[0].name},
    {name: "{{pbExtensionDueDays}}", value: pbExtension[0]},
    {name: "{{pbExtensionDueDate}}", value: pbExtension[1]},
    {name: "{{pbExtensionReason}}", value: getMappedValue("pbextensionreason", pbExtension[2])}, 
    {name: "{{pbExtensionBody}}", value: "public body"}, 
    {name: "{{requestid_visibility}}", value: isRequestInfoVisible(templateInfo)},
    {name:"{{currentDate}}", value: formatDateInPst(new Date(),"MMM dd yyyy")},
    {name:"{{arcsNumber}}", value: requestDetails.requestType === "general" ? 30 : 40},
    {name: "{{oipcExtensionDueDays}}", value: oipcExtension[0]}, 
    {name: "{{oipcExtensionDueDates}}", value: oipcExtension[1]}, 
    {name: "{{oipcExtensionReason}}", value: oipcExtension[2]}, 
    {name: "{{oipcExtensionNotiDate}}", value: oipcExtension[5]},
    {name: "{{oipcOriginalReceivedDate}}", value: requestDetails.receivedDate},
    {name: "{{oipcOriginalDueDate}}", value: requestDetails.originalDueDate},
    {name: "{{sectionID}}", value: mapSectionWithExtensionReasonId(oipcExtension[4])},
    {name: "{{takenExtensionStatus}}", value: isAlreadyTakenTimeExtension(filteredOutLatestExtensions)},
    {name: "{{filteredExtensionDate}}", value: filteredOutLatestExtensions ? filteredOutLatestExtensions.extendedduedate : ""},
    {name: "{{filteredExtensionDueDays}}", value: filteredOutLatestExtensions ? filteredOutLatestExtensions.extendedduedays : ""},
    {name: "{{oipcComplaintStatus}}", value: oipcComplaintCheck(requestDetails.oipcdetails)},
  ];
  
}

export const isRequestInfoVisible = (templateInfo: any) => {
  if (templateInfo?.value === "EXTENSIONS-PB") {
    return "none";
  }
  return "block";
}

export const isFeeTemplateDisabled = (currentCFRForm: any, template: any) => {
  if (template.name === 'PAYONLINE') {
    return currentCFRForm.status !== 'approved' || ("estimatepaymentmethod" in currentCFRForm.feedata && currentCFRForm.feedata.actualtotaldue > 0)
  } else if (template.name === 'PAYOUTSTANDING') {
    return currentCFRForm.status !== 'approved' || !("estimatepaymentmethod" in currentCFRForm.feedata) || currentCFRForm.feedata.balanceremaining <= 0 || currentCFRForm.feedata.actualtotaldue <= 0
  }
  return false
}

/*
Potentially this can be a own utility class of its own.
*/
const MappedDataList = Object.freeze({

  pbExtensionReasons : [
  {"key":"Public Body - Applicant Consent", "value":"Thank you for consenting to an extension"},
  {"key":"Public Body - Consultation" , "value":"Your request requires consultation with a third party or other public body"},
  {"key": "Public Body - Further Detail from Applicant Required" , "value":"Your request required further detail from you to identify the requested record(s)"},
  {"key":"Public Body - Large Volume and/or Volume of Search", "value":"Your request involves a large volume and/or search for records"},
  {"key":"Public Body - Large Volume and/or Volume of Search and Consultation", "value":"​Your request requires consultation with a third party or other public body and involves a large volume and/or search for records"},
]
})

const getMappedValue = (property: string, propertykey: string) => {
  if(propertykey && property === "pbextensionreason") {
    return MappedDataList.pbExtensionReasons.filter(extension => extension.key == propertykey)[0].value
  }
  return "";
}
// Function to map extension reason id to its textual representation
const mapSectionWithExtensionReasonId = (extensionReasonId: number) => {
  switch (extensionReasonId) {
      case 6:
          return "10(1)(d)"; // 10(1)(d) = Applicant Consent
      case 7:
          return "10(1)(c)"; // 10(1)(c) = Consultation
      case 8:
          return "10(1)(a)"; // 10(1)(a) = Further detail from applicant required
      case 9:
          return "10(1)(b)"; // 10(1)(b) = Large Volume and/or Volume of Search
      default:
          return "";
  }
};

// List of reasons to check already taken a time extension under section 10(1)
const reasonsToCheck = [
  "OIPC - Applicant Consent",
  "OIPC - Consultation",
  "OIPC - Further Detail from Applicant Required",
  "OIPC - Large Volume and/or Volume of Search"
];

// Find the record that matches the criteria for already taken a time extension under section 10(1), excluding the most recent record.
const findLatestMatchingTimeExtension = (requestExtensions: any[], reasonsToCheck: string[]): any | null => {
  const foundObject = requestExtensions
      .filter(extension => extension.extensiontype === "OIPC" && reasonsToCheck.includes(extension.extensionreson) && extension !== requestExtensions[0])
      .find(extension => reasonsToCheck.includes(extension.extensionreson)) || null;

  return foundObject;
};

// Function to check and return "Yes" or "No"
const isAlreadyTakenTimeExtension = (result: any | null): string => {
  return result === null ? "No" : "Yes";
};

// Check if there are any OIPC details.
const oipcComplaintCheck = (oipcdetails: any): string => oipcdetails && oipcdetails.length > 0 ? "Yes" : "No";

