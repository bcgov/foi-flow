
import { formatDateInPst, convertDate } from "../../../../helper/FOI/helper";
import { any, instanceOf, number } from "prop-types";
import { fetchDocumentPage, fetchDocumentPageFlags } from "../../../../apiManager/services/FOI/foiRecordServices";

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
      } else if (recentExtension["extensiontype"] === "OIPC") {
        return [recentExtension["approvednoofdays"], recentExtension["extendedduedate"], recentExtension["extensionreson"], recentExtension["created_at"], recentExtension["extensionreasonid"], recentExtension["decisiondate"], recentExtension["extendedduedays"]
      ]
      }
    }    
    return ["","","","","","",""]
}

export const getExtensionType = (requestDetails:any, requestExtensions: any) => {

  if (requestDetails.currentState === "Open") {
    return "NA";
  }

  if (!requestExtensions || requestExtensions.length === 0) {
    return "NA";
  }

  const latestExtension = requestExtensions[0];
  const approvedOIPCExists = requestExtensions.some((ext : any) => ext.extensionstatus === "Approved" && ext.extensiontype === "OIPC");

   // Get the type of the latest extension
  //const { extensiontype, extensionstatus } = requestExtensions[0];

  if (latestExtension.extensionstatus === "Approved" && latestExtension.extensiontype === "OIPC") {
    return "OIPCAPPLICANTCONSENTEXTENSION";
  } else if (latestExtension.extensionstatus === "Pending" && latestExtension.extensiontype === "OIPC") {
    return approvedOIPCExists ? "OIPCSUBSEQUENTTIMEEXTENSION" : "OIPCFIRSTTIMEEXTENSION";
  } else if (latestExtension.extensionstatus === "Approved" && latestExtension.extensiontype === "Public Body") {
    return "PB";
  }

  return "NA";

  // return extensionstatus === "Approved"
  //   ? (extensiontype === "Public Body" ? "PB" : extensiontype === "OIPC" ? "OIPC" : "NA") : "NA";
}

