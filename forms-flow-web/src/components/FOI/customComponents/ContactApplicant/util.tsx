
import { formatDateInPst, convertDate } from "../../../../helper/FOI/helper";
import { any, number } from "prop-types";
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
        return [recentExtension["approvednoofdays"], recentExtension["extendedduedate"], recentExtension["extensionreson"], recentExtension["created_at"], recentExtension["extensionreasonid"], recentExtension["decisiondate"]
      ]
      }
    }    
    return ["","","","","",""]
}

export const getExtensionType = (requestExtensions: any) => {
  if (!requestExtensions || requestExtensions.length === 0) {
    return "NA";
  }

  const latestExtension = requestExtensions[0];
  const approvedOIPCExists = requestExtensions.some((ext : any) => ext.extensionstatus === "Approved" && ext.extensiontype === "OIPC");

   // Get the type of the latest extension
  //const { extensiontype, extensionstatus } = requestExtensions[0];

  if (latestExtension.extensionstatus === "Approved" && latestExtension.extensiontype === "OIPC") {
    if (latestExtension.extensionreson === "OIPC - Applicant Consent") {
      return "OIPCAPPLICANTCONSENTEXTENSION";
    }
    
  } else if (latestExtension.extensionstatus === "Approved" && latestExtension.extensiontype === "Public Body") {
    console.log("Returning PB");
    return "PB";
  } else if (latestExtension.extensionstatus === "Pending") {
    console.log("approvedOIPCExists : ",approvedOIPCExists)
    return approvedOIPCExists ? "OIPCSUBSEQUENTTIMEEXTENSION" : "OIPCFIRSTTIMEEXTENSION";
  }

  return "NA";

  // return extensionstatus === "Approved"
  //   ? (extensiontype === "Public Body" ? "PB" : extensiontype === "OIPC" ? "OIPC" : "NA") : "NA";
}

