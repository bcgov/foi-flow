export const getCorrespondenceSubject = (correspondence, templateList, requestNumber) => {
    if (correspondence?.subject) return correspondence.subject
    if (!correspondence?.sentby && correspondence?.templatename) return templateList.find((obj)=> obj.fileName == correspondence.templatename)?.templateName
    if (correspondence.category === "response") return correspondence.correspondencesubject?.trim() ? correspondence.correspondencesubject : "Applicant Response";
    if ((correspondence?.sentby == "System Generated Email" || correspondence?.sentby == "system") && 
      (correspondence?.text.includes("as you have additional options outside of paying the fee") || 
      correspondence?.text.includes("has received your payment for FOI request"))) return "Fee Estimate / Outstanding Fee"
    return `Your FOI Request ${requestNumber}`
  }

export const getFullEmailListText = (correspondence) => {
    let fullEmailListText = correspondence?.emails?.length > 0 ? 'Email To: ' : '';
    correspondence?.emails.forEach((email, index) => {
      fullEmailListText = fullEmailListText + email
      if (index < correspondence.emails.length - 1) fullEmailListText = fullEmailListText + ', '
    })
    return fullEmailListText;
}

export const getFullCCEmailListText = (correspondence) => {
    let fullCCEmailListText = correspondence?.ccemails?.length > 0 ? 'CC To: ' : '';
    correspondence?.ccemails.forEach((email, index) => {
      fullCCEmailListText = fullCCEmailListText + email
      if (index < correspondence.ccemails.length - 1) fullCCEmailListText = fullCCEmailListText + ', '
    })
    return fullCCEmailListText;
}

export const convertDateStringToNumeric = (input) => {
  const [datePart, timePart] = input.split(" | ");
  const dateStr = `${datePart} ${timePart}`;
  const parsedDate = new Date(dateStr);
  const year = parsedDate.getFullYear();
  const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
  const day = String(parsedDate.getDate()).padStart(2, '0');
  return `${year}-${month}-${day} ${timePart}`
}