export const getTemplateVariables = (requestDetails: any, requestExtensions: any, responsePackagePdfStitchStatus: any, cfrFeeData: any, templateInfo: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let pbExtension =  getExtensiondetails(requestExtensions, "Public Body");

  // Find the record that matches the criteria for already taken a time extension under section 10(1), excluding the most recent record
  const filteredOutLatestExtensions = findLatestMatchingTimeExtension(requestExtensions, reasonsToCheck);

  const checkFinalPackage = checkRecordReleased(responsePackagePdfStitchStatus)

  const [feeEstimateStatus, feeEstimateDate] = getFeeEstimateInfo(cfrFeeData);

  return [
    {name: "{{axisRequestId}}", value: requestDetails.axisRequestId},
    {name: "{{title}}", value: templateInfo?.label || ""},
    {name: "{{firstName}}", value: requestDetails.firstName},
    {name: "{{lastName}}", value: requestDetails.lastName},
    {name: "{{assignedToFirstName}}", value: requestDetails.assignedToFirstName || ""},
    {name: "{{assignedToLastName}}", value: requestDetails.assignedToLastName || ""},
    {name: "{{assignedGroup}}", value: requestDetails.assignedGroup},
    {name: "{{assignedGroupEmail}}", value: requestDetails.assignedGroupEmail || ""},
    {name: "{{ffaurl}}", value: requestDetails.ffaurl},
    {name: "{{description}}", value: requestDetails.description},
    {name: "{{selectedMinistry}}", value: requestDetails?.selectedMinistries[0].name},
    {name: "{{address}}", value: requestDetails.address},
    {name: "{{dueDate}}", value: convertDate(requestDetails.dueDate)},
    {name: "{{receivedDate}}", value: convertDate(requestDetails.receivedDate)},
    {name: "{{pbExtensionDueDays}}", value: pbExtension[0]},
    {name: "{{pbExtensionDueDate}}", value: pbExtension[1]},
    {name: "{{pbExtensionReason}}", value: getMappedValue("pbextensionreason", pbExtension[2])}, 
    {name: "{{pbExtensionBody}}", value: "public body"}, 
    {name: "{{requestid_visibility}}", value: isRequestInfoVisible(templateInfo)},
    {name: "{{currentDate}}", value: formatDateInPst(new Date(),"MMM dd yyyy")},
    {name: "{{arcsNumber}}", value: requestDetails.requestType === "general" ? 30 : 40},
    {name: "{{oipcExtensionDueDays}}", value: oipcExtension[6] || ""}, 
    {name: "{{oipcExtensionDueDates}}", value:  convertDate(oipcExtension[1])}, 
    {name: "{{oipcExtensionReason}}", value: oipcExtension[2] || ""}, 
    {name: "{{oipcExtensionNotiDate}}", value: oipcExtension[5] || ""},
    {name: "{{oipcOriginalReceivedDate}}", value: convertDate(requestDetails.receivedDate)},
    {name: "{{oipcOriginalDueDate}}", value: convertDate(requestDetails.originalDueDate)},
    {name: "{{oipcCurrentDueDate}}", value: convertDate(requestDetails.dueDate)},
    {name: "{{sectionID}}", value: mapSectionWithExtensionReasonId(oipcExtension[4])},
    {name: "{{takenExtensionStatus}}", value: isAlreadyTakenTimeExtension(filteredOutLatestExtensions)},
    {name: "{{filteredExtensionDate}}", value: filteredOutLatestExtensions ? filteredOutLatestExtensions.extendedduedate : ""},
    {name: "{{filteredExtensionDueDays}}", value: filteredOutLatestExtensions ? filteredOutLatestExtensions.extendedduedays : ""},
    {name: "{{oipcComplaintStatus}}", value: oipcComplaintCheck(requestDetails.oipcdetails)},
    {name: "{{finalPackageStatus}}", value: checkFinalPackage},
    {name: "{{feeEstimateStatus}}", value: displayFeeEstimateInfo(cfrFeeData)},
    {name: "{{feeEstimateDate}}", value: feeEstimateDate},
    {name: "{{fullFeePaidDate}}", value: getFullFeePaidDate(cfrFeeData)},
    {name: "{{feeWaiverDecisionDate}}", value: getFeeWaiverDecisionDate(cfrFeeData)},
    {name: "{{pbExtensionStatus}}", value: displayPBExtension(requestExtensions)},
    //{name: "{{oipcExtensionSection}}", value: await displayOIPCExtensionSection(oipcExtension[4], requestDetails)},
    {name: "{{oipcExtensionList}}", value: displayOIPCExtension(requestExtensions)},
    {name: "{{oipcApplicantConsentSection}}", value: displayApplicantConsentSection(requestExtensions, requestDetails)},
    {name: "{{onlineFormHtmlForAcknowledgementLetter}}", value: renderOnlineFormHTML(requestDetails)},
  ]
}

export const getTemplateVariablesAsync = async (requestDetails: any, requestExtensions: any, responsePackagePdfStitchStatus: any, cfrFeeData: any, templateInfo: any, callback: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let templateVariables = getTemplateVariables(requestDetails, requestExtensions, responsePackagePdfStitchStatus, cfrFeeData, templateInfo);

  templateVariables.push({name: "{{oipcExtensionSection}}", value: await displayOIPCExtensionSection(oipcExtension[4], requestDetails)})

  callback(templateVariables)
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
    return MappedDataList.pbExtensionReasons.filter(extension => extension.key == propertykey)[0]?.value
  }
  return "";
}

