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

export const getTemplateVariables = (requestDetails: any, templateInfo: any) => {
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
