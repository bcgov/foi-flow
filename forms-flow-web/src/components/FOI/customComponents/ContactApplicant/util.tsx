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
        return [recentExtension["approvednoofdays"], recentExtension["extendedduedate"], recentExtension["extensionreson"]]
      }
    }    
    return ["","",""]
}

export const getTemplateVariables = (requestDetails: any, requestExtensions:any, templateInfo: any) => {
  let oipcExtension = getExtensiondetails(requestExtensions, "OIPC");
  let pbExtension =  getExtensiondetails(requestExtensions, "Public Body");
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
    {name: "{{pbExtensionReason}}", value: pbExtension[2]}, 
    {name: "{{pbExtensionBody}}", value: "public body"}, 
  ];
  
}

export const isTemplateDisabled = (currentCFRForm: any, template: any) => {
  if (template.name === 'PAYONLINE') {
    return currentCFRForm.status !== 'approved' || ("estimatepaymentmethod" in currentCFRForm.feedata && currentCFRForm.feedata.actualtotaldue > 0)
  } else if (template.name === 'PAYOUTSTANDING') {
    return currentCFRForm.status !== 'approved' || !("estimatepaymentmethod" in currentCFRForm.feedata) || currentCFRForm.feedata.balanceremaining <= 0 || currentCFRForm.feedata.actualtotaldue <= 0
  }
  return false
}