export const getTemplateVariables = async (requestDetails: any, requestExtensions:any, responsePackagePdfStitchStatus:any, cfrFeeData:any, templateInfo: any, callback: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let pbExtension =  getExtensiondetails(requestExtensions, "Public Body");

  // Find the record that matches the criteria for already taken a time extension under section 10(1), excluding the most recent record
  const filteredOutLatestExtensions = findLatestMatchingTimeExtension(requestExtensions, reasonsToCheck);

  const checkFinalPackage = checkRecordReleased(responsePackagePdfStitchStatus)

  const [feeEstimateStatus, feeEstimateDate] = getFeeEstimateInfo(cfrFeeData);
  // const fullFeePaidDate = getFullFeePaidDate(cfrFeeData);

  // const feeWaiverDecisionDate = getFeeWaiverDecisionDate(cfrFeeData);
  
  // const redatedTotalPage = fetchDocumentPage(requestDetails.id, (_err : any, res : any) => {
  //   if (!_err) {
  //     console.log("********************* fetchRedactedPageFlags : ")
  //     console.log(res)
  //     // volume of records - total pagecount
  //     const totalPageCount = res.data.reduce((sum : any, item : any) => sum + (item.pagecount || 0), 0);
  //     console.log("Total Page Count:", totalPageCount);
      
  //     return totalPageCount || null;
  //   } else {
  //     console.log("********************* error: ", _err)
  //   }
  // })


  //test((dispatch: any) => {})   // nice shot

  callback([
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
    {name: "{{oipcExtensionDueDates}}", value:  convertDate(oipcExtension[1])}, 
    {name: "{{oipcExtensionReason}}", value: oipcExtension[2]}, 
    {name: "{{oipcExtensionNotiDate}}", value: oipcExtension[5]},
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
    {name: "{{oipcExtensionSection}}", value: await displayOIPCExtensionSection(oipcExtension[4], requestDetails)},
    {name: "{{oipcExtensionList}}", value: displayOIPCExtension(requestExtensions)},
  ]);
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
// Function to map extension reason id to its textual representation
// const mapSectionWithExtensionReasonId = (extensionReasonId: number) => {
//   switch (extensionReasonId) {
//       case 6:
//           return "10(1)(d)"; // 10(1)(d) = Applicant Consent
//       case 7:
//           return "10(1)(c)"; // 10(1)(c) = Consultation
//       case 8:
//           return "10(1)(a)"; // 10(1)(a) = Further detail from applicant required
//       case 9:
//           return "10(1)(b)"; // 10(1)(b) = Large Volume and/or Volume of Search
//       default:
//           return "";
//   }
// };

// Function to map extension reason id to its textual representation (PB and OIPC combined)
const mapSectionWithExtensionReasonId = (extensionReasonId: number) => {
  console.log("extensionReasonId : ",extensionReasonId)
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
    console.log("Fee dateSent: "+dateSent, "/ Fee datePaid:",datePaid," / Fee dateWaiverDecision:",dateWaiverDecision)

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
  console.log("requestExtensions!!!!!!!!! : ",requestExtensions)
  if (requestExtensions && requestExtensions.length > 0) {
    // Filter out only Public Body extensions that are approved
    const pbExtensions = requestExtensions.filter((ext: any) => 
      ext.extensiontype === "Public Body" && ext.extensionstatus === "Approved"
    );

    // Check if there are any PB Extensions
    if (pbExtensions.length > 0) {
      const recentPBExtension = pbExtensions[0]; // Assuming the list is sorted by date with the most recent first
      console.log("Most recent PB Extension:", recentPBExtension);
      
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
      console.log("displayOIPCExtension : ",reasonsString)
      return reasonsString;
    }
  }
  // If no OIPC Extension is found, return an empty string
  return ''
};


const fetchTotalPageCount = (ministryId : number) => {
  const dispatch = () => {};

  return new Promise((resolve, reject) => {
    fetchDocumentPage(ministryId, (err : any, res : any) => {
      if (!err) {
        console.log("********************* fetchRedactedPageFlags : ");
        console.log(res);
        
        // Sum the page counts
        const totalPageCount = res.data.reduce((sum : any, item : any) => sum + (item.pagecount || 0), 0);
        console.log("Total Page Count:", totalPageCount);
        
        resolve(totalPageCount || null);

        console.log("Resolved ")
      } else {
        console.log("********************* error: ", err);
        reject(err);
      }
    })(dispatch);
  });
};


// const fetchConsultPageFlag = (ministryId: number): Promise<string> => {
//   return new Promise((resolve, reject) => {
//     fetchDocumentPageFlags(ministryId, (err: any, res: any) => {
//       if (!err) {
//         console.log("********************* fetchRedactedPageFlags : ");
//         console.log(res.data);

//         // Generate JSX string from the result
//         const jsxString = res.data.map((item: any) => `
//             <p>strong><span style="font-size: 13px;">Consultee: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_name}</span></p>
//             <p><strong><span style="font-size: 13px;">Consultation page count: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_page_count}</span></p>
//             <p><strong><span style="font-size: 13px;">Consultation Date: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_date}</span></p>
//         `).join('');
//         console.log("헤헤: ",jsxString)

//         resolve(jsxString);
//       } else {
//         console.log("********************* error: ", err);
//         reject(err);
//       }
//     });
//   });
// };
const fetchConsultPageFlag =  (ministryId: number)=> {
  const dispatch = () => {};
  try {
    // const res = new Promise<any>((resolve, reject) => {
    //   fetchDocumentPageFlags(ministryId, (err: any, res: any) => {
    //     if (!err) {
    //       resolve(res);
    //     } else {
    //       reject(err);
    //     }
    //   })(() => {});
    // });

    // console.log("********************* fetchRedactedPageFlags : ");
    // console.log(res.data);

    return new Promise((resolve, reject) => {
      fetchDocumentPageFlags(ministryId, (err : any, res : any) => {
        if (!err) {
          console.log("********************* fetchRedactedPageFlags : ");
          console.log(res);
          
          const jsxString = res.data.map((item: any) => `
      <p><strong><span style="font-size: 13px;">Consultee: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_name}</span></p>
      <p><strong><span style="font-size: 13px;">Consultation page count: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_page_count}</span></p>
      <p><strong><span style="font-size: 13px;">Consultation Date: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_date}</span></p>
    `).join('');
    console.log("헤헤: ", jsxString);



          resolve(jsxString || null);
        } else {
          console.log("********************* error: ", err);
          reject(err);
        }
      })(dispatch);
    });

    // Generate JSX string from the result
    // const jsxString = res.data.map((item: any) => `
    //   <p><strong><span style="font-size: 13px;">Consultee: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_name}</span></p>
    //   <p><strong><span style="font-size: 13px;">Consultation page count: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_page_count}</span></p>
    //   <p><strong><span style="font-size: 13px;">Consultation Date: &nbsp;</span></strong><span style="font-size: 13px;">${item.consultation_date}</span></p>
    // `).join('');
    // console.log("헤헤: ", jsxString);

    // return jsxString;
  } catch (err:any) {
    console.log("********************* error: ", err);
    throw new Error(err.message || "Error fetching consultation page flag.");
  }
};


const displayOIPCExtensionSection = async (extensionId: number, requestDetails: any) => {
  switch (mapSectionWithExtensionReasonId(extensionId)) {
    case "10(1)(a)":
      return `
<p><strong><span style="font-size: 13px;">10(1)(a) Insufficient detail</span></strong></p>
<p><span style="font-size: 13px;">A copy of the original request is included. It does not provide sufficient detail to proceed with the request. <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> Satisfactory clarification from the applicant was not obtained within 60 business days (or 30 business days if the public body’s time extension was not taken): &nbsp;<strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> </span></p>
`;
    case "10(1)(b)":

    //  const getTotalPageCount = async (ministryId: number) => {
    //    try {
    // console.log("여기 안들어오나? requestDetails.id:", requestDetails.id)    
    // const totalPageCount = await fetchTotalPageCount(requestDetails.id);

    //      return totalPageCount
    //      // Do something with totalPageCount
    //    } catch (error) {
    //      console.error("Error:", error);
    //    }
    //  };

    let totalPageCount = await fetchTotalPageCount(requestDetails.id);

    // fetchTotalPageCount(requestDetails.id).then((count: any) => {
    //   console.log("count: ",count)
    //   if(count!=null){
    //     totalPageCount = count;
    //   }
    // });
    // console.log("헬로")
    // try {
    //   totalPageCount = await fetchTotalPageCount(requestDetails.id);console.log("그래!!!!!!!! > ",totalPageCount)
    // } catch (error) {
    //     console.error("Error fetching total page count:", error);
    // }
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
    console.log("여기는 consult!!!!!")
    //const consultPageFlag = await fetchConsultPageFlag(requestDetails.id);
    // const getConsultPageFlag = async (ministryId: number): Promise<string> => {
    //   try {
        const consultPageFlag = fetchConsultPageFlag(requestDetails.id);
    //     return consultPageFlag;
    //   } catch (error:any) {
    //     console.error("Error:", error.message);
    //     return "Error fetching consultation page flag.";
    //   }
    // };
      return `
<p><strong><span style="font-size: 13px;">10(1)(c) Time for consultation</span></strong></p>
<p style="text-align: center;"><span style="font-size: 13px; ">&nbsp;</span></p>
${consultPageFlag}
 <p><strong><span style="font-size: 13px;">Why is consultation necessary to decide access?</span></strong></p>
 <p>
    <span>
    <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
    </span>
 </p>
 <p><strong><span style="font-size: 13px;">What is the third party or public body’s interest in the record?</span></strong></p>
 <p>
    <span>
    <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
    </span>
 </p>
 <p><strong><span style="font-size: 13px;">Current status of the consultation, including efforts made to obtain a response to the consultation and expected return date:</span></strong></p>
 <p>
    <span>
    <strong>&lt;insert some indication the analyst needs to populate this area&gt;</strong> 
    </span>
 </p>
 <p><span style="font-size: 13px;">10(2)(b)</span></p>
 <p><strong><span style="font-size: 13px;">Explain why it would be fair and reasonable for the Commissioner to grant a time extension. Include a chronology of the processing of the request and an explanation for any delays: </span></strong></p>
 <p><strong><span style="font-size: 13px;">&lt;insert some indication the analyst needs to populate this area&gt;</span></strong></p>
`;

    default:
      return "";
  }
};