// Function to map extension reason id to its textual representation (PB and OIPC combined)
const mapSectionWithExtensionReasonId = (extensionReasonId: number) => {
  switch (extensionReasonId) {
    case 1:
    case 6:
      return "10(1)(d)"; // 10(1)(d) = Public Body - Applicant Consent / OIPC - Applicant Consent
    case 2:
    case 7:
      return "10(1)(c)"; // 10(1)(c) = Public Body - Consultation / OIPC - Consultation
    case 3:
    case 8:
      return "10(1)(a)"; // 10(1)(a) = Public Body - Further detail from applicant required / OIPC - Further detail from applicant required
    case 4:
    case 9:
      return "10(1)(b)"; // 10(1)(b) = Public Body - Large Volume and/or Volume of Search / OIPC - Large Volume and/or Volume of Search
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


// Function to check record release status
const checkRecordReleased = (status: string): string => { return status === "completed" ? "Yes" : "No"; };

const displayFeeEstimateInfo = (data: any[]): string => {
  const result = data.find(
    item => item["cfrfeestatus.description"] === "Approved" && item.feedata.estimatedtotaldue > 0
  );

  const status = result ? "Yes" : "No";
  let htmlString = "";

  if (status === "Yes") {
    const dateSent = result.created_at || "";
    const datePaid = getFullFeePaidDate(data) || "";
    const dateWaiverDecision = getFeeWaiverDecisionDate(data) || "";

    htmlString = `
      <p><strong><span style="font-size: 13px;">Fee Estimate:&nbsp;</span></strong><span style="font-size: 13px;">Yes</span></p>
      <p><strong><span style="font-size: 13px;">Date fee estimate sent:&nbsp;</span></strong><span style="font-size: 13px;">${dateSent}</span></p>
    `;

    if (datePaid) {
      htmlString += `
        <p><strong><span style="font-size: 13px;">Date deposit or full fee paid:&nbsp;</span></strong><span style="font-size: 13px;">${datePaid}</span></p>
      `;
    }

    if (dateWaiverDecision) {
      htmlString += `
        <p><strong><span style="font-size: 13px;">Date of fee waiver decision:&nbsp;</span></strong><span style="font-size: 13px;">${dateWaiverDecision}</span></p>
      `;
    }
  } else {
    htmlString = `
      <p><strong><span style="font-size: 13px;">Fee Estimate:&nbsp;</span></strong><span style="font-size: 13px;">No</span></p>
    `;
  }

  return htmlString;
};

// Function to check fee estimate and get the created_at date for a specific condition
const getFeeEstimateInfo = (data: any[]): [string, string] => {
  const result = data.find(
    item => item["cfrfeestatus.description"] === "Approved" && item.feedata.estimatedtotaldue > 0
  );

  const status = result ? "Yes" : "No";
  const date = result ? result.created_at : "";

  return [status, date];
};

// Function to get the created_at date when the full fee is paid
const getFullFeePaidDate = (data: any[]): string => {
  const result = data.find(
    item => 
      item["cfrfeestatus.description"] === "Approved" && 
      item.feedata.balanceremaining <= 0 && 
      item.feedata.actualtotaldue <= 0
  );

  return result ? result.created_at : "";
};

// Function to get the created_at date when feewaiveramount is greater than 0 and status is Approved
const getFeeWaiverDecisionDate = (data: any[]): string => {
  const result = data.find(
    item => 
      item["cfrfeestatus.description"] === "Approved" && 
      item.feedata.feewaiveramount > 0
  );

  return result ? result.created_at : "";
};

const displayPBExtension = (requestExtensions:any): string => {
  if (requestExtensions && requestExtensions.length > 0) {
    // Filter out only Public Body extensions that are approved
    const pbExtensions = requestExtensions.filter((ext: any) => 
      ext.extensiontype === "Public Body" && ext.extensionstatus === "Approved"
    );

    // Check if there are any PB Extensions
    if (pbExtensions.length > 0) {
      const recentPBExtension = pbExtensions[0]; // Assuming the list is sorted by date with the most recent first

      // Extract variables for the HTML template
      const {
        extendedduedate,
        extendedduedays,
        extensionreson,
        extensionreasonid,
        created_at
      } = recentPBExtension;
    
      // Build the HTML template for "Yes" case
      const htmlTemplate = `
        <p><strong><span style="font-size: 13px;">Public Body Extension:&nbsp;</span></strong><span style="font-size: 13px;">Yes</span></p>
        <p><strong><span style="font-size: 13px;">Date of time extension:&nbsp;</span></strong><span style="font-size: 13px;">${convertDate(extendedduedate)}</span></p>
        <p><strong><span style="font-size: 13px;">Number of days extended:&nbsp;</span></strong><span style="font-size: 13px;">${extendedduedays}</span></p>
        <p><strong><span style="font-size: 13px;">Reason for Extension:section:&nbsp;</span></strong><span style="font-size: 13px;">${mapSectionWithExtensionReasonId(extensionreasonid)}</span></p>
        <p><strong><span style="font-size: 13px;">Date applicant was notified:&nbsp;</span></strong><span style="font-size: 13px;">${convertDate(created_at)}</span></p>
        <p><strong><span style="font-size: 13px;">Applicant complaint about time extension:&nbsp;</span></strong><span style="font-size: 13px;">No</span></p>
      `;

      return htmlTemplate;
    }
  }
  // If no PB Extension is found, return the "No" template
  return `
    <p><strong><span style="font-size: 13px;">Public Body Extension:&nbsp;</span></strong><span style="font-size: 13px;">No</span></p>
  `;
};


const displayOIPCExtension = (requestExtensions:any): string => {
  if (requestExtensions && requestExtensions.length > 0) {
    // Filter out only OIPC extensions that are approved
    const filteredOIPCExtensions = requestExtensions.filter((ext: any) => 
      ext.extensiontype === "OIPC" && ext.extensionstatus === "Approved"
    );

    // Check if there are any OIPC Extensions
    if (filteredOIPCExtensions.length > 0) {
      // Map the extensionreasonid values to their corresponding string values
      const mappedReasons = filteredOIPCExtensions.map((ext: any) =>
        mapSectionWithExtensionReasonId(ext.extensionreasonid)
      );
      // Join the mapped reasons into a comma-separated string
      const reasonsString = mappedReasons.join(", ");  
      return reasonsString;
    }
  }
  // If no OIPC Extension is found, return an empty string
  return ''
};

const displayApplicantConsentSection = (requestExtensions:any, requestDetails:any): string => {
  if (requestExtensions && requestExtensions.length > 0) {
    // Filter out only OIPC extensions that are approved
    const oipcExtensions = requestExtensions.filter((ext: any) => 
      ext.extensiontype === "OIPC" && ext.extensionstatus === "Approved"
    );

    // Check if there are any OIPC Extensions
    if (oipcExtensions.length > 0) {
      const recentOIPCExtension = oipcExtensions[0]; // Assuming the list is sorted by date with the most recent first
      
      // Extract variables for the HTML template
      const { extensionreson } = recentOIPCExtension;
    
      // Build the HTML template based on the extension reason

      if (extensionreson === "OIPC - Applicant Consent") {
        return `
          <p><span style='font-size:13px;font-family:"BC Sans";'>You have the right to ask the Information and Privacy Commissioner to review this decision. &nbsp;I have enclosed information on the review and complaint process.</span></p>
          <p style="margin:0cm;"><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>Sincerely,</span></p>
          <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
          <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'></span><span style='font-size:13px;font-family:"BC Sans";'>${requestDetails.firstName}&nbsp;${requestDetails.lastName},&nbsp;</span><span style='font-size:13px;font-family:"BC Sans";'>IAO Position Title</span><span style="font-size:11px;">&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>Information Access Operations</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>Enclosure</span></p><strong><span style='font-size:13px;font-family:"BC Sans";'><br>&nbsp;</span></strong>
          <p><strong><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></strong></p>
          <p style="text-align: center;"><span style="font-size: 13px; "><strong>How to Request a Review with the Office of the Information and Privacy Commissioner </strong></span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";text-align: center;'>If you have any questions regarding your request please contact the analyst assigned to your file. The analyst’s name and telephone number are listed in the attached letter. </span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";text-align: center;'>Pursuant to section 52 of the Freedom of Information and Protection of Privacy Act (FOIPPA), you may ask the Office of the Information and Privacy Commissioner to review any decision, act, or failure to act with regard to your request under FOIPPA.</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";text-align: center;'><strong>Please note that you have 30 business days to file your review with the Office of the Information and Privacy Commissioner. In order to request a review please write to: </strong></span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p style="text-align: center;"><span style='font-size:13px;font-family:"BC Sans";'>Information and Privacy Commissioner</span></p>
          <p style="text-align: center;"><span style='font-size:13px;font-family:"BC Sans";'>PO Box 9038 Stn Prov Govt</span></p>
          <p style="text-align: center;"><span style='font-size:13px;font-family:"BC Sans";'>Victoria BC  V8W 9A4 </span></p>
          <p style="text-align: center;"><span style='font-size:13px;font-family:"BC Sans";'>Telephone 250 387-5629	Fax 250 387-1696</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>If you request a review, please provide the Commissioner's Office with: </span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. A copy of your original request; </span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. A copy of our response; and </span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. The reasons or grounds upon which you are requesting the review. </span></p>
        `;
      } else {
        return `
          <p><span style='font-size:13px;font-family:"BC Sans";'>Sincerely,</span></p>
          <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
          <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'></span><span style='font-size:13px;font-family:"BC Sans";'>${requestDetails.firstName}&nbsp;${requestDetails.lastName},&nbsp;</span><span style='font-size:13px;font-family:"BC Sans";'>IAO Position Title</span><span style="font-size:11px;">&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>Information Access Operations</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>&nbsp;</span></p>
          <p><span style='font-size:13px;font-family:"BC Sans";'>Enclosure</span></p><strong><span style='font-size:13px;font-family:"BC Sans";'><br>&nbsp;</span></strong>
        `;
      }
    }
  }
  // If no OIPC Extension is found, return the "No" template
  return ``;
};


const fetchTotalPageCount = (ministryId : number) => {
  const dispatch = () => {};

  return new Promise((resolve, reject) => {
    fetchDocumentPage(ministryId, (err : any, res : any) => {
      if (!err) {
        // Sum the page counts
        const totalPageCount = res.data.reduce((sum : any, item : any) => sum + (item.pagecount || 0), 0);
        
        resolve(totalPageCount || null);

      } else {
        reject(err);
      }
    })(dispatch);
  });
};

const fetchConsultPageFlag = (ministryId : number) : Promise<any> => {
  const dispatch = () => {};

  return new Promise((resolve, reject) => {
    fetchDocumentPageFlags(ministryId, (err : any, res : any) => {
      if (!err) {
        resolve(res.data || null);
      } else {
        reject(err);
      }
    })(dispatch);
  });
};

const displayOIPCExtensionSection = async (extensionId: number, requestDetails: any) => {
  switch (mapSectionWithExtensionReasonId(extensionId)) {
    
    case "10(1)(a)":
    
    return `
    <p><strong><span style="font-size: 13px;">10(1)(a) Insufficient detail</span></strong></p>
    <p><span style="font-size: 13px;">A copy of the original request is included. It does not provide sufficient detail to proceed with the request. <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> Satisfactory clarification from the applicant was not obtained within 60 business days (or 30 business days if the public body’s time extension was not taken): &nbsp;<strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> </span></p>
`;
    case "10(1)(b)":

    let totalPageCount = await fetchTotalPageCount(requestDetails.id);
    
    return `
    <p><strong><span style="font-size: 13px;">10(1)(b) Volume of records </span></strong></p>
    <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
    <p><strong><span style="font-size: 13px;">Approximate page count:&nbsp;</span></strong><span style="font-size: 13px;">${totalPageCount}</span></p>
    <p><strong><span style="font-size: 13px;">Number of pages searched:&nbsp;</span></strong><span style="font-size: 13px;"> </span></p>
    <p><strong><span style="font-size: 13px;">Number of program areas searched: &nbsp;</span></strong><span style="font-size: 13px;"> </span></p>
    <p><strong><span style="font-size: 13px;">Total search time:&nbsp;</span></strong><span style="font-size: 13px;"> </span></p>
    <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
    <p><strong><span style="font-size: 13px;">UNREASONABLE INTERFERENCE WITH THE OPERATIONS OF THE PUBLIC BODY</span></strong></p>
    <p><span style="font-size: 13px;">Meeting the current legislated due date would unreasonably interfere with the public body's operations. <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> </span></p>
    <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
    <p><strong><span style="font-size: 13px;">Current status</span></strong></p> 
    <p><span style="font-size: 13px;">Please describe the current status of processing this request and any other relevant information:<strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> </span></p>`;

    case "10(1)(c)":

    const consultPageFlag = await fetchConsultPageFlag(requestDetails.id);

    const htmlConsultContent = consultPageFlag && Array.isArray(consultPageFlag)
      ? consultPageFlag.map((item: any) => `
        <p><strong><span style="font-size: 13px;">Consultee: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_name || ''}</span></p>
        <p><strong><span style="font-size: 13px;">Consultation page count: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_page_count  || ''}</span></p>
        <p><strong><span style="font-size: 13px;">Consultation Date: &nbsp;</span></strong><span style="font-size: 13px;">${convertDate(item.consultation_date)  || ''}</span></p><p><span>&nbsp;</span></p>
      `).join('')
      : "";

      return `
      <p><strong><span style="font-size: 13px;">10(1)(c) Time for consultation</span></strong></p>
      <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
      ${htmlConsultContent}
      <p><strong><span style="font-size: 13px;">Why is consultation necessary to decide access?</span></strong></p>
      <p>
          <span>
          <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
          </span>
      </p><p><span>&nbsp;</span></p>
      <p><strong><span style="font-size: 13px;">What is the third party or public body’s interest in the record?</span></strong></p>
      <p>
          <span>
          <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
          </span>
      </p><p><span>&nbsp;</span></p>
      <p><strong><span style="font-size: 13px;">Current status of the consultation, including efforts made to obtain a response to the consultation and expected return date:</span></strong></p>
      <p>
          <span>
          <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
          </span>
      </p><p><span>&nbsp;</span></p>
      <p><span style="font-size: 13px;">10(2)(b)</span></p>
      <p><strong><span style="font-size: 13px;">Explain why it would be fair and reasonable for the Commissioner to grant a time extension. Include a chronology of the processing of the request and an explanation for any delays: </span></strong></p>
      <p><strong><span style="font-size: 13px;">&lt;insert some indication the analyst needs to populate this area&gt;</span></strong></p>
      `;

    default:
      return "";
  }
};

const renderOnlineFormHTML = (requestDetails:any): string => {
  if (requestDetails.receivedMode !== "Online Form") {
    // Return the HTML content when the request mode is NOT "Online Form".
    return `
        <p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p><p><span style='font-size:13px;font-family:"BC Sans";'>You submitted your request outside of our online process. For future reference, you can submit both personal and general requests at: <a href="https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/freedom-of-information"><span style="font-size: 13px; ">https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/open-government/open-information/freedom-of-information.</span></a>Using the online process is a fast, easy and secure way to submit your Freedom of Information (FOI) request. It also ensures that we receive the information required to open your request. The webpage also includes frequently asked questions, additional information regarding the FOI process, and links to previously completed FOI requests and proactively released government records. </span></p>
    `;
  } 
  return ''
};